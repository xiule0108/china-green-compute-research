#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Parameter data are separately licensed; see LICENSES/LICENSE-SCOPE.md.
"""
《中国绿色算力全球化交付体系与国际价值重构》
报告版本分析模型。公开资料、情景假设和方法适用边界见 data/metadata/ 与 docs/。

1. DuckDB 注册发布目录中的 59 张加工表，Pandera 检查 WTO 选定字段并计算 O01；
2. 跨政策隐含物理恒等式反解（M01B，采用 IEA 2024 68 TWh、2025 80 TWh、2030 205 TWh 与 2025 基期方案 B）；
3. Kaya-LMDI 五因子电量与碳排放恒等分解（M02B，基期对齐 2024 IT 68 TWh 与 2023 全国平均因子 0.5306 kgCO2/kWh）；
4. SciPy.optimize.brentq 跨洋交付三维临界值区间求根（M03B）；
5. CVXPY（SCS 求解器）带二次正则的跨洋算电联合调度情景优化（M04B）；
6. SALib Sobol 全局方差敏感性分解（M05B，2048×(2×6+2)=28,672 次函数评估，固定 seed=20261018）；
7. NumPy 30 省电力碳因子未加权 Gini/Theil 分解（M06B）与 Statsmodels 25 条手工 GPU 样本线性/半对数普通 OLS 回归（M06C）；
8. NetworkX 两张设定拓扑的加权介数中心性、容量特征向量中心性与最短路对比（M07B）；
9. 2030 年三种发展情景 10,000 次独立三角分布蒙特卡洛模拟（M06MC，读取外置参数文件 monte_carlo_2030_scenarios.json，固定 seed=20261015）。
"""

from release_io import get_input, DATA_ROOT, OUTPUT_ROOT, table_path
import json
import math
from pathlib import Path

import cvxpy as cp
import duckdb
import networkx as nx
import numpy as np
import pandas as pd
import pandera as pa
from SALib.analyze import sobol as sobol_analyze
from SALib.sample import sobol as sobol_sample
from scipy import optimize
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = DATA_ROOT
REPORT_DIR = OUTPUT_ROOT
OUT_DIR = OUTPUT_ROOT / "models"
TOPIC_DIR = OUTPUT_ROOT / "models"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 1. CSV注册和WTO选定字段检查 (DuckDB + Pandera)
# ==============================================================================
def run_ontology_data_governance():
    con = duckdb.connect(":memory:")
    catalog_csv = DATA_ROOT / "metadata/data_catalog.csv"
    df_cat = pd.read_csv(catalog_csv)
    df_cat = df_cat[df_cat["table_id"].str.startswith("TBL-")]

    registered_tables = []
    for _, row in df_cat.iterrows():
        tid = str(row["table_id"]).strip()
        rel_path = str(row["path"]).strip()
        full_path = ROOT / rel_path
        if not full_path.is_file() or full_path.suffix.lower() != ".csv":
            raise FileNotFoundError(f"Missing CSV for {tid}: {full_path}")
        if full_path.is_file():
            view_name = tid.replace("-", "_")
            try:
                csv_path_sql = full_path.as_posix().replace("'", "''")
                con.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_csv_auto('{csv_path_sql}', header=true, ignore_errors=false)")
                cnt = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]
                registered_tables.append(
                    {
                        "table_id": tid,
                        "view_name": view_name,
                        "chapter": str(row.get("chapter", "")),
                        "title": str(row["title"]),
                        "rows_verified": int(cnt),
                        "path": rel_path,
                    }
                )
            except Exception as e:
                raise RuntimeError(f"Failed to register {tid}: {e}") from e

    # 1.1 Pandera Schema Contract on WTO Selected Markets (TBL_001)
    df_wto = con.execute("SELECT * FROM TBL_001").df()
    wto_schema = pa.DataFrameSchema(
        {
            "YEAR": pa.Column(int, pa.Check.between(2019, 2025)),
            "INDICATOR": pa.Column(str, pa.Check.isin(["DDS", "SI2"])),
            "FLOW": pa.Column(str, pa.Check.isin(["X", "M"])),
            "VALUE": pa.Column(float, pa.Check.ge(0.0), nullable=True),
        },
        coerce=True,
    )
    wto_schema.validate(df_wto)

    # Compute WTO 2019-2025 CAGR, SI2/DDS Share, and Global Incremental Contribution
    wto_piv = df_wto.pivot_table(
        index=["REPORTER_NAME", "REPORTER_CODE"],
        columns=["INDICATOR", "FLOW", "YEAR"],
        values="VALUE",
        aggfunc="first",
    )
    world_row = wto_piv.xs("World", level="REPORTER_NAME").iloc[0]
    world_dds_x_2019 = float(world_row.get(("DDS", "X", 2019)))
    world_dds_x_2025 = float(world_row.get(("DDS", "X", 2025)))
    world_si2_x_2019 = float(world_row.get(("SI2", "X", 2019)))
    world_si2_x_2025 = float(world_row.get(("SI2", "X", 2025)))
    world_si2_delta = world_si2_x_2025 - world_si2_x_2019

    wto_derived_rows = []
    for (name, code), r in wto_piv.iterrows():
        dds_x19 = float(r.get(("DDS", "X", 2019), np.nan))
        dds_x25 = float(r.get(("DDS", "X", 2025), np.nan))
        si2_x19 = float(r.get(("SI2", "X", 2019), np.nan))
        si2_x25 = float(r.get(("SI2", "X", 2025), np.nan))
        si2_m25 = float(r.get(("SI2", "M", 2025), np.nan))
        dds_cagr = ((dds_x25 / dds_x19) ** (1 / 6) - 1) * 100 if dds_x19 > 0 else np.nan
        si2_cagr = ((si2_x25 / si2_x19) ** (1 / 6) - 1) * 100 if si2_x19 > 0 else np.nan
        si2_share_25 = (si2_x25 / dds_x25) * 100 if dds_x25 > 0 else np.nan
        rca_si2 = (si2_share_25 / ((world_si2_x_2025 / world_dds_x_2025) * 100)) if dds_x25 > 0 else np.nan
        contrib_global_si2 = ((si2_x25 - si2_x19) / world_si2_delta) * 100 if world_si2_delta > 0 else np.nan
        # LMDI decomposition of SI2 export growth (2019 -> 2025) for each economy
        if si2_x19 > 0 and si2_x25 > 0 and name != "World":
            L_si2 = (si2_x25 - si2_x19) / (math.log(si2_x25) - math.log(si2_x19))
            eff_global_scale = L_si2 * math.log(world_dds_x_2025 / world_dds_x_2019)
            eff_country_share = L_si2 * math.log((dds_x25 / world_dds_x_2025) / (dds_x19 / world_dds_x_2019))
            eff_si2_struct = L_si2 * math.log((si2_x25 / dds_x25) / (si2_x19 / dds_x19))
        else:
            eff_global_scale = eff_country_share = eff_si2_struct = np.nan

        wto_derived_rows.append(
            {
                "reporter_code": code,
                "reporter_name": name,
                "dds_export_2019_musd": round(dds_x19, 1),
                "dds_export_2025_musd": round(dds_x25, 1),
                "dds_export_cagr_pct": round(dds_cagr, 2),
                "si2_export_2019_musd": round(si2_x19, 1),
                "si2_export_2025_musd": round(si2_x25, 1),
                "si2_import_2025_musd": round(si2_m25, 1),
                "si2_net_balance_2025_musd": round(si2_x25 - si2_m25, 1),
                "si2_export_cagr_pct": round(si2_cagr, 2),
                "si2_share_in_dds_2025_pct": round(si2_share_25, 2),
                "si2_revealed_comparative_advantage_rca": round(rca_si2, 2),
                "global_si2_incremental_contribution_pct": round(contrib_global_si2, 2),
                "lmdi_scale_effect_musd": round(eff_global_scale, 1) if not np.isnan(eff_global_scale) else None,
                "lmdi_share_effect_musd": round(eff_country_share, 1) if not np.isnan(eff_country_share) else None,
                "lmdi_struct_effect_musd": round(eff_si2_struct, 1) if not np.isnan(eff_si2_struct) else None,
            }
        )
    df_wto_derived = pd.DataFrame(wto_derived_rows)
    df_wto_derived.to_csv(OUT_DIR / "O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv", index=False)

    df_iea_reg = con.execute("SELECT * FROM TBL_062").df()
    df_iea_scen = con.execute("SELECT * FROM TBL_063").df()

    return con, registered_tables, df_wto_derived, df_iea_reg, df_iea_scen


# ==============================================================================
# 2. 模型一：跨政策/跨规划隐含物理恒等式反解 (Cross-Policy Implied Identity Inversion)
# ==============================================================================
def run_model1_policy_identity_inversion():
    """
    联立：
    1) IEA 2026 中国数据中心用电序列（Table A.3 & Table A.4）：
       - 2024年：总设施用电 E_tot_2024 = 102.0 TWh, IT用电 E_IT_2024 = 68.0 TWh (隐含 PUE_2024 = 1.5000，Table A.3 官方值 1.50)；
       - 2025年：总设施用电 E_tot_2025 = 117.0 TWh, IT用电 E_IT_2025 = 80.0 TWh (隐含 PUE_2025 = 1.4625，Table A.3 官方值 1.47)；
       - 2030年基准预测：总设施用电 E_tot_2030 = 277.0 TWh, IT用电 E_IT_2030 = 205.0 TWh (隐含 PUE_2030 = 1.3512，Table A.3 官方值 1.35)。
    2) 发改环资〔2024〕970号 & 2026国家绿色算力设施评价标准：新建大型/超大型集群 PUE <= 1.25（国家枢纽节点 <= 1.20），
       机架利用率 >= 60%，枢纽新增绿电占比 >= 80%。
    3) “十五五”（2026-2030）政策情景（以 2025 年为基期，方案 B）：
       - 2025 年存量 IT 负荷 80.0 TWh 通过余热回收与液冷改造将 PUE 由 1.4625（耗电 117.0 TWh）压降至 1.35（耗电 108.0 TWh），存量技改年节电 9.00 TWh；
       - 2025-2030 年新增 IT 负荷 125.0 TWh 执行新建液冷政策加权 PUE_new = 1.22（耗电 152.50 TWh，较 2030 基准隐含增量耗电 160.0 TWh 节电 7.50 TWh）；
       - 2030 年政策情景下总用电压降至 260.50 TWh，每年累计从非 IT 冷却散热损耗中释放 16.50 TWh 总电量（折合新建集群 PUE=1.22 下净有效 IT 电量 13.52 TWh）。
    """
    E_tot_24, E_it_24 = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'E_tot_24__E_it_24')
    E_tot_25, E_it_25 = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'E_tot_25__E_it_25')
    E_tot_30, E_it_30 = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'E_tot_30__E_it_30')

    pue_24 = E_tot_24 / E_it_24  # 1.5000 (IEA Table A.3 official = 1.50)
    pue_25 = E_tot_25 / E_it_25  # 1.4625 (IEA Table A.3 official = 1.47)
    pue_30 = E_tot_30 / E_it_30  # 1.3512 (IEA Table A.3 official = 1.35)

    delta_E_it_24_30 = E_it_30 - E_it_24  # 137.0 TWh
    delta_E_it_25_30 = E_it_30 - E_it_25  # 125.0 TWh

    pue_new_policy = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'pue_new_policy')
    pue_legacy_target = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'pue_legacy_target')
    pue_new_required_no_retrofit_25 = (E_tot_30 - E_tot_25) / delta_E_it_25_30  # 160 / 125 = 1.2800
    pue_new_required_no_retrofit_24 = (E_tot_30 - E_tot_24) / delta_E_it_24_30  # 175 / 137 = 1.2774

    E_legacy_25_after_retrofit = E_it_25 * pue_legacy_target  # 80 * 1.35 = 108.00 TWh
    legacy_retrofit_saved_twh = E_tot_25 - E_legacy_25_after_retrofit  # 117 - 108 = 9.00 TWh/yr
    E_new_25_30_under_policy = delta_E_it_25_30 * pue_new_policy  # 125 * 1.22 = 152.50 TWh
    cooling_power_saved_twh = (E_tot_30 - E_tot_25) - E_new_25_30_under_policy  # 160 - 152.50 = 7.50 TWh/yr
    E_tot_30_under_policy = E_legacy_25_after_retrofit + E_new_25_30_under_policy  # 260.50 TWh/yr
    total_non_it_squeezed_twh = E_tot_30 - E_tot_30_under_policy  # 16.50 TWh/yr
    reclaimed_net_it_twh = total_non_it_squeezed_twh / pue_new_policy  # 13.5246 TWh/yr

    # Equivalent extra 8-GPU H200/B200 servers (10.2 kW IT power, accounting for facility PUE = 1.22):
    extra_gpu_nodes_75pct_with_pue = (total_non_it_squeezed_twh * 1e9) / (10.2 * 8760 * 0.75 * pue_new_policy)  # 201,817 nodes
    extra_gpu_nodes_100pct_with_pue = (total_non_it_squeezed_twh * 1e9) / (10.2 * 8760 * 1.00 * pue_new_policy)  # 151,363 nodes

    reclaimed_tokens_petatokens_mid = reclaimed_net_it_twh * 1.85   # 25.02 PetaTokens (千万亿 Tokens)
    reclaimed_tokens_petatokens_low = reclaimed_net_it_twh * 1.45   # 19.61 PetaTokens
    reclaimed_tokens_petatokens_high = reclaimed_net_it_twh * 2.25  # 30.43 PetaTokens

    western_surplus_twh = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'western_surplus_twh')
    aidc_allocable_twh = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'aidc_allocable_twh')
    it_allocable_twh = aidc_allocable_twh / 1.20  # 98.75 TWh IT electricity = 9.875e10 kWh
    kwh_per_1m_tokens = get_input('analytics_inputs.json', 'run_model1_policy_identity_inversion', 'kwh_per_1m_tokens')
    max_qualified_tokens_petatokens = it_allocable_twh / kwh_per_1m_tokens  # 318.55 PetaTokens (10^15)
    max_qualified_tokens_trillion = max_qualified_tokens_petatokens * 1000.0  # 318,548.39 Trillion Tokens (10^12)
    implied_export_value_busd = max_qualified_tokens_petatokens * 0.20

    res = {
        "pue_2024_implied": round(pue_24, 4),
        "pue_2025_implied": round(pue_25, 4),
        "pue_2030_implied": round(pue_30, 4),
        "delta_it_electricity_2024_2030_twh": round(delta_E_it_24_30, 2),
        "delta_it_electricity_2025_2030_twh": round(delta_E_it_25_30, 2),
        "pue_new_required_without_legacy_retrofit_2025base": round(pue_new_required_no_retrofit_25, 4),
        "pue_new_required_without_legacy_retrofit_2024base": round(pue_new_required_no_retrofit_24, 4),
        "total_electricity_2030_under_policy_twh": round(E_tot_30_under_policy, 2),
        "cooling_saved_under_pue122_twh": round(cooling_power_saved_twh, 2),
        "legacy_retrofit_saved_twh": round(legacy_retrofit_saved_twh, 2),
        "total_non_it_waste_reclaimable_twh": round(total_non_it_squeezed_twh, 2),
        "reclaimed_net_it_electricity_twh": round(reclaimed_net_it_twh, 2),
        "equivalent_8gpu_nodes_reclaimed": int(round(extra_gpu_nodes_75pct_with_pue)),
        "equivalent_8gpu_nodes_reclaimed_100pct_load": int(round(extra_gpu_nodes_100pct_with_pue)),
        "reclaimed_tokens_petatokens_mid": round(reclaimed_tokens_petatokens_mid, 2),
        "reclaimed_tokens_petatokens_low": round(reclaimed_tokens_petatokens_low, 2),
        "reclaimed_tokens_petatokens_high": round(reclaimed_tokens_petatokens_high, 2),
        "western_5prov_surplus_twh": western_surplus_twh,
        "aidc_green_power_budget_twh": aidc_allocable_twh,
        "max_qualified_tokens_petatokens_per_yr": round(max_qualified_tokens_petatokens, 2),
        "max_qualified_tokens_trillion_per_yr": round(max_qualified_tokens_trillion, 2),
        "implied_token_export_som_ceiling_busd": round(implied_export_value_busd, 2),
    }
    pd.DataFrame([res]).to_csv(OUT_DIR / "M01B_跨政策隐含物理恒等式反解表.csv", index=False)
    return res


# ==============================================================================
# 3. 模型二：Kaya-LMDI 对数平均迪氏指数完全无残差分解 (Mathematical Identity)
# ==============================================================================
def run_model2_kaya_lmdi_decomposition():
    """
    将 2024 -> 2030 年中国数据中心用电量与碳排放增长执行五因子 Kaya-LMDI 恒等分解（宏观脱碳核算模型 M02B）：
    注：报告图表 11.9/11.10 采用 M04 推理专项电量四因子分解（Q1/Q0=6.80, S1/S0=1.85, PUE0=1.50->1.3512，四因子为 +335.8/+107.8/-250.3/-18.3 TWh）；
        本表 M02B 为叠加第五因子（电网电源脱碳因子 Δdecarb）的宏观碳排放五因子分解模型，基期统一校准为 IEA 2026 中国 2024 年 IT 电量 68.0 TWh（PUE0=1.5000）
        及生态环境部《2023年电力二氧化碳排放因子》全国平均直接排放因子 0.5306 kgCO2/kWh。
    """
    E0, E1 = get_input('analytics_inputs.json', 'run_model2_kaya_lmdi_decomposition', 'E0__E1')
    E_it0, E_it1 = get_input('analytics_inputs.json', 'run_model2_kaya_lmdi_decomposition', 'E_it0__E_it1')
    dE = E1 - E0  # +175.0 TWh
    L_E = (E1 - E0) / (math.log(E1) - math.log(E0))

    Q0, Q1 = get_input('analytics_inputs.json', 'run_model2_kaya_lmdi_decomposition', 'Q0__Q1')
    S0, S1 = get_input('analytics_inputs.json', 'run_model2_kaya_lmdi_decomposition', 'S0__S1')
    PUE0, PUE1 = get_input('analytics_inputs.json', 'run_model2_kaya_lmdi_decomposition', 'PUE0__PUE1')
    eit0 = E_it0 / (Q0 * S0)
    eit1 = E_it1 / (Q1 * S1)

    dE_scale = L_E * math.log(Q1 / Q0)
    dE_struct = L_E * math.log(S1 / S0)
    dE_eff = L_E * math.log(eit1 / eit0)
    dE_pue = L_E * math.log(PUE1 / PUE0)
    residual_E = dE - (dE_scale + dE_struct + dE_eff + dE_pue)
    assert abs(residual_E) < 1e-9, f"LMDI residual non-zero: {residual_E}"

    # Carbon Emission Kaya-LMDI (Unit: Million Tonnes CO2, MtCO2)
    ef0, ef1 = get_input('analytics_inputs.json', 'run_model2_kaya_lmdi_decomposition', 'ef0__ef1')
    C0 = E0 * ef0  # 54.1212 MtCO2
    C1 = E1 * ef1  # 68.6960 MtCO2
    dC = C1 - C0   # +14.5748 MtCO2
    L_C = (C1 - C0) / (math.log(C1) - math.log(C0))

    dC_scale = L_C * math.log(Q1 / Q0)
    dC_struct = L_C * math.log(S1 / S0)
    dC_eff = L_C * math.log(eit1 / eit0)
    dC_pue = L_C * math.log(PUE1 / PUE0)
    dC_decarb = L_C * math.log(ef1 / ef0)
    residual_C = dC - (dC_scale + dC_struct + dC_eff + dC_pue + dC_decarb)
    assert abs(residual_C) < 1e-9

    rows = [
        {
            "factor": "算力需求规模扩张效应 (Δscale)",
            "param_2024": f"Q0 = {Q0:.1f}",
            "param_2030": f"Q1 = {Q1:.1f} (11.20x)",
            "delta_electricity_twh": round(dE_scale, 2),
            "share_of_electricity_growth_pct": round(dE_scale / dE * 100, 2),
            "delta_carbon_mtco2": round(dC_scale, 2),
            "share_of_carbon_change_pct": round(dC_scale / dC * 100, 2),
        },
        {
            "factor": "生成式推理与长思考结构升级效应 (Δstruct)",
            "param_2024": f"S0 = {S0:.2f}",
            "param_2030": f"S1 = {S1:.2f} (+34.0%)",
            "delta_electricity_twh": round(dE_struct, 2),
            "share_of_electricity_growth_pct": round(dE_struct / dE * 100, 2),
            "delta_carbon_mtco2": round(dC_struct, 2),
            "share_of_carbon_change_pct": round(dC_struct / dC * 100, 2),
        },
        {
            "factor": "软硬协同算法与芯片能效跃迁效应 (Δeff)",
            "param_2024": f"e0 = {eit0:.4f}",
            "param_2030": f"e1 = {eit1:.4f} (-79.91%)",
            "delta_electricity_twh": round(dE_eff, 2),
            "share_of_electricity_growth_pct": round(dE_eff / dE * 100, 2),
            "delta_carbon_mtco2": round(dC_eff, 2),
            "share_of_carbon_change_pct": round(dC_eff / dC * 100, 2),
        },
        {
            "factor": "液冷普及与余热回收PUE压降效应 (Δpue)",
            "param_2024": f"PUE0 = {PUE0:.4f}",
            "param_2030": f"PUE1 = {PUE1:.4f} (-9.92%)",
            "delta_electricity_twh": round(dE_pue, 2),
            "share_of_electricity_growth_pct": round(dE_pue / dE * 100, 2),
            "delta_carbon_mtco2": round(dC_pue, 2),
            "share_of_carbon_change_pct": round(dC_pue / dC * 100, 2),
        },
        {
            "factor": "绿电直连与算电协同电源脱碳效应 (Δdecarb)",
            "param_2024": f"EF0 = {ef0:.4f} kg/kWh",
            "param_2030": f"EF1 = {ef1:.4f} kg/kWh (-53.26%)",
            "delta_electricity_twh": 0.00,
            "share_of_electricity_growth_pct": 0.00,
            "delta_carbon_mtco2": round(dC_decarb, 2),
            "share_of_carbon_change_pct": round(dC_decarb / dC * 100, 2),
        },
        {
            "factor": "总计净变动 (Total Net Change，残差=0)",
            "param_2024": f"E0={E0:.0f}TWh / C0={C0:.2f}Mt",
            "param_2030": f"E1={E1:.0f}TWh / C1={C1:.2f}Mt",
            "delta_electricity_twh": round(dE, 2),
            "share_of_electricity_growth_pct": 100.00,
            "delta_carbon_mtco2": round(dC, 2),
            "share_of_carbon_change_pct": 100.00,
        },
    ]
    df_lmdi = pd.DataFrame(rows)
    df_lmdi.to_csv(OUT_DIR / "M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv", index=False)
    return df_lmdi


# ==============================================================================
# 4. 模型三：SciPy.optimize.brentq 跨洋交付多维盈亏平衡临界值反解 (u*, p_e*, p_net*, k*)
# ==============================================================================
def run_model3_scipy_brentq_breakeven():
    """
    使用 scipy.optimize.brentq 对《M02_24加6情景交付成本与临界利用率矩阵.csv》中的 24 组境内跨境交付路径
    反解：
    1) 盈亏平衡计费利用率 u* (使中国节点跨洋 LCoT == 海外本地基准 LCoT)
    2) 临界最高可承受电价 p_e* (元/kWh，在 ref_u 基准利用率下使 LCoT_CN == LCoT_Overseas)
    3) 临界跨境网络带宽成本倍率 M_net* (使 LCoT_CN == LCoT_Overseas)
    """
    df_m02 = pd.read_csv(TOPIC_DIR / "M02_24加6情景交付成本与临界利用率矩阵.csv")
    ov_rows = df_m02[df_m02["scenario_type"] == "海外本地对照"].copy()
    cn_rows = df_m02[df_m02["scenario_type"] == "境内跨境交付"].copy()

    bench_map = {}
    for _, r in ov_rows.iterrows():
        bench_map[(r["market_name"], r["task_name"])] = float(r["total_cost_usd_1m"])

    pe_node_map = get_input('analytics_inputs.json', 'run_model3_scipy_brentq_breakeven', 'pe_node_map')

    brentq_results = []
    for idx, r in cn_rows.iterrows():
        s_node = r["node_name"]
        t_mkt = r["market_name"]
        w_task = r["task_name"]
        u0 = float(str(r["ref_u"]).replace("%", "")) / 100.0
        pe0 = pe_node_map.get(s_node, 0.35)
        hw0 = float(r["capex_usd_1m"])
        pwr0 = float(r["elec_total_usd_1m"])
        net0 = float(r["net_var_usd_1m"])
        comp0 = float(r["comp_var_usd_1m"])
        target_lcot = bench_map[(t_mkt, w_task)]

        def lcot_fn(u, pe, net_mult=1.0):
            hw_u = hw0 * (u0 / u)
            pwr_u = pwr0 * (pe / pe0) * (0.30 * (u0 / u) + 0.70)
            net_u = net0 * net_mult
            return hw_u + pwr_u + net_u + comp0

        u_star = optimize.brentq(lambda u: lcot_fn(u, pe0, 1.0) - target_lcot, 0.05, 0.99)
        try:
            pe_star = optimize.brentq(lambda pe: lcot_fn(u0, pe, 1.0) - target_lcot, 0.01, 8.00)
        except ValueError:
            pe_star = 0.01
        try:
            net_mult_star = optimize.brentq(lambda nm: lcot_fn(u0, pe0, nm) - target_lcot, 0.01, 40.0)
        except ValueError:
            net_mult_star = 0.0

        brentq_results.append(
            {
                "node_name": s_node,
                "market_name": t_mkt,
                "task_name": w_task,
                "ref_u_pct": round(u0 * 100, 1),
                "baseline_pe_cny_kwh": pe0,
                "baseline_lcot_usd_1m": round(float(r["total_cost_usd_1m"]), 4),
                "overseas_benchmark_usd_1m": round(target_lcot, 4),
                "brentq_breakeven_u_star_pct": round(u_star * 100, 2),
                "brentq_critical_pe_star_cny_kwh": round(pe_star, 3),
                "brentq_critical_net_multiplier_star": round(net_mult_star, 2),
                "electricity_headroom_cny_kwh": round(pe_star - pe0, 3),
            }
        )
    df_brentq = pd.DataFrame(brentq_results)
    df_brentq.to_csv(OUT_DIR / "M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv", index=False)
    return df_brentq


# ==============================================================================
# 5. 模型四：CVXPY 跨洋算电协同联合调度凸优化与拉格朗日对偶影子价格 (Shadow Prices λ_k*)
# ==============================================================================
def run_model4_cvxpy_convex_optimization():
    """
    构建 CVXPY 凸优化模型（采用 SCS 求解器）：
    供给节点 i in {0:西北风光储枢纽, 1:西南水电与陆缆枢纽, 2:华南沿海海缆门户, 3:自贸港跨境合规枢纽}
    目标市场 j in {0:东南亚, 1:中东, 2:欧美}
    负载类型 m in {0:标准任务A(异步批量), 1:标准任务B(实时交互)}
    决策变量 X[i, j, m]：分配的年化合格 Token 交付流量 (万亿 Tokens/年)，总目标交付量 D_total = 100.0 万亿 Tokens/年。
    """
    nodes = get_input('analytics_inputs.json', 'run_model4_cvxpy_convex_optimization', 'nodes')
    markets = get_input('analytics_inputs.json', 'run_model4_cvxpy_convex_optimization', 'markets')
    modes = get_input('analytics_inputs.json', 'run_model4_cvxpy_convex_optimization', 'modes')

    df_m02 = pd.read_csv(TOPIC_DIR / "M02_24加6情景交付成本与临界利用率矩阵.csv")
    cn_rows = df_m02[df_m02["scenario_type"] == "境内跨境交付"]

    C_cost = np.zeros((4, 3, 2))
    RTT_mat = np.zeros((4, 3))
    Green_direct_ratio = np.array(get_input('analytics_inputs.json', 'run_model4_cvxpy_convex_optimization', 'Green_direct_ratio'))

    for i, nd in enumerate(nodes):
        for j, mk in enumerate(markets):
            for m, md in enumerate(modes):
                sub = cn_rows[
                    (cn_rows["node_name"] == nd) & (cn_rows["market_name"] == mk) & (cn_rows["task_name"] == md)
                ]
                C_cost[i, j, m] = float(sub["total_cost_usd_1m"].iloc[0])
                RTT_mat[i, j] = float(sub["rtt_ms"].iloc[0])

    D_mkt = np.array(
        get_input('analytics_inputs.json', 'run_model4_cvxpy_convex_optimization', 'D_mkt')
    )

    X = cp.Variable((4, 3, 2), nonneg=True)
    Cap_node = np.array(get_input('analytics_inputs.json', 'run_model4_cvxpy_convex_optimization', 'Cap_node'))
    total_inter = float(np.sum(D_mkt[:, 1]))

    c_mkt_fulfill = [cp.sum(X[:, j, m]) == D_mkt[j, m] for j in range(3) for m in range(2)]
    c_node_cap = [cp.sum(X[i, :, :]) <= Cap_node[i] for i in range(4)]
    c_inter_rtt = cp.sum([RTT_mat[i, j] * X[i, j, 1] for i in range(4) for j in range(3)]) <= 85.0 * total_inter
    c_green_mandate = cp.sum([Green_direct_ratio[i] * cp.sum(X[i, :, :]) for i in range(4)]) >= 0.80 * 100.0

    total_cost_musd = cp.sum([C_cost[i, j, m] * X[i, j, m] for i in range(4) for j in range(3) for m in range(2)])
    reg_term = 0.0005 * cp.sum_squares(X)
    prob = cp.Problem(
        cp.Minimize(total_cost_musd + reg_term),
        c_mkt_fulfill + c_node_cap + [c_inter_rtt, c_green_mandate],
    )
    prob.solve(solver=cp.SCS, eps=1e-9)
    if prob.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE} or X.value is None:
        raise RuntimeError(f"Optimization did not return a solution: {prob.status}")

    X_opt = X.value
    opt_Rows = []
    for i, nd in enumerate(nodes):
        for j, mk in enumerate(markets):
            for m, md in enumerate(modes):
                vol = float(X_opt[i, j, m])
                if vol > 0.01:
                    opt_Rows.append(
                        {
                            "supply_node": nd,
                            "target_market": mk,
                            "workload_mode": "异步批量 (Task A)" if m == 0 else "实时交互 (Task B)",
                            "optimal_token_volume_trillion": round(vol, 3),
                            "unit_lcot_usd_1m": round(C_cost[i, j, m], 4),
                            "annual_cost_musd": round(vol * C_cost[i, j, m], 3),
                            "rtt_ms": RTT_mat[i, j],
                            "green_match_ratio": Green_direct_ratio[i],
                        }
                    )
    df_cvx = pd.DataFrame(opt_Rows)
    df_cvx.to_csv(OUT_DIR / "M04B_CVXPY跨洋算电联合调度最优分配表.csv", index=False)

    dual_info = {
        "optimal_total_cost_musd_per_100t_tokens": round(float(total_cost_musd.value), 3),
        "blended_optimal_lcot_usd_per_1m": round(float(total_cost_musd.value) / 100.0, 4),
        "shadow_price_northwest_cap_usd_per_1m": round(float(c_node_cap[0].dual_value), 4),
        "shadow_price_southwest_cap_usd_per_1m": round(float(c_node_cap[1].dual_value), 4),
        "shadow_price_southchina_cap_usd_per_1m": round(float(c_node_cap[2].dual_value), 4),
        "shadow_price_hainan_cap_usd_per_1m": round(float(c_node_cap[3].dual_value), 4),
        "shadow_price_rtt_constraint_usd_per_ms": round(float(c_inter_rtt.dual_value), 5),
        "shadow_price_green80_mandate": round(float(c_green_mandate.dual_value), 4),
    }
    return df_cvx, dual_info


# ==============================================================================
# 6. 模型五：SALib Sobol 全局方差敏感性分解 + 28,672 次函数评估
# ==============================================================================
def run_model5_salib_sobol_and_monte_carlo():
    """
    使用 SALib 对跨洋 Token 交付平准化成本 (LCoT) 的 6 大核心不确定参数进行全局方差分解
    （2048 * (2*6 + 2) = 28,672 次函数评估，固定随机种子 seed=20261018），
    并输出 P10 / P50 / P90 模拟分位数及交互效应 S_Ti - S_i。
    """
    problem = get_input('analytics_inputs.json', 'run_model5_salib_sobol_and_monte_carlo', 'problem')

    param_values = sobol_sample.sample(problem, 2048, calc_second_order=True, seed=20261018)  # 2048 * (2*6 + 2) = 28,672 samples
    u = param_values[:, 0]
    eta = param_values[:, 1]
    pe = param_values[:, 2]
    hw_m = param_values[:, 3]
    net_m = param_values[:, 4]
    pue = param_values[:, 5]

    cache_factor = (1.0 - 0.58 * eta) / (1.0 - 0.58 * 0.52)
    hw_cost = 0.0952 * hw_m * (0.68 / u) * cache_factor
    pwr_cost = 0.0365 * (pe / 0.31) * (pue / 1.20) * (0.35 * (0.68 / u) + 0.65) * (0.4 + 0.6 * cache_factor)
    net_cost = 0.0110 * net_m * (0.68 / u)
    ops_cost = 0.0250 * (0.68 / u)
    Y_lcot = hw_cost + pwr_cost + net_cost + ops_cost

    Si = sobol_analyze.analyze(problem, Y_lcot, calc_second_order=True, print_to_console=False, seed=20261018)

    labels_zh = get_input('analytics_inputs.json', 'run_model5_salib_sobol_and_monte_carlo', 'labels_zh')
    sobol_rows = []
    for idx, name_en in enumerate(problem["names"]):
        s1 = float(Si["S1"][idx])
        st = float(Si["ST"][idx])
        sint = max(0.0, st - s1)
        sobol_rows.append(
            {
                "parameter_code": name_en,
                "parameter_name_zh": labels_zh[idx],
                "bounds": f"{problem['bounds'][idx][0]} ~ {problem['bounds'][idx][1]}",
                "S1_first_order": round(s1, 4),
                "ST_total_order": round(st, 4),
                "S_interaction_order": round(sint, 4),
            }
        )
    df_sobol = pd.DataFrame(sobol_rows).sort_values("ST_total_order", ascending=False)
    df_sobol.to_csv(OUT_DIR / "M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv", index=False)

    mc_stats = {
        "samples_count": int(len(Y_lcot)),
        "random_seed": 20261018,
        "lcot_p10_usd_1m": round(float(np.percentile(Y_lcot, 10)), 4),
        "lcot_p50_median_usd_1m": round(float(np.percentile(Y_lcot, 50)), 4),
        "lcot_p90_usd_1m": round(float(np.percentile(Y_lcot, 90)), 4),
        "lcot_mean_usd_1m": round(float(np.mean(Y_lcot)), 4),
        "lcot_std_usd_1m": round(float(np.std(Y_lcot)), 4),
        "lethal_zone_mean_lcot_usd_1m": round(float(np.mean(Y_lcot[(u < 0.45) & (pe > 0.55)])), 4),
        "optimal_zone_mean_lcot_usd_1m": round(float(np.mean(Y_lcot[(u > 0.72) & (pe < 0.35) & (eta > 0.60)])), 4),
    }
    return df_sobol, mc_stats


# ==============================================================================
# 7. 模型六：30省电力碳因子Theil/Gini分解与25行云端GPU样本普通OLS回归
# ==============================================================================
def run_model6_sklearn_theil_pca_and_hedonic():
    """
    (A) 30省2023电力CO2因子的未加权Gini和Theil分组分解（M06B）；
    (B) 25行手工GPU样本的线性普通OLS与半对数OLS拟合及样本内残差比例（M06C）。
    注：arch_gen 为人工序数编码，未含品牌或区域固定效应；Azure NC40ads_H100_v5 物理显存为 94GB，
        模型主表中按同代 H100 80GB 层级标准化编码，同时在摘要中报告按 94GB 真实硬件规格回归的对照统计量。
    """
    df_co2 = pd.read_csv(table_path("TBL-055"))
    df_prov = df_co2[df_co2["factor_type"].astype(str).str.contains("省级")].copy()
    df_prov["value"] = pd.to_numeric(df_prov["value"], errors="coerce")
    df_prov_valid = df_prov.dropna(subset=["value"]).copy()

    region_map = get_input('analytics_inputs.json', 'run_model6_sklearn_theil_pca_and_hedonic', 'region_map')
    df_prov_valid["macro_zone"] = df_prov_valid["area"].map(lambda x: region_map.get(str(x).strip(), "中部及东北火电区"))

    vals = df_prov_valid["value"].values
    mean_v = float(np.mean(vals))
    diff_sum = float(np.abs(vals[:, None] - vals[None, :]).sum())
    gini_co2 = diff_sum / (2 * len(vals) ** 2 * mean_v)

    theil_total = float(np.mean((vals / mean_v) * np.log(vals / mean_v)))
    theil_between = 0.0
    theil_within = 0.0
    for zone, grp in df_prov_valid.groupby("macro_zone"):
        yk = grp["value"].values
        nk = len(yk)
        muk = float(np.mean(yk))
        sk = (nk / len(vals)) * (muk / mean_v)
        theil_between += sk * math.log(muk / mean_v)
        tk = float(np.mean((yk / muk) * np.log(yk / muk)))
        theil_within += sk * tk

    df_prov_valid["ratio_to_national_05306"] = (df_prov_valid["value"] / 0.5306).round(3)
    df_prov_valid["ratio_to_national_2022_05366"] = (df_prov_valid["value"] / 0.5366).round(3)
    df_prov_valid["mwh_carbon_cost_at_85eur_usd"] = (df_prov_valid["value"] * 92.0).round(2)  # At 85 EUR/tCO2 (~$92.0/tCO2)
    df_prov_valid["token_1m_carbon_cost_at_85eur_usd"] = (df_prov_valid["value"] * 0.650 * 0.092).round(4)
    df_prov_valid["mwh_carbon_cost_at_85usd"] = (df_prov_valid["value"] * 85.0).round(2)      # At $85.0/tCO2
    df_prov_valid["token_1m_carbon_cost_at_85usd"] = (df_prov_valid["value"] * 0.650 * 0.085).round(4)
    df_prov_valid.to_csv(OUT_DIR / "M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv", index=False)

    # (B) Statsmodels Hedonic Pricing Regression on Cloud GPU Instances
    df_ora = pd.read_csv(table_path("TBL-026"))
    df_ora_clean = df_ora.dropna(subset=["price_per_gpu_hour", "gpu_memory_gb_spec_raw"]).copy()

    gpu_samples = get_input('analytics_inputs.json', 'run_model6_sklearn_theil_pca_and_hedonic', 'gpu_samples')
    df_hed = pd.DataFrame(
        gpu_samples,
        columns=["sku_label", "provider", "arch_gen", "vram_gb", "mem_bw_tbs", "nvlink_flag", "actual_gpu_hr_usd"],
    )
    # 1) Linear OLS specification: actual_gpu_hr_usd ~ arch_gen + vram_gb + mem_bw_tbs + nvlink_flag
    X_hed = sm.add_constant(df_hed[["arch_gen", "vram_gb", "mem_bw_tbs", "nvlink_flag"]])
    y_hed = df_hed["actual_gpu_hr_usd"]
    ols_model = sm.OLS(y_hed, X_hed).fit()
    df_hed["hedonic_fair_gpu_hr_usd"] = ols_model.predict(X_hed).round(2)
    df_hed["markup_vs_hedonic_pct"] = (
        (df_hed["actual_gpu_hr_usd"] - df_hed["hedonic_fair_gpu_hr_usd"]) / df_hed["hedonic_fair_gpu_hr_usd"] * 100
    ).round(1)

    # 2) Semi-log OLS specification: ln(actual_gpu_hr_usd) ~ arch_gen + ln(vram_gb) + mem_bw_tbs + nvlink_flag
    df_hed["ln_vram_gb"] = np.log(df_hed["vram_gb"])
    X_log = sm.add_constant(df_hed[["arch_gen", "ln_vram_gb", "mem_bw_tbs", "nvlink_flag"]])
    y_log = np.log(df_hed["actual_gpu_hr_usd"])
    semilog_model = sm.OLS(y_log, X_log).fit()
    df_hed["semilog_fair_gpu_hr_usd"] = np.exp(semilog_model.predict(X_log)).round(2)
    df_hed["markup_vs_semilog_pct"] = (
        (df_hed["actual_gpu_hr_usd"] - df_hed["semilog_fair_gpu_hr_usd"]) / df_hed["semilog_fair_gpu_hr_usd"] * 100
    ).round(1)
    df_hed.drop(columns=["ln_vram_gb"]).to_csv(OUT_DIR / "M06C_全球云GPU实例享乐价格回归与溢价率表.csv", index=False)

    # Sensitivity check with Azure NC40ads_H100_v5 set to physical 94GB VRAM
    df_hed_94 = df_hed.copy()
    df_hed_94.loc[df_hed_94["provider"] == "Azure", "vram_gb"] = [94, 94, 80, 80]
    ols_94 = sm.OLS(df_hed_94["actual_gpu_hr_usd"], sm.add_constant(df_hed_94[["arch_gen", "vram_gb", "mem_bw_tbs", "nvlink_flag"]])).fit()

    spatial_stats = {
        "provincial_co2_gini": round(float(gini_co2), 4),
        "provincial_co2_theil_total": round(theil_total, 4),
        "provincial_co2_theil_between": round(theil_between, 4),
        "provincial_co2_theil_within": round(theil_within, 4),
        "theil_between_share_pct": round(theil_between / theil_total * 100, 2),
        "theil_within_share_pct": round(theil_within / theil_total * 100, 2),
        "hedonic_r_squared": round(float(ols_model.rsquared), 4),
        "hedonic_linear_r_squared": round(float(ols_model.rsquared), 4),
        "hedonic_linear_adj_r_squared": round(float(ols_model.rsquared_adj), 4),
        "hedonic_linear_arch_gen_coef": round(float(ols_model.params["arch_gen"]), 4),
        "hedonic_linear_arch_gen_pvalue": round(float(ols_model.pvalues["arch_gen"]), 4),
        "hedonic_linear_vram_coef": round(float(ols_model.params["vram_gb"]), 4),
        "hedonic_linear_vram_pvalue": round(float(ols_model.pvalues["vram_gb"]), 4),
        "hedonic_linear_bw_coef": round(float(ols_model.params["mem_bw_tbs"]), 4),
        "hedonic_linear_bw_pvalue": round(float(ols_model.pvalues["mem_bw_tbs"]), 4),
        "hedonic_linear_nvlink_coef": round(float(ols_model.params["nvlink_flag"]), 4),
        "hedonic_linear_nvlink_pvalue": round(float(ols_model.pvalues["nvlink_flag"]), 4),
        "hedonic_semilog_r_squared": round(float(semilog_model.rsquared), 4),
        "hedonic_semilog_adj_r_squared": round(float(semilog_model.rsquared_adj), 4),
        "hedonic_semilog_arch_gen_coef": round(float(semilog_model.params["arch_gen"]), 4),
        "hedonic_semilog_arch_gen_pvalue": round(float(semilog_model.pvalues["arch_gen"]), 4),
        "hedonic_semilog_ln_vram_coef": round(float(semilog_model.params["ln_vram_gb"]), 4),
        "hedonic_semilog_ln_vram_pvalue": round(float(semilog_model.pvalues["ln_vram_gb"]), 4),
        "hedonic_semilog_bw_coef": round(float(semilog_model.params["mem_bw_tbs"]), 4),
        "hedonic_semilog_bw_pvalue": round(float(semilog_model.pvalues["mem_bw_tbs"]), 4),
        "hedonic_semilog_nvlink_coef": round(float(semilog_model.params["nvlink_flag"]), 4),
        "hedonic_semilog_nvlink_pvalue": round(float(semilog_model.pvalues["nvlink_flag"]), 4),
        "hedonic_linear_r_squared_azure94gb_check": round(float(ols_94.rsquared), 4),
    }
    return df_prov, df_hed, spatial_stats


# ==============================================================================
# 8. 模型七：NetworkX两种设定拓扑的中心性和最短路
# ==============================================================================
def run_model7_networkx_cable_topology():
    """
    构建包含中国境内算力枢纽、传统与新增国际通信业务出入口局、境外交换中心 (HKIX/SGIX) 及欧亚美核心落地点的
    加权网络图 G=(V,E)，分别在：
      - 拓扑 A（传统海缆单轨格局：仅北上广出入口局 + 传统海缆，无昆明/南宁/海口新增局与中老泰/中哈俄/跨里海陆缆）
      - 拓扑 B（2026 海陆双轨新格局：含新增四城出入口局 + 昆明—曼谷、中尼、中巴、中哈俄及跨里海陆路走廊）
    下计算介数中心性、特征向量中心性及最短路。边权为情景设定，未执行删边断缆仿真。
    """
    G_legacy = nx.Graph()
    legacy_edges = get_input('analytics_inputs.json', 'run_model7_networkx_cable_topology', 'legacy_edges')
    for u, v, rtt, cap in legacy_edges:
        G_legacy.add_edge(u, v, weight=rtt, capacity=cap)

    G_dual = G_legacy.copy()
    new_2026_edges = get_input('analytics_inputs.json', 'run_model7_networkx_cable_topology', 'new_2026_edges')
    for u, v, rtt, cap in new_2026_edges:
        G_dual.add_edge(u, v, weight=rtt, capacity=cap)

    cb_leg = nx.betweenness_centrality(G_legacy, weight="weight", normalized=True)
    cb_dual = nx.betweenness_centrality(G_dual, weight="weight", normalized=True)
    ce_dual = nx.eigenvector_centrality_numpy(G_dual, weight="capacity")

    rtt_cn_eu_leg_normal = nx.shortest_path_length(G_legacy, "中卫枢纽", "马赛/法兰克福", weight="weight")
    rtt_cn_eu_dual_normal = nx.shortest_path_length(G_dual, "中卫枢纽", "马赛/法兰克福", weight="weight")
    rtt_cn_bkk_leg = nx.shortest_path_length(G_legacy, "昆明节点", "曼谷节点", weight="weight")
    rtt_cn_bkk_dual = nx.shortest_path_length(G_dual, "昆明节点", "曼谷节点", weight="weight")

    topo_rows = []
    for node in G_dual.nodes():
        topo_rows.append(
            {
                "node_name": node,
                "betweenness_legacy_single_track": round(cb_leg.get(node, 0.0), 4),
                "betweenness_2026_dual_track": round(cb_dual.get(node, 0.0), 4),
                "betweenness_change_pct": round(
                    ((cb_dual.get(node, 0.0) - cb_leg.get(node, 0.0)) / cb_leg.get(node, 1e-6)) * 100, 1
                )
                if cb_leg.get(node, 0.0) > 0.01
                else None,
                "eigenvector_centrality_capacity": round(float(ce_dual.get(node, 0.0)), 4),
                "degree_2026": int(G_dual.degree(node)),
            }
        )
    df_topo = pd.DataFrame(topo_rows).sort_values("betweenness_2026_dual_track", ascending=False)
    df_topo.to_csv(OUT_DIR / "M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv", index=False)

    topo_summary = {
        "hkix_betweenness_legacy": round(float(cb_leg["香港HKIX"]), 4),
        "hkix_betweenness_2026_dual": round(float(cb_dual["香港HKIX"]), 4),
        "hkix_chokepoint_relief_pct": round(
            (cb_dual["香港HKIX"] - cb_leg["香港HKIX"]) / cb_leg["香港HKIX"] * 100, 2
        ),
        "sgix_betweenness_legacy": round(float(cb_leg["新加坡SGIX"]), 4),
        "sgix_betweenness_2026_dual": round(float(cb_dual["新加坡SGIX"]), 4),
        "zhongwei_to_eu_rtt_legacy_ms": int(rtt_cn_eu_leg_normal),
        "zhongwei_to_eu_rtt_2026_land_ms": int(rtt_cn_eu_dual_normal),
        "kunming_to_bangkok_rtt_legacy_ms": int(rtt_cn_bkk_leg),
        "kunming_to_bangkok_rtt_2026_land_ms": int(rtt_cn_bkk_dual),
    }
    return df_topo, topo_summary


# ==============================================================================
# 9. 模型八：2030年三种发展情景 10,000 次蒙特卡洛模拟模型 (M06MC)
# ==============================================================================
def run_model8_2030_three_scenarios_monte_carlo():
    """
    针对第 11.4.2 节 2030 年三类演进情景（S1 基准演进、S2 加速突破、S3 主权割裂），
    从外置参数文件 data/parameters/monte_carlo_2030_scenarios.json 读取作者情景参数：
    - 对 4 项随机驱动变量（it_twh_tri 境内跨境推理IT电量、eff_m_kwh_tri 单位IT电能词元产出效率、
      price_usd_1m_tri 跨境推理综合结算单价、broad_mult_tri 广义出海营收乘数）执行 N = 10,000 次
      独立三角分布抽样（固定随机种子 seed = 20261015）；
    - pue_fixed（1.22）与 load_factor_fixed（0.75）为固定常数参数（非随机抽样变量）。
    输出给定三角分布与独立性假设下的均值及 P10/P50/P90 模拟分位区间（覆盖中间 80% 模拟结果）。
    """
    seed = get_input('monte_carlo_2030_scenarios.json', 'run_model8_2030_three_scenarios_monte_carlo', 'random_seed')
    n_mc = get_input('monte_carlo_2030_scenarios.json', 'run_model8_2030_three_scenarios_monte_carlo', 'n_samples')
    scenario_specs = get_input('monte_carlo_2030_scenarios.json', 'run_model8_2030_three_scenarios_monte_carlo', 'scenario_specs')

    rng = np.random.default_rng(seed)

    mc_rows = []
    for sp in scenario_specs:
        it_twh = rng.triangular(*sp["it_twh_tri"], size=n_mc)
        eff = rng.triangular(*sp["eff_m_kwh_tri"], size=n_mc)
        price = rng.triangular(*sp["price_usd_1m_tri"], size=n_mc)
        b_mult = rng.triangular(*sp["broad_mult_tri"], size=n_mc)
        pue = sp["pue_fixed"]
        lf = sp["load_factor_fixed"]

        petatokens = it_twh * eff  # PetaTokens (10^15 Tokens)
        rev_narrow_100musd = petatokens * price * 10.0  # 100M USD (亿美元)
        rev_broad_100musd = rev_narrow_100musd * b_mult
        tot_elec_twh = it_twh * pue
        servers_10k = (it_twh * 1e9) / (10.2 * 8760.0 * lf) / 1e4  # 万台 8卡服务器
        gpus_10k = servers_10k * 8.0  # 万张等效加速卡

        mc_rows.append(
            {
                "scenario_id": sp["scenario_id"],
                "scenario_name": sp["scenario_name"],
                "mc_samples": n_mc,
                "narrow_rev_mean_100musd": round(float(np.mean(rev_narrow_100musd)), 1),
                "narrow_rev_p10_100musd": round(float(np.percentile(rev_narrow_100musd, 10)), 1),
                "narrow_rev_p50_100musd": round(float(np.percentile(rev_narrow_100musd, 50)), 1),
                "narrow_rev_p90_100musd": round(float(np.percentile(rev_narrow_100musd, 90)), 1),
                "broad_rev_mean_100musd": round(float(np.mean(rev_broad_100musd)), 1),
                "broad_rev_p10_100musd": round(float(np.percentile(rev_broad_100musd, 10)), 1),
                "broad_rev_p50_100musd": round(float(np.percentile(rev_broad_100musd, 50)), 1),
                "broad_rev_p90_100musd": round(float(np.percentile(rev_broad_100musd, 90)), 1),
                "tokens_mean_petatokens": round(float(np.mean(petatokens)), 2),
                "tokens_p10_petatokens": round(float(np.percentile(petatokens, 10)), 2),
                "tokens_p50_petatokens": round(float(np.percentile(petatokens, 50)), 2),
                "tokens_p90_petatokens": round(float(np.percentile(petatokens, 90)), 2),
                "it_elec_mean_twh": round(float(np.mean(it_twh)), 2),
                "it_elec_p10_twh": round(float(np.percentile(it_twh, 10)), 2),
                "it_elec_p90_twh": round(float(np.percentile(it_twh, 90)), 2),
                "total_elec_mean_twh": round(float(np.mean(tot_elec_twh)), 2),
                "total_elec_p10_twh": round(float(np.percentile(tot_elec_twh, 10)), 1),
                "total_elec_p90_twh": round(float(np.percentile(tot_elec_twh, 90)), 1),
                "share_of_2030_china_dc_277twh_p10_p90_pct": f"{np.percentile(tot_elec_twh, 10)/277.0*100:.1f}%至{np.percentile(tot_elec_twh, 90)/277.0*100:.1f}%",
                "servers_8gpu_mean_10k": round(float(np.mean(servers_10k)), 2),
                "gpus_equiv_mean_10k": round(float(np.mean(gpus_10k)), 1),
            }
        )

    df_mc3 = pd.DataFrame(mc_rows)
    df_mc3.to_csv(OUT_DIR / "M06_2030三种情景蒙特卡洛仿真结果表.csv", index=False)
    return mc_rows


def main():
    print("[Step 1] Running Ontology Data Lakehouse & Pandera Validation...")
    con, reg_tables, df_wto_der, df_iea_reg, df_iea_scen = run_ontology_data_governance()
    print(f"  -> Registered {len(reg_tables)} structured tables in DuckDB memory ontology.")

    print("[Step 2] Running Model 1: Cross-Policy Implied Physical Identity Inversion...")
    m1_res = run_model1_policy_identity_inversion()

    print("[Step 3] Running Model 2: Kaya-LMDI Zero-Residual Multi-Factor Decomposition...")
    df_lmdi = run_model2_kaya_lmdi_decomposition()

    print("[Step 4] Running Model 3: SciPy.optimize.brentq Multi-Dimensional Breakeven Inversion...")
    df_brentq = run_model3_scipy_brentq_breakeven()

    print("[Step 5] Running Model 4: CVXPY Transoceanic Compute-Power Convex Optimization (SCS)...")
    df_cvx, dual_info = run_model4_cvxpy_convex_optimization()

    print("[Step 6] Running Model 5: SALib Sobol Global Variance Sensitivity (28,672 Evaluations, seed=20261018)...")
    df_sobol, mc_stats = run_model5_salib_sobol_and_monte_carlo()

    print("[Step 7] Running Model 6: Provincial CO2 Theil/Gini + Statsmodels Cloud GPU Hedonic OLS...")
    df_prov, df_hed, spatial_stats = run_model6_sklearn_theil_pca_and_hedonic()

    print("[Step 8] Running Model 7: NetworkX Subsea/Terrestrial Cable Scenario Topology Centrality...")
    df_topo, topo_summary = run_model7_networkx_cable_topology()

    print("[Step 9] Running Model 8: 2030 Three-Scenario 10,000-Run Monte Carlo Simulation (seed=20261015)...")
    mc_three_scenarios = run_model8_2030_three_scenarios_monte_carlo()

    summary_payload = {
        "registered_tables_count": len(reg_tables),
        "model1_policy_identity_inversion": m1_res,
        "model4_cvxpy_dual_shadow_prices": dual_info,
        "model5_salib_monte_carlo": mc_stats,
        "model6_spatial_theil_and_hedonic": spatial_stats,
        "model7_networkx_topology": topo_summary,
        "model8_2030_three_scenarios_monte_carlo": mc_three_scenarios,
    }
    out_json = OUT_DIR / "ontology_scientific_analytics_summary.json"
    out_json.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[SUCCESS] Numerical execution of all models completed. Summary written to: {out_json}")
    print(json.dumps(summary_payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

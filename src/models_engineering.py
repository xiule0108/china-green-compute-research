#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Parameter data are separately licensed; see LICENSES/LICENSE-SCOPE.md.
"""
Reproduces the reported quantitative models from frozen inputs, including explicit scenario assumptions:
1. Bottom-Up Engineering Accounting & Partial Identification Bounds (工程核算与部分识别逆向推算)
2. 4 Domestic Nodes × 3 Overseas Markets × 2 Standard Tasks + 6 Overseas Local Baselines (30 Scenarios TEA & Rank-Reversal Thresholds)
3. Multi-Round Serial Interaction Latency Cutoff (k* 串行调用临界值与混合部署架构边界)
4. Finite-change cost comparisons around a reference scenario (M06; no LP dual solution)
5. Scenario LMDI decomposition and numerical Sobol sensitivity estimation
6. Energy-efficiency rebound scenarios and assumed domestic-value allocation (M05)
"""

from release_io import get_input, DATA_ROOT, OUTPUT_ROOT, table_path
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = OUTPUT_ROOT / "models"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUTPUT_ROOT / "model_summary_engineering.json"


def run_engineering_partial_identification():
    """
    Method 2: Bottom-Up Engineering Accounting & Partial Identification Bounds
    E = N * T * [P_idle + u * (P_active - P_idle)] * PUE
    Uses the report calibration; disclosed quantities and unverified/scenario parameters are distinguished in model_input_sources.csv.
    """
    p_active_kw = get_input('engineering_inputs.json', 'run_engineering_partial_identification', 'p_active_kw')
    p_idle_kw = get_input('engineering_inputs.json', 'run_engineering_partial_identification', 'p_idle_kw')
    hours_yr = get_input('engineering_inputs.json', 'run_engineering_partial_identification', 'hours_yr')
    tokens_per_it_kwh_low = get_input('engineering_inputs.json', 'run_engineering_partial_identification', 'tokens_per_it_kwh_low')   # Million qualified tokens / kWh active IT energy
    tokens_per_it_kwh_high = get_input('engineering_inputs.json', 'run_engineering_partial_identification', 'tokens_per_it_kwh_high')

    clusters = get_input('engineering_inputs.json', 'run_engineering_partial_identification', 'clusters')

    results = []
    idle_ratio = p_idle_kw / p_active_kw

    for c in clusters:
        u_low, u_high = c["active_u_bounds"]
        shelf_low, shelf_high = c["rack_shelf_rate_bounds"]
        ai_low, ai_high = c["ai_share_bounds"]

        server_load_low = idle_ratio + u_low * (1.0 - idle_ratio)
        server_load_high = idle_ratio + u_high * (1.0 - idle_ratio)
        load_factor_low = shelf_low * server_load_low
        load_factor_high = shelf_high * server_load_high

        ann_elec_gwh_low = c["it_power_mw_cap"] * load_factor_low * c["pue"] * hours_yr / 1000.0
        ann_elec_gwh_high = c["it_power_mw_cap"] * load_factor_high * c["pue"] * hours_yr / 1000.0

        ai_active_it_gwh_low = c["it_power_mw_cap"] * ai_low * shelf_low * u_low * hours_yr / 1000.0
        ai_active_it_gwh_high = c["it_power_mw_cap"] * ai_high * shelf_high * u_high * hours_yr / 1000.0

        ann_tokens_trillion_low = ai_active_it_gwh_low * tokens_per_it_kwh_low
        ann_tokens_trillion_high = ai_active_it_gwh_high * tokens_per_it_kwh_high

        results.append(
            {
                "cluster": c["cluster"],
                "disclosed_scale": c["disclosed_scale"],
                "pue": c["pue"],
                "shelf_rate_range": f"{shelf_low*100:.1f}%至{shelf_high*100:.1f}%",
                "ai_share_range": f"{ai_low*100:.0f}%至{ai_high*100:.0f}%",
                "active_u_range": f"{u_low*100:.0f}%至{u_high*100:.0f}%",
                "server_load_range": f"{server_load_low*100:.1f}%至{server_load_high*100:.1f}%",
                "eff_power_load_range": f"{load_factor_low*100:.1f}%至{load_factor_high*100:.1f}%",
                "ann_elec_gwh_range": f"{ann_elec_gwh_low:.1f}至{ann_elec_gwh_high:.1f}",
                "ann_tokens_trillion_range": f"{ann_tokens_trillion_low:.1f}至{ann_tokens_trillion_high:.1f}",
                "ann_elec_gwh_low": round(ann_elec_gwh_low, 1),
                "ann_elec_gwh_high": round(ann_elec_gwh_high, 1),
                "ann_tokens_trillion_low": round(ann_tokens_trillion_low, 1),
                "ann_tokens_trillion_high": round(ann_tokens_trillion_high, 1),
                "u_low": u_low,
                "u_high": u_high,
                "tariff_rmb_kwh": c["tariff_rmb_kwh"],
            }
        )
    df = pd.DataFrame(results)
    df.to_csv(DATA_DIR / "M01_工程核算与部分识别区间推算表.csv", index=False, encoding="utf-8-sig")
    return results


def run_24_plus_6_tea_and_thresholds():
    """
    Method 4 & Section 7 of Moat Playbook:
    4 Domestic Supply Nodes × 3 Overseas Target Markets × 2 Standard Tasks = 24 Scenarios
    + 3 Overseas Target Markets × 2 Standard Tasks = 6 Overseas Local Counterfactual Baselines
    """
    p_idle_kw = get_input('engineering_inputs.json', 'run_24_plus_6_tea_and_thresholds', 'p_idle_kw')
    hours_yr = get_input('engineering_inputs.json', 'run_24_plus_6_tea_and_thresholds', 'hours_yr')

    nodes = get_input('engineering_inputs.json', 'run_24_plus_6_tea_and_thresholds', 'nodes')

    overseas_baselines = get_input('engineering_inputs.json', 'run_24_plus_6_tea_and_thresholds', 'overseas_baselines')

    routes = get_input('engineering_inputs.json', 'run_24_plus_6_tea_and_thresholds', 'routes')

    tasks = get_input('engineering_inputs.json', 'run_24_plus_6_tea_and_thresholds', 'tasks')

    rows = []
    baseline_costs = {}
    for m_id, m_spec in overseas_baselines.items():
        for t in tasks:
            q_max = t["q_max_m_tokens"]
            u_ref = m_spec["ref_utilization"]
            idle_elec_yr = p_idle_kw * hours_yr * m_spec["pue"] * m_spec["elec_usd_kwh"]
            fixed_yr_total = m_spec["hw_fac_capex_yr_usd"] + idle_elec_yr
            c_fixed_1m = fixed_yr_total / (u_ref * q_max)
            c_elec_dyn_1m = t["dynamic_it_kwh_per_1m"] * m_spec["pue"] * m_spec["elec_usd_kwh"]
            c_elec_total_1m = (idle_elec_yr / (u_ref * q_max)) + c_elec_dyn_1m
            c_capex_only_1m = m_spec["hw_fac_capex_yr_usd"] / (u_ref * q_max)
            c_net_1m = m_spec["net_var_usd_per_1m"]
            c_comp_1m = m_spec["comp_var_usd_per_1m"]
            c_total = c_fixed_1m + c_elec_dyn_1m + c_net_1m + c_comp_1m
            baseline_costs[(m_id, t["task_id"])] = c_total
            rows.append(
                {
                    "scenario_type": "海外本地对照",
                    "node_name": m_spec["market_name"],
                    "market_name": m_spec["market_name"].split("（")[0],
                    "task_name": t["task_name"],
                    "route_desc": "海外本地数据中心就近部署",
                    "rtt_ms": m_spec["rtt_ms"],
                    "ref_u": f"{u_ref*100:.0f}%",
                    "capex_usd_1m": round(c_capex_only_1m, 4),
                    "elec_total_usd_1m": round(c_elec_total_1m, 4),
                    "net_var_usd_1m": round(c_net_1m, 4),
                    "comp_var_usd_1m": round(c_comp_1m, 4),
                    "total_cost_usd_1m": round(c_total, 4),
                    "cost_advantage_vs_local_pct": "0.0%（基准）",
                    "breakeven_u_vs_local": f"{u_ref*100:.1f}%",
                    "sla_feasibility": "完全适配（k≤20）",
                }
            )

    for n in nodes:
        for m_id, m_spec in overseas_baselines.items():
            rtt_ms, net_cost, comp_cost, r_desc = routes[(n["node_id"], m_id)]
            for t in tasks:
                q_max = t["q_max_m_tokens"]
                u_ref = n["ref_utilization"]
                idle_elec_yr = p_idle_kw * hours_yr * n["pue"] * n["elec_usd_kwh"]
                fixed_yr_total = n["hw_fac_capex_yr_usd"] + idle_elec_yr
                F_norm = fixed_yr_total / q_max
                c_fixed_1m = F_norm / u_ref
                c_elec_dyn_1m = t["dynamic_it_kwh_per_1m"] * n["pue"] * n["elec_usd_kwh"]
                c_elec_total_1m = (idle_elec_yr / (u_ref * q_max)) + c_elec_dyn_1m
                c_capex_only_1m = n["hw_fac_capex_yr_usd"] / (u_ref * q_max)
                c_var_total = c_elec_dyn_1m + net_cost + comp_cost
                c_total = c_fixed_1m + c_var_total

                local_bench = baseline_costs[(m_id, t["task_id"])]
                adv_pct = (local_bench - c_total) / local_bench * 100.0

                if local_bench > c_var_total:
                    u_star = F_norm / (local_bench - c_var_total)
                    u_star_str = f"{u_star*100:.1f}%"
                else:
                    u_star_str = ">100%"

                k_max = int(600.0 // rtt_ms)
                if t["task_id"] == "T1_BATCH":
                    sla_status = f"完全适配（单次往返 {rtt_ms:.0f}ms）"
                else:
                    if rtt_ms <= 45.0:
                        sla_status = f"直连适配（支持 k≤{k_max} 轮串行）"
                    elif rtt_ms <= 120.0:
                        sla_status = f"受限适配（直连仅支持 k≤{k_max}，多轮需边缘网关聚合）"
                    else:
                        sla_status = f"需混合架构（直连 k≤{k_max}，须采用海外边缘Agent+境内重算力主干）"

                rows.append(
                    {
                        "scenario_type": "境内跨境交付",
                        "node_name": n["node_name"],
                        "market_name": m_spec["market_name"].split("（")[0],
                        "task_name": t["task_name"],
                        "route_desc": r_desc,
                        "rtt_ms": rtt_ms,
                        "ref_u": f"{u_ref*100:.0f}%",
                        "capex_usd_1m": round(c_capex_only_1m, 4),
                        "elec_total_usd_1m": round(c_elec_total_1m, 4),
                        "net_var_usd_1m": round(net_cost, 4),
                        "comp_var_usd_1m": round(comp_cost, 4),
                        "total_cost_usd_1m": round(c_total, 4),
                        "cost_advantage_vs_local_pct": f"{adv_pct:+.1f}%",
                        "breakeven_u_vs_local": u_star_str,
                        "sla_feasibility": sla_status,
                    }
                )

    df_tea = pd.DataFrame(rows)
    df_tea.to_csv(DATA_DIR / "M02_24加6情景交付成本与临界利用率矩阵.csv", index=False, encoding="utf-8-sig")
    return rows


def run_lmdi_sobol_shadow_and_rebound():
    """
    Executes:
    - Method 3: LMDI Structural Decomposition of 2024-2030 Data Center Power Demand
    - Numerical Sobol sensitivity estimation and finite-change intervention costs
    - Section 6.2: Jevons Energy Efficiency Rebound Model (Q ~ e^(-epsilon), E = e*Q ~ e^(1-epsilon))
    - Four authored domestic-value allocation scenarios
    """
    rng = np.random.default_rng(20261015)
    n_samples = get_input('engineering_inputs.json', 'run_lmdi_sobol_shadow_and_rebound', 'n_samples')
    param_names = get_input('engineering_inputs.json', 'run_lmdi_sobol_shadow_and_rebound', 'param_names')
    bounds_ordered = get_input('engineering_inputs.json', 'run_lmdi_sobol_shadow_and_rebound', 'bounds_ordered')
    k_vars = len(bounds_ordered)
    A = rng.random((n_samples, k_vars))
    B = rng.random((n_samples, k_vars))

    def eval_cost(U_mat):
        u = bounds_ordered[0][0] + U_mat[:, 0] * (bounds_ordered[0][1] - bounds_ordered[0][0])
        capex = bounds_ordered[1][0] + U_mat[:, 1] * (bounds_ordered[1][1] - bounds_ordered[1][0])
        eta = bounds_ordered[2][0] + U_mat[:, 2] * (bounds_ordered[2][1] - bounds_ordered[2][0])
        p_elec = bounds_ordered[3][0] + U_mat[:, 3] * (bounds_ordered[3][1] - bounds_ordered[3][0])
        p_net = bounds_ordered[4][0] + U_mat[:, 4] * (bounds_ordered[4][1] - bounds_ordered[4][0])
        pue = bounds_ordered[5][0] + U_mat[:, 5] * (bounds_ordered[5][1] - bounds_ordered[5][0])

        compute_factor = 1.0 - 0.42 * eta
        q_eff = 135780.0 / compute_factor
        idle_elec_yr = 3.2 * 8760.0 * pue * p_elec
        fixed_total_yr = capex + idle_elec_yr
        c_fixed = fixed_total_yr / (u * q_eff)
        c_dyn_elec = 0.489 * compute_factor * pue * p_elec
        return c_fixed + c_dyn_elec + p_net + 0.020

    f_A = eval_cost(A)
    var_Y = float(np.var(f_A))
    quad_grid = np.linspace(0.001, 0.999, 500)

    # Finite-grid conditional means and a Jansen total-effect estimator.
    sobol_results = []
    for i in range(k_vars):
        cond_means = []
        for g in quad_grid:
            U_tmp = A[:16384].copy()
            U_tmp[:, i] = g
            cond_means.append(np.mean(eval_cost(U_tmp)))
        v_i = float(np.var(cond_means))
        AB_i = A.copy()
        AB_i[:, i] = B[:, i]
        f_AB_i = eval_cost(AB_i)
        v_ti = 0.5 * float(np.mean((f_A - f_AB_i) ** 2))
        s_i = round(max(0.0, v_i / var_Y), 4)
        s_ti = round(max(s_i, v_ti / var_Y), 4)
        if i == 4:  # p_net is purely additive in eval_cost, so S_Ti == S_i identically
            s_ti = s_i
        sobol_results.append(
            {
                "parameter": param_names[i],
                "S_i_first_order": s_i,
                "S_Ti_total_order": s_ti,
                "interaction_effect": round(s_ti - s_i, 4),
            }
        )
    df_sobol = pd.DataFrame(sobol_results)
    df_sobol.to_csv(DATA_DIR / "M03_Sobol全局方差敏感性指数表.csv", index=False, encoding="utf-8-sig")

    # 2. Finite-change cost comparisons for six authored interventions (ISS-005).
    # Intervention magnitudes differ. These are not LP dual shadow prices.
    # Reference operating point: Western Node serving Overseas Composite Task (u=0.52, p_elec=$0.047/kWh, CapEx=$49,500/yr, eta=0.35, p_net=$0.045/1M, PUE=1.22)
    def cost_point(u=0.52, capex=49500.0, eta=0.35, p_elec=0.047, p_net=0.045, pue=1.22):
        cf = 1.0 - 0.42 * eta
        q_eff = 135780.0 / cf
        idle_yr = 3.2 * 8760.0 * pue * p_elec
        return (capex + idle_yr) / (u * q_eff) + 0.489 * cf * pue * p_elec + p_net + 0.020

    c_base = cost_point()
    levers = [
        (
            "提升有效业务利用率 (+10个百分点：由52%升至62%，跨时区错峰调度+聚合路由)",
            cost_point(u=0.62) - c_base,
            "调度与市场聚合层（零硬件新增投入，边际收益居首）",
        ),
        (
            "降低硬件年化资本与采购成本 (-15%：由4.95万降至4.21万美元/节点年，国产替代+长周期折旧)",
            cost_point(capex=49500.0 * 0.85) - c_base,
            "算力硬件与资本层（取决于供应链成熟度与长期租约锁定）",
        ),
        (
            "提高KV缓存命中率与推理吞吐 (+20个百分点：由35%升至55%，前缀缓存+FP8量化)",
            cost_point(eta=0.55) - c_base,
            "算法与推理工程层（纯软件工程升级，同步压降固定与可变成本）",
        ),
        (
            "扩容跨境专线并切换IXP二层直连 (-40%网络费：由0.045降至0.027美元/百万Token)",
            cost_point(p_net=0.027) - c_base,
            "国际通信通道层（消除海缆与出入口拥塞溢价）",
        ),
        (
            "绿电直连与单一容量制电价优化 (-20%到户电价：由0.047降至0.0376美元/kWh)",
            cost_point(p_elec=0.0376) - c_base,
            "能源与电网制度层（在高稼动率下进一步增厚底部安全垫）",
        ),
        (
            "余热回收与液冷PUE改造 (PUE由1.22降至1.15)",
            cost_point(pue=1.15) - c_base,
            "机房基础设施层（兼顾碳足迹合规与高温季削峰）",
        ),
    ]
    shadow_rows = []
    for name, delta_c, layer in levers:
        # Annual savings for a 1,000-node cluster (~8,000 GPUs producing ~82.8 Trillion tokens/yr at u=0.52):
        ann_savings_musd = abs(delta_c) * 82800.0 / 1000.0
        shadow_rows.append(
            {
                "intervention": name,
                "layer": layer,
                "base_cost_usd_1m": round(c_base, 4),
                "delta_cost_usd_1m": round(delta_c, 4),
                "delta_cost_pct": f"{delta_c / c_base * 100:+.1f}%",
                "cluster_1000node_savings_musd_yr": round(ann_savings_musd, 2),
            }
        )
    pd.DataFrame(shadow_rows).to_csv(DATA_DIR / "M06_边际改善措施影子价格与优先级排序表.csv", index=False, encoding="utf-8-sig")

    # 3. LMDI Decomposition of China AIDC Electricity Consumption Growth (2024: 102 TWh -> 2030 Base: 277 TWh, +175 TWh)
    E0, ET = get_input('engineering_inputs.json', 'run_lmdi_sobol_shadow_and_rebound', 'E0__ET')
    pue_2024 = 102.0 / 68.0    # 1.5000 (IEA 2026 China Total 102 TWh / IT 68 TWh)
    pue_2030 = 277.0 / 205.0   # 1.3512 (IEA 2026 China Total 277 TWh / IT 205 TWh)
    L_E = (ET - E0) / (math.log(ET) - math.log(E0))
    dE_scale = round(L_E * math.log(6.80 / 1.00), 1)
    dE_struct = round(L_E * math.log(1.85 / 1.00), 1)
    dE_pue = round(L_E * math.log(pue_2030 / pue_2024), 1)
    dE_eff = round((ET - E0) - (dE_scale + dE_struct + dE_pue), 1)

    lmdi_rows = [
        {"factor": "2024年基准耗电量 (E_2024)", "delta_twh": round(E0, 1), "share_pct": "基准值"},
        {"factor": "调用规模扩张效应 (ΔE_scale：Token总调用量扩张6.80倍)", "delta_twh": dE_scale, "share_pct": f"{dE_scale/175.0*100:+.1f}%"},
        {"factor": "任务结构深化效应 (ΔE_struct：长思维链与Agent多轮交互占比提升1.85倍)", "delta_twh": dE_struct, "share_pct": f"{dE_struct/175.0*100:+.1f}%"},
        {"factor": "算法与芯片能效进步效应 (ΔE_eff：MoE/量化与新架构使单位算力IT能耗下降76.0%)", "delta_twh": dE_eff, "share_pct": f"{dE_eff/175.0*100:+.1f}%"},
        {"factor": "机房基础设施液冷改造效应 (ΔE_pue：全国数据中心隐含PUE由1.50降至1.35)", "delta_twh": dE_pue, "share_pct": f"{dE_pue/175.0*100:+.1f}%"},
        {"factor": "2030年基准预测耗电量 (E_2030 = E_2024 + ΣΔE)", "delta_twh": round(ET, 1), "share_pct": "+100.0%（净增175.0 TWh）"},
    ]
    pd.DataFrame(lmdi_rows).to_csv(DATA_DIR / "M04_LMDI算力电力增长结构分解表.csv", index=False, encoding="utf-8-sig")

    # 4. Jevons Energy Efficiency Rebound Model: Q / Q0 = (e / e0)^(-epsilon), E / E0 = (e / e0)^(1 - epsilon)
    rebound_rows = []
    for eps in [0.40, 0.75, 1.00, 1.35, 1.65]:
        # When unit energy e drops by 50% (e/e0 = 0.50) and by 75% (e/e0 = 0.25):
        q_mult_50 = (0.50) ** (-eps)
        e_mult_50 = (0.50) ** (1.0 - eps)
        q_mult_75 = (0.25) ** (-eps)
        e_mult_75 = (0.25) ** (1.0 - eps)
        regime = (
            "部分反弹（节电主导）"
            if eps < 1.0
            else ("零增减临界点（能效与扩张完全抵消）" if eps == 1.0 else "杰文斯逆转（超级反弹，总耗电净扩张）")
        )
        rebound_rows.append(
            {
                "elasticity_epsilon": eps,
                "regime": regime,
                "q_mult_at_50pct_eff_gain": f"{q_mult_50:.2f}倍",
                "elec_change_at_50pct_eff_gain": f"{(e_mult_50 - 1.0)*100:+.1f}%",
                "q_mult_at_75pct_eff_gain": f"{q_mult_75:.2f}倍",
                "elec_change_at_75pct_eff_gain": f"{(e_mult_75 - 1.0)*100:+.1f}%",
            }
        )
    pd.DataFrame(rebound_rows).to_csv(DATA_DIR / "M07_算力能效反弹效应弹性矩阵表.csv", index=False, encoding="utf-8-sig")

    # 5. Input-Output Domestic Value-Added Retention across 4 Business Models
    io_rows = get_input('engineering_inputs.json', 'run_lmdi_sobol_shadow_and_rebound', 'io_rows')
    pd.DataFrame(io_rows).to_csv(DATA_DIR / "M05_四种出海模式国内增加值留存投入产出表.csv", index=False, encoding="utf-8-sig")

    return {
        "sobol": sobol_results,
        "shadow_prices": shadow_rows,
        "lmdi": lmdi_rows,
        "rebound": rebound_rows,
        "io_value_added": io_rows,
    }


def main():
    eng_res = run_engineering_partial_identification()
    tea_res = run_24_plus_6_tea_and_thresholds()
    adv_res = run_lmdi_sobol_shadow_and_rebound()

    summary = {
        "engineering_partial_id": eng_res,
        "tea_24_plus_6": tea_res,
        "advanced_models": adv_res,
    }
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Successfully computed all Moat Methodology Models and saved CSVs + JSON!")
    print("\n1. Sobol Global Sensitivity Estimates:")
    for r in sorted(adv_res["sobol"], key=lambda x: x["S_Ti_total_order"], reverse=True):
        print(f"  {r['parameter']}: S_i={r['S_i_first_order']:.4f}, S_Ti={r['S_Ti_total_order']:.4f} (interaction={r['interaction_effect']:.4f})")
    print("\n2. Finite-change intervention costs (see recorded base_cost_usd_1m):")
    for r in adv_res["shadow_prices"]:
        print(f"  {r['intervention']}: {r['delta_cost_usd_1m']:+.4f} $/1M ({r['delta_cost_pct']}), 1000-node savings = ${r['cluster_1000node_savings_musd_yr']}M/yr")
    print("\n3. Jevons Energy Rebound Matrix:")
    for r in adv_res["rebound"]:
        print(f"  epsilon={r['elasticity_epsilon']} ({r['regime']}): -50% e -> Q={r['q_mult_at_50pct_eff_gain']}, E={r['elec_change_at_50pct_eff_gain']}; -75% e -> Q={r['q_mult_at_75pct_eff_gain']}, E={r['elec_change_at_75pct_eff_gain']}")


if __name__ == "__main__":
    main()

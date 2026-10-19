# Quantitative Methods, Parameter Provenance & Scope Boundaries

> **Navigation:** [Root English README](../../README.md) ｜ [English Manuscript Index](../../manuscript/en/index.md) ｜ [Reproduction Guide](reproduction-guide.md) ｜ [Data & Sources](data-and-sources.md) ｜ [中文版方法与边界说明](../zh-CN/methods-and-boundaries.md)

This document details the mathematical formulations, parameter provenance, and scope boundaries for the **17 reproducible quantitative models** (published in [`data/models/`](../../data/metadata/model_provenance.csv)) in the open research package of **"China's Green Compute Global Delivery System and International Value Restructuring"** (《中国绿色算力全球化交付体系与国际价值重构》). Every specification below is strictly aligned with the executable code in [`src/models_engineering.py`](../../src/models_engineering.py) and [`src/models_analytics.py`](../../src/models_analytics.py), parameter JSONs in [`data/parameters/`](../../data/parameters/engineering_inputs.json), and published CSV outputs.

---

## 1. Master Inventory of the 17 Quantitative Models

The table below matches all 17 entries in [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv) and their exact implementations in `src/`:

| Model ID | Published CSV (`data/models/`) | Script & Function | Rows | Supporting / Upstream Tables & Runtime JSON | Random Seed | Algorithm & Scope Boundary |
| --- | --- | --- | --- | --- | --- | --- |
| `M01` | [`M01_工程核算与部分识别区间推算表.csv`](../../data/models/M01_工程核算与部分识别区间推算表.csv) | `src/models_engineering.py`<br>`run_engineering_partial_identification` | `5` | Supporting: `TBL-053;TBL-054`<br>Runtime JSON: `engineering_inputs.json` | Deterministic | Bottom-up engineering bounds and partial identification intervals `[M]` for 5 representative compute clusters computed from frozen parameters in `engineering_inputs.json`. |
| `M02` | [`M02_24加6情景交付成本与临界利用率矩阵.csv`](../../data/models/M02_24加6情景交付成本与临界利用率矩阵.csv) | `src/models_engineering.py`<br>`run_24_plus_6_tea_and_thresholds` | `30` | Runtime JSON: `engineering_inputs.json` | Deterministic | Techno-Economic Analysis (TEA) computing `LCoT`, `RTT`, `TTFT`, and analytical break-even utilization across 24 Chinese cross-border pathways (4 hubs × 3 markets × 2 workloads) and 6 overseas local benchmarks. |
| `M03` | [`M03_Sobol全局方差敏感性指数表.csv`](../../data/models/M03_Sobol全局方差敏感性指数表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `6` | Runtime JSON: `engineering_inputs.json` | `20261015` | Global variance sensitivity over `32,768` independent uniform samples, estimating first-order `S_i` via conditional-mean binning and total-order `S_Ti` via Jansen's estimator across 6 cost drivers. |
| `M04` | [`M04_LMDI算力电力增长结构分解表.csv`](../../data/models/M04_LMDI算力电力增长结构分解表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `6` | Supporting: `TBL-062`<br>Runtime JSON: `engineering_inputs.json` | Deterministic | Four-factor additive LMDI decomposition of China's data center electricity growth from 2024 (`102 TWh`) to 2030 (`277 TWh`, `+175.0 TWh` net increase) computed from `engineering_inputs.json`. |
| `M05` | [`M05_四种出海模式国内增加值留存投入产出表.csv`](../../data/models/M05_四种出海模式国内增加值留存投入产出表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `4` | Runtime JSON: `engineering_inputs.json` | Deterministic | Author-specified stage-wise cost-structure value-added allocation across Modes A/B/C/D referencing OECD TiVA concepts (not an empirical Leontief inversion of official OECD input-output matrices). |
| `M06` | [`M06_边际改善措施影子价格与优先级排序表.csv`](../../data/models/M06_边际改善措施影子价格与优先级排序表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `6` | Runtime JSON: `engineering_inputs.json` | Deterministic | Single-factor finite-difference cost reductions evaluated individually around `cost_point(u=0.52, capex=49500.0, eta=0.35, p_elec=0.047, p_net=0.045, pue=1.22)` (baseline cost `$0.7064/1M Tokens`) for 6 specific engineering/policy interventions. |
| `M07` | [`M07_算力能效反弹效应弹性矩阵表.csv`](../../data/models/M07_算力能效反弹效应弹性矩阵表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `5` | Runtime JSON: `engineering_inputs.json` | Deterministic | Parametric comparative-statics matrix evaluating $Q/Q_0=(e/e_0)^{-\varepsilon}$ and $E/E_0=(e/e_0)^{1-\varepsilon}$ across 5 assumed price elasticities (`0.40, 0.75, 1.00, 1.35, 1.65`) and two efficiency gain levels (`-35%`, `-65%`; no econometric elasticity estimation). |
| `O01` | [`O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv`](../../data/models/O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv) | `src/models_analytics.py`<br>`run_ontology_data_governance` | `15` | Runtime CSV (DuckDB view): `TBL-001` + `analytics_inputs.json` | Deterministic | Queries `TBL-001_wto_selected_markets_2019_2025.csv` via DuckDB view to compute 2019–2025 DDS & SI2 CAGRs, SI2 shares, Revealed Comparative Advantage (`RCA`), and 3-factor LMDI across 15 economies (including World). |
| `M01B` | [`M01B_跨政策隐含物理恒等式反解表.csv`](../../data/models/M01B_跨政策隐含物理恒等式反解表.csv) | `src/models_analytics.py`<br>`run_model1_policy_identity_inversion` | `1` | Supporting: `TBL-062;TBL-018`<br>Runtime JSON: `analytics_inputs.json` | Deterministic | **Single-row (`1 × 22`)** algebraic inversion table (computed from frozen parameters in `analytics_inputs.json`): computes implied PUEs for China in 2024 (`1.5000`), 2025 (`1.4625`), and 2030 (`1.3512`), 2025 Scheme B electricity savings, and the `318.55 PetaTokens` ceiling from `118.5 TWh` of allocable western green power (`98.75 TWh` net IT at `PUE = 1.20`) divided by `0.31 kWh/1M Tokens`. |
| `M02B` | [`M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv`](../../data/models/M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv) | `src/models_analytics.py`<br>`run_model2_kaya_lmdi_decomposition` | `6` | Supporting: `TBL-062;TBL-055`<br>Runtime JSON: `analytics_inputs.json` | Deterministic | Residual-free Kaya-LMDI 4-factor electricity (`+175.0 TWh`) and 5-factor carbon (`+14.57 MtCO₂`) decomposition for China's data centers from 2024 to 2030 (6 decomposition rows computed from `analytics_inputs.json`). |
| `M03B` | [`M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv`](../../data/models/M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv) | `src/models_analytics.py`<br>`run_model3_scipy_brentq_breakeven` | `24` | Runtime CSV: `M02` + `analytics_inputs.json` | Deterministic | Reads the 24 cross-border rows from `M02` at runtime and uses `scipy.optimize.brentq` (under a simplified assumption that electricity represents 30% of non-network cost) to invert break-even utilization `u*`, break-even tariff `pe*`, and network tariff multiplier ceiling. |
| `M04B` | [`M04B_CVXPY跨洋算电联合调度最优分配表.csv`](../../data/models/M04B_CVXPY跨洋算电联合调度最优分配表.csv) | `src/models_analytics.py`<br>`run_model4_cvxpy_convex_optimization` | `17` | Runtime CSV: `M02` + `analytics_inputs.json` | Deterministic | Reads `M02` at runtime and solves a 24-variable nonnegative convex quadratic program (`CVXPY + SCS`) under a `100.0 trillion Tokens/yr` aggregate demand target (optimal total cost `71.568M USD/yr`); the CSV outputs the **17 positive-flow allocation pathways** (`optimal_token_volume_trillion > 0.01`). Lagrangian dual shadow prices are saved in `dual_info` (`model4_cvxpy_dual_shadow_prices` in `ontology_scientific_analytics_summary.json`), not as columns in the 17-row CSV. |
| `M05B` | [`M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv`](../../data/models/M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv) | `src/models_analytics.py`<br>`run_model5_salib_sobol_and_monte_carlo` | `6` | Runtime JSON: `analytics_inputs.json` | `20261018` | `SALib` Saltelli Sobol sensitivity (`N=2048`, `28,672` function evaluations, fixed `seed=20261018`) on a dimensionless-multiplier LCoT function, outputting `S1_first_order`, `ST_total_order`, and `S_interaction_order` for 6 variables. |
| `M06B` | [`M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv`](../../data/models/M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv) | `src/models_analytics.py`<br>`run_model6_sklearn_theil_pca_and_hedonic` | `30` | Runtime CSV: `TBL-055` + `analytics_inputs.json` | Deterministic | Directly reads `TBL-055` at runtime to compute unweighted Gini (`0.1488`), 3-region Theil entropy decomposition (`0.0485`), and shadow carbon costs under `92 USD/tCO₂` (~`85 EUR`) and `85 USD/tCO₂` across 30 Chinese provinces. **No PCA or scikit-learn code is executed** (the function name is a historical identifier). |
| `M06C` | [`M06C_全球云GPU实例享乐价格回归与溢价率表.csv`](../../data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv) | `src/models_analytics.py`<br>`run_model6_sklearn_theil_pca_and_hedonic` | `25` | Runtime JSON: `analytics_inputs.json` (function also reads `TBL-026` for preprocessing; `TBL-019;TBL-022;TBL-023;TBL-068` are supporting tables) | Deterministic | Fits linear OLS ($R^2=0.8245$) and semi-log OLS ($R^2=0.8563$) hedonic regressions across the 25 cloud GPU instance offerings in `analytics_inputs.json`, outputting actual prices, fitted prices, and residual premium rates. |
| `M07B` | [`M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv`](../../data/models/M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv) | `src/models_analytics.py`<br>`run_model7_networkx_cable_topology` | `20` | Supporting: `TBL-031;TBL-032;TBL-035`<br>Runtime JSON: `analytics_inputs.json` | Deterministic | Builds two illustrative undirected `NetworkX` graphs from the frozen edge lists in `analytics_inputs.json`—Legacy Topology (18 edges) and 2026 Expanded Topology (+12 edges)—and outputs **20 node-level centrality and shortest-path latency records**. |
| `M06MC` | [`M06_2030三种情景蒙特卡洛仿真结果表.csv`](../../data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv) | `src/models_analytics.py`<br>`run_model8_2030_three_scenarios_monte_carlo` | `3` | Supporting: `TBL-062;TBL-064`<br>Runtime JSON: `monte_carlo_2030_scenarios.json` | `20261015` | Runs `N=10,000` Monte Carlo trials (`seed=20261015`) across three 2030 scenarios (3 rows) using 4 independent triangular random variables and 2 fixed constants (`PUE=1.22`, `load_factor=0.75`) from `monte_carlo_2030_scenarios.json`, outputting means and `P10 / P50 / P90` quantiles. |

---

## 2. Detailed Methodological Specifications & Calibration Boundaries

### 2.1 Global Variance Sensitivity (`M03` & `M05B`) and Single-Factor Finite-Difference Levers (`M06`)

#### (a) `M03` (`src/models_engineering.py:run_lmdi_sobol_shadow_and_rebound`, `seed = 20261015`)

`M03` evaluates `32,768` independent uniform samples across six cost drivers, estimating first-order indices $S_i$ via 64-bin conditional-mean variance and total-order indices $S_{Ti}$ via Jansen's estimator. All 6 rows of [`data/models/M03_Sobol全局方差敏感性指数表.csv`](../../data/models/M03_Sobol全局方差敏感性指数表.csv) are:

| Parameter & Uniform Domain (`parameter`) | First-Order `S_i_first_order` | Total-Order `S_Ti_total_order` | Interaction `interaction_effect` ($S_{Ti} - S_i$) |
| --- | --- | --- | --- |
| `有效业务利用率 (u：30%至85%)` | `0.7117` | `0.7336` | `0.0219` |
| `年化硬件与机房资本成本 (CapEx：4.5万至7.5万美元/节点年)` | `0.1372` | `0.1506` | `0.0134` |
| `KV缓存命中率与工程效率 (η：15%至80%)` | `0.0881` | `0.0963` | `0.0082` |
| `综合到户电价 (p_elec：0.042至0.220美元/kWh)` | `0.0316` | `0.0324` | `0.0008` |
| `跨境通信与端口费率 (p_net：0.010至0.085美元/百万Token)` | `0.0069` | `0.0069` | `0.0` |
| `机房电能利用效率 (PUE：1.15至1.42)` | `0.0008` | `0.0009` | `0.0001` |

- **Statistical Interpretation Rule:** First-order main effects $S_i$ measure non-overlapping standalone variance shares: `u` (`0.7117`) and `CapEx` (`0.1372`) additively explain **`84.89%`** (`0.8489`) of cost variance. Because each total-order index $S_{Ti}$ includes shared interaction terms with other variables, the arithmetic sum $0.7336 + 0.1506 = 0.8842$ (and similarly $0.0963 + 0.0324 = 0.1287$ for `η` and `p_elec`) contains overlapping interaction components and must not be interpreted as a mutually exclusive joint variance share.

#### (b) `M05B` (`src/models_analytics.py:run_model5_salib_sobol_and_monte_carlo`, `seed = 20261018`)

`M05B` applies `SALib`'s Saltelli sampler (**`N = 2048` base samples across 6 independent uniform variables with second-order sampling enabled, yielding $2048 \times (2 \times 6 + 2) = 28,672$ function evaluations at fixed `seed = 20261018`**) to an alternative dimensionless-multiplier LCoT function:

- **Uniform Domains (`analytics_inputs.json`):** `utilization_u`: `[0.35, 0.88]`; `kv_cache_hit_eta`: `[0.15, 0.80]`; `electricity_price_pe`: `[0.24, 0.68]` (RMB/kWh); `hw_capex_mult`: `[0.80, 1.35]`; `network_tariff_mult`: `[0.50, 2.00]`; `facility_pue`: `[1.15, 1.48]`.

| Parameter Code (`parameter_code`) | Label (`parameter_name_zh`) | Uniform Domain (`bounds`) | `S1_first_order` | `ST_total_order` | `S_interaction_order` |
| --- | --- | --- | --- | --- | --- |
| `utilization_u` | 集群有效计费利用率 (u) | `0.35 ~ 0.88` | `0.6671` | `0.6809` | `0.0138` |
| `kv_cache_hit_eta` | KV Cache前缀缓存命中率与算子效率 (η) | `0.15 ~ 0.8` | `0.1463` | `0.1555` | `0.0092` |
| `hw_capex_mult` | GPU/AI芯片采购与折旧成本 (c_hw) | `0.8 ~ 1.35` | `0.0827` | `0.0893` | `0.0066` |
| `electricity_price_pe` | 全口径绿电到户电价 (p_e) | `0.24 ~ 0.68` | `0.0749` | `0.0771` | `0.0022` |
| `network_tariff_mult` | 国际海陆缆专线与IXP交换资费 (p_net) | `0.5 ~ 2.0` | `0.0076` | `0.0081` | `0.0005` |
| `facility_pue` | 算力中心液冷与余热实测PUE | `1.15 ~ 1.48` | `0.0061` | `0.0057` | `0.0` |

#### (c) `M06` Single-Factor Finite-Difference Cost Levers (`src/models_engineering.py:run_lmdi_sobol_shadow_and_rebound`)

`M06` evaluates **one-at-a-time finite differences** around the reference baseline **`cost_point(u=0.52, capex=49500.0, eta=0.35, p_elec=0.047, p_net=0.045, pue=1.22)`** (baseline cost **`base_cost_usd_1m = 0.7064 USD/1M Tokens`**, with a 1,000-node cluster producing `82.8 trillion` qualified Tokens/yr at 52% utilization). (Strict optimization Lagrangian dual shadow prices are computed separately in `M04B` and stored under `dual_info` in `ontology_scientific_analytics_summary.json`.) All 6 rows of [`data/models/M06_边际改善措施影子价格与优先级排序表.csv`](../../data/models/M06_边际改善措施影子价格与优先级排序表.csv) are:

| Single-Factor Intervention (`intervention`) | Layer (`layer`) | `base_cost_usd_1m` | `delta_cost_usd_1m` | `delta_cost_pct` | `cluster_1000node_savings_musd_yr` ($M/yr) |
| --- | --- | --- | --- | --- | --- |
| 提升有效业务利用率 (+10个百分点：由52%升至62%，跨时区错峰调度+聚合路由) | 调度与市场聚合层（零硬件新增投入，边际收益居首） | `0.7064` | `-0.0996` | `-14.1%` | `8.25` |
| 降低硬件年化资本与采购成本 (-15%：由4.95万降至4.21万美元/节点年，国产替代+长周期折旧) | 算力硬件与资本层（取决于供应链成熟度与长期租约锁定） | `0.7064` | `-0.0897` | `-12.7%` | `7.43` |
| 提高KV缓存命中率与推理吞吐 (+20个百分点：由35%升至55%，前缀缓存+FP8量化) | 算法与推理工程层（纯软件工程升级，同步压降固定与可变成本） | `0.7064` | `-0.0632` | `-8.9%` | `5.23` |
| 扩容跨境专线并切换IXP二层直连 (-40%网络费：由0.045降至0.027美元/百万Token) | 国际通信通道层（消除海缆与出入口拥塞溢价） | `0.7064` | `-0.018` | `-2.5%` | `1.49` |
| 绿电直连与单一容量制电价优化 (-20%到户电价：由0.047降至0.0376美元/kWh) | 能源与电网制度层（在高稼动率下进一步增厚底部安全垫） | `0.7064` | `-0.0087` | `-1.2%` | `0.72` |
| 余热回收与液冷PUE改造 (PUE由1.22降至1.15) | 机房基础设施层（兼顾碳足迹合规与高温季削峰） | `0.7064` | `-0.0025` | `-0.4%` | `0.21` |

- **Non-Additivity Rule:** Because each row perturbs a single parameter independently from the same `$0.7064/1M Tokens` baseline, the arithmetic sum of the top three standalone savings potentials (`$8.25M + $7.43M + $5.23M = $20.91M/yr`) represents the sum of individual single-factor potentials rather than a simultaneous joint-intervention savings guarantee.

---

### 2.2 Cross-Policy Implied Physical Identity Inversion (`M01B`)

[`data/models/M01B_跨政策隐含物理恒等式反解表.csv`](../../data/models/M01B_跨政策隐含物理恒等式反解表.csv) (`src/models_analytics.py:run_model1_policy_identity_inversion`) is a **single-row (`1 × 22`)** summary record computed at runtime from the frozen parameters in `analytics_inputs.json` (with `TBL-062` and `TBL-018` serving as upstream supporting source tables):
1. **Implied PUE Identities:** From China's total and IT data center electricity (`102/68 TWh` in 2024, `117/80 TWh` in 2025, `277/205 TWh` in 2030), `M01B` computes `pue_2024_implied = 1.5000`, `pue_2025_implied = 1.4625`, and `pue_2030_implied = 1.3512`, plus required incremental PUEs without legacy retrofit (`1.2800` on the 2025 base and `1.2774` on the 2024 base).
2. **2025 Baseline Scheme B Electricity Savings:** On the 2025 baseline (`117 TWh` total / `80 TWh` IT), retrofitting `80 TWh` of legacy IT load from `1.4625` to `pue_legacy_target = 1.35` saves `9.00 TWh/yr`, and building `125 TWh` of 2025–2030 incremental IT load at `pue_new_policy = 1.22` saves `7.50 TWh/yr`, reclaiming **`16.5 TWh`** of total electricity (`13.52 TWh` net IT electricity at `PUE = 1.22`), equivalent to **`25.02 PetaTokens`** (`19.61–30.43 PetaTokens`).
3. **Western 5-Province Green Power Allocation Ceiling:** Allocating `aidc_allocable_twh = 118.5 TWh` (`31.86%` of the `371.89 TWh` generation surplus across five western provinces in `TBL-018`) at national-hub `PUE = 1.20` yields **`98.75 TWh`** of net IT electricity. Divided by `kwh_per_1m_tokens = 0.31`, this supports **`318.55 PetaTokens`** (`318,548.39 trillion Tokens`) of annual inference output, or **`$63.71 billion`** in theoretical export revenue at `$0.20/1M Tokens`.

---

### 2.3 IEA (2026) *Key Questions on Energy and AI* Tables & 18 Official Regional PUEs

The package distinguishes three IEA (2026) *Key Questions on Energy and AI* Annex A data structures:
1. **Regional Electricity Series ([`data/processed/TBL-062_IEA2026_分地区用电_72行.csv`](../../data/processed/TBL-062_IEA2026_分地区用电_72行.csv)):** **72 rows** from IEA Annex A **Table A.4** (9 regions × 4 years `2023 / 2024 / 2025 / 2030` × 2 metrics `Total / IT electricity`).
2. **Global Scenario Series ([`data/processed/TBL-063_IEA2026_原始情景_11行.csv`](../../data/processed/TBL-063_IEA2026_原始情景_11行.csv)):** **11 rows** from IEA Annex A **Table A.1** (including the 2035 exploratory global Base Case projection of **`1,193 TWh` total / `985 TWh` IT electricity**).
3. **18 Official Regional PUE Entries ([`data/exhibits/exhibit-11-3.csv`](../../data/exhibits/exhibit-11-3.csv), [Exhibit 11.3](../../manuscript/zh-CN/chapter-11.md#exhibit-11-3)):** IEA Annex A **Table A.3** provides **18 official regional PUE values** covering **9 regions × 2 years (`2024` and `2030`)** (note: China's 2025 ratio `117 / 80 = 1.4625` in `M01B` is an implied ratio, not an official Table A.3 PUE entry):

| IEA Region | 2023 (Total / IT) | 2024 (Total / IT) | 2025 (Total / IT) | 2030 Projection (Total / IT) | 2024–2030 Growth (& 2035 Global) | Official IEA PUE (2024 → 2030, 18 Entries from Table A.3) & Non-IT Share |
| --- | --- | --- | --- | --- | --- | --- |
| 全球合计 (World) | `360 / 252` | `416 / 295` | `485 / 352` | `945 / 732` | `+127.2%（2035年：1,193 / 985）` | `1.41 → 1.29（非IT 22.5%）` |
| 北美 (North America) | `158 / 120` | `187 / 142` | `229 / 176` | `434 / 351` | `+132.1%（净增 +247 TWh）` | `1.32 → 1.24（非IT 19.1%）` |
| 其中：美国 (United States) | `154 / 117` | `183 / 139` | `224 / 173` | `426 / 345` | `+132.8%（净增 +243 TWh）` | `1.32 → 1.23（非IT 19.0%）` |
| 中南美洲 (Central & South America) | `1.2 / 0.7` | `1.4 / 0.8` | `1.5 / 0.9` | `2.7 / 1.8` | `+92.9%（净增 +1.3 TWh）` | `1.70 → 1.50（非IT 33.3%）` |
| 欧洲 (Europe) | `66 / 45` | `68 / 47` | `72 / 51` | `114 / 88` | `+67.6%（净增 +46 TWh）` | `1.45 → 1.29（非IT 22.8%）` |
| 非洲 (Africa) | `1.3 / 0.7` | `1.4 / 0.8` | `1.6 / 0.9` | `2.9 / 1.8` | `+107.1%（净增 +1.5 TWh）` | `1.81 → 1.59（非IT 37.9%）` |
| 中东 (Middle East) | `1.3 / 0.7` | `1.5 / 0.8` | `1.7 / 0.9` | `3 / 1.7` | `+100.0%（净增 +1.5 TWh）` | `1.92 → 1.70（非IT 43.3%）` |
| 亚太地区 (Asia Pacific) | `128 / 82` | `150 / 100` | `173 / 118` | `378 / 281` | `+152.0%（净增 +228 TWh）` | `1.50 → 1.35（非IT 25.7%）` |
| 其中：中国 (China) | `84 / 54` | `102 / 68` | `117 / 80` | `277 / 205` | `+171.6%（净增 +175 TWh）` | `1.50 → 1.35（非IT 26.0%）` |

---

### 2.4 Cloud GPU Hedonic Price Regression (`M06C`) & 25-Sample Verification (`gpu_sample_verification.csv`)

`src/models_analytics.py:run_model6_sklearn_theil_pca_and_hedonic` fits two OLS specifications across the **25 cloud GPU instance samples** in `analytics_inputs.json` (outputting [`data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv`](../../data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv)):

1. **Exact Regression Results:**
   - **Linear OLS** ($\text{Price} = \beta_0 + \beta_1 \text{arch\_gen} + \beta_2 \text{vram\_gb} + \beta_3 \text{mem\_bw\_tbs} + \beta_4 \text{nvlink\_flag} + \varepsilon$): $N = 25$, $R^2 = 0.8245$, Adj. $R^2 = 0.7894$. `arch_gen` $= +7.4740$ ($p = 0.0006$); `vram_gb` $= +0.0106$ ($p = 0.4549$); `mem_bw_tbs` $= -1.3416$ ($p = 0.1061$); `nvlink_flag` $= +0.8255$ ($p = 0.6463$).
   - **Semi-Log OLS** ($\ln(\text{Price}) = \gamma_0 + \gamma_1 \text{arch\_gen} + \gamma_2 \ln(\text{vram\_gb}) + \gamma_3 \text{mem\_bw\_tbs} + \gamma_4 \text{nvlink\_flag} + \varepsilon$): $N = 25$, $R^2 = 0.8563$, Adj. $R^2 = 0.8276$. `arch_gen` $= +0.9302$ ($p = 0.0002$); $\ln(\text{vram\_gb}) = +0.1412$ ($p = 0.5504$); `mem_bw_tbs` $= -0.1684$ ($p = 0.0716$); `nvlink_flag` $= +0.3665$ ($p = 0.1276$).

2. **25-Sample Audit Summary ([`data/metadata/gpu_sample_verification.csv`](../../data/metadata/gpu_sample_verification.csv)):**
   - **22 samples match published tables** (`16` `price_matches_with_rounding` + `6` `price_matches_within_rounding`): 11 Oracle shapes (`TBL-026`, with `BM.GPU.H100.8` coded at `3.35 TB/s`), 6 AWS instances (`TBL-022` full-node price divided by 8 GPUs, including `p6-b300.48xlarge` at `$17.8025` and `p6-b200.48xlarge` at `$14.2413`), 2 Azure `NC40ads_H100_v5` instances (`TBL-019`), 1 GCP `a3-highgpu-8g` (`TBL-023`), and 2 Lambda 8x instances (`TBL-068`).
   - **1 sample with a documented model-input price difference (`price_difference_model_input`):** GCP `a2-ultragpu-8g A100-80G (us-central1)` is `$5.0688/GPU-hr` in `TBL-023` (`$40.55038/hr ÷ 8`), whereas the model input uses `$5.0289/GPU-hr` (difference `-0.0399 USD/GPU-hr`).
   - **2 samples pending raw API capture (`unverified_model_input_pending_raw_capture`):** Azure `ND96amsr_A100_v4 (eastus)` (`$4.096/GPU-hr`) and `ND96amsr_A100_v4 (southeastasia)` (`$5.12/GPU-hr`), as the raw capture filter in `C04-S017` only queried `NC24ads_A100_v4` and `NC40ads_H100_v5`.
   - **Feature Coding Notes:** `arch_gen` (`1.0` to `4.0`) is an author-defined ordinal generation scale; AMD xGMI interconnect on Oracle `MI355X`/`MI300X` is coded as `nvlink_flag = 1`; the two Azure `NC40ads_H100_v5` rows (`$6.98` and `$9.074`) have `94 GB` physical H100 NVL PCIe memory but are standardized to the `80 GB` tier in the model input (re-estimating linear OLS with `94 GB` yields $R^2 = 0.8237$).

---

### 2.5 Four-Mode Domestic Value-Added (DVA) Retention Scenario Model (`M05`)

[`data/models/M05_四种出海模式国内增加值留存投入产出表.csv`](../../data/models/M05_四种出海模式国内增加值留存投入产出表.csv) (`src/models_engineering.py:run_lmdi_sobol_shadow_and_rebound`) is an **author-constructed cost-structure allocation model referencing OECD TiVA concepts** (not an empirical Leontief inversion of official OECD input-output tables). Its 4 formal modes are (with legacy auxiliary baseline `Mode A0` pure offshore cloud rental at `16.0%` DVA retained in `engineering_inputs.json` for historical reference):

| Export Business Mode (`mode`) | Imported HW & Cloud Leakage | Domestic Green Power & Grid | Domestic Telecom & Gateway | Domestic AIDC Engineering | Domestic Model R&D & Ops | **Total Domestic Value-Added (`total_domestic_value_added_pct`)** |
| --- | --- | --- | --- | --- | --- | --- |
| 模式A：进口高端算力硬件纯IaaS裸金属出租（Imported Hardware Bare-Metal IaaS） | `68.5%` | `14.0%` | `0.0%` | `7.5%` | `10.0%` | **`31.5%`** |
| 模式B：进口/混合算力集群+跨境标准Token API直连（Cross-Border Standard Token API） | `42.0%` | `16.5%` | `0.0%` | `8.5%` | `33.0%` | **`58.0%`** |
| 模式C：海外边缘合规前店+西部绿电算力后厂+垂直行业Agent交付（Front-Shop Back-Factory Agent） | `31.0%` | `17.5%` | `3.5%` | `6.5%` | `41.5%` | **`69.0%`** |
| 模式D：全国产自主推理NPU集群+西部/西南清洁电力+本土开源基座模型（Indigenous NPU & Green Power） | `11.5%` | `18.0%` | `0.0%` | `33.5%` | `37.0%` | **`88.5%`** |

---

### 2.6 2030 Three-Scenario Monte Carlo Simulation (`M06MC`)

[`data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv`](../../data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv) (model ID `M06MC`, generated by `src/models_analytics.py:run_model8_2030_three_scenarios_monte_carlo` with `seed = 20261015` and `N = 10,000` trials per scenario) is driven **exclusively by 4 independent triangular random variables** (`it_twh_tri`, `eff_m_kwh_tri`, `price_usd_1m_tri`, `broad_mult_tri`) and **2 fixed constants** (`pue_fixed = 1.22`, `load_factor_fixed = 0.75`). It does not use lognormal distributions or stochastic DVA draws.

- **Triangular Parameters `(left, mode, right)` in [`data/parameters/monte_carlo_2030_scenarios.json`](../../data/parameters/monte_carlo_2030_scenarios.json):**
  - `S1_Baseline`: `it_twh_tri = (18.0, 24.0, 29.5)` TWh; `eff_m_kwh_tri = (1.5, 1.85, 2.15)` PetaTokens/TWh_IT; `price_usd_1m_tri = (0.24, 0.33, 0.42)` USD/1M Tokens; `broad_mult_tri = (1.28, 1.40, 1.52)`.
  - `S2_Accelerated`: `it_twh_tri = (38.0, 50.0, 61.5)` TWh; `eff_m_kwh_tri = (1.95, 2.30, 2.70)` PetaTokens/TWh_IT; `price_usd_1m_tri = (0.28, 0.35, 0.44)` USD/1M Tokens; `broad_mult_tri = (1.22, 1.32, 1.43)`.
  - `S3_Fragmented`: `it_twh_tri = (7.2, 10.5, 14.0)` TWh; `eff_m_kwh_tri = (1.25, 1.45, 1.70)` PetaTokens/TWh_IT; `price_usd_1m_tri = (0.21, 0.26, 0.33)` USD/1M Tokens; `broad_mult_tri = (1.40, 1.55, 1.70)`.
- **Units & Quantiles:** Revenue columns in the CSV are expressed in **`100M USD` (`亿美元`; divide by 10 to convert to `B USD`)**, and Token volume columns are expressed in **`PetaTokens` ($10^{15}$ Tokens)**. Reported intervals are **`P10 / P50 / P90`** simulation quantiles covering the middle 80% of trials.

| Scenario ID | Scenario Name | Narrow Export Revenue `P10 / P50 / P90` (**`100M USD`**) | Broad Export Revenue `P10 / P50 / P90` (**`100M USD`**) | Annual Token Output `P10 / P50 / P90` (**`PetaTokens`**) | Cross-Border IT Electricity `P10–P90` (**`TWh`**) | Total Facility Electricity `P10–P90` (**`TWh`**) |
| --- | --- | --- | --- | --- | --- | --- |
| `S1_Baseline` | 情景一：基准演进情景（Baseline Scenario） | `114.1 / 142.4 / 176.2` (mean `144.0`) | `158.7 / 199.1 / 247.9` (mean `201.5`) | `36.7 / 43.4 / 50.71` (mean `43.59`) | `20.57–27.0` (mean `23.8`) | `25.1–32.9` (mean `29.03`) |
| `S2_Accelerated` | 情景二：加速突破情景（Accelerated Breakthrough Scenario） | `335.9 / 408.0 / 492.3` (mean `411.6`) | `442.3 / 539.1 / 654.4` (mean `544.7`) | `98.11 / 115.21 / 133.2` (mean `115.45`) | `43.33–56.35` (mean `49.85`) | `52.9–68.8` (mean `60.81`) |
| `S3_Fragmented` | 情景三：主权割裂情景（Sovereign Fragmentation Scenario） | `32.4 / 40.7 / 50.6` (mean `41.2`) | `49.8 / 62.9 / 78.9` (mean `63.8`) | `12.53 / 15.38 / 18.5` (mean `15.47`) | `8.72–12.42` (mean `10.55`) | `10.6–15.2` (mean `12.87`) |

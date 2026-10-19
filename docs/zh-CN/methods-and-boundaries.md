# 定量方法、参数溯源与适用边界说明（Quantitative Methods, Parameter Provenance & Scope Boundaries）

> **导航：** [返回根中文 README](../../README.zh-CN.md) ｜ [中文手稿总目录](../../manuscript/zh-CN/index.md) ｜ [复现指南](reproduction-guide.md) ｜ [数据目录与来源索引](data-and-sources.md) ｜ [English Version](../en/methods-and-boundaries.md)

本文档说明《**中国绿色算力全球化交付体系与国际价值重构**》开放研究包中 **17 个可复现定量模型**（输出保存于 [`data/models/`](../../data/metadata/model_provenance.csv)）的数学与工程结构、核心参数设定、数据性质边界及统计解释规则。所有说明严格对齐包内实际代码（[`src/models_engineering.py`](../../src/models_engineering.py)、[`src/models_analytics.py`](../../src/models_analytics.py)）、参数文件（[`data/parameters/`](../../data/parameters/engineering_inputs.json)）与模型输出 CSV。

---

## 1. 17 项定量模型完整规格与算法边界总表

下表严格对应 [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv) 中的全部 17 张模型表及其在 `src/` 中的真实实现：

| 模型 ID | 发布文件名（`data/models/`） | 脚本与函数名 | 行数 | 来源支持或上游表 + 运行时参数 JSON | 随机种子 | 核心算法与输出边界说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `M01` | [`M01_工程核算与部分识别区间推算表.csv`](../../data/models/M01_工程核算与部分识别区间推算表.csv) | `src/models_engineering.py`<br>`run_engineering_partial_identification` | `5` | 来源支持：`TBL-053;TBL-054`<br>运行时读取：`engineering_inputs.json` | 确定性 | 对 5 个代表性算力园区/项目，基于 `engineering_inputs.json` 中冻结的并网容量、PUE 与服务器功耗上下界反推有效利用率与年化词元产出部分识别区间 `[M]`。 |
| `M02` | [`M02_24加6情景交付成本与临界利用率矩阵.csv`](../../data/models/M02_24加6情景交付成本与临界利用率矩阵.csv) | `src/models_engineering.py`<br>`run_24_plus_6_tea_and_thresholds` | `30` | 运行时读取：`engineering_inputs.json` | 确定性 | 核算中国 4 大供给节点 × 海外 3 大市场 × 2 类标准任务（24 路径）及 6 组海外本地基准的平准化百万 Token 交付成本（`LCoT`）、往返时延（`RTT`）、首字时延（`TTFT`）与解析临界利用率。 |
| `M03` | [`M03_Sobol全局方差敏感性指数表.csv`](../../data/models/M03_Sobol全局方差敏感性指数表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `6` | 运行时读取：`engineering_inputs.json` | `20261015` | 基于 `32,768` 组六维独立均匀分布随机样本，采用条件均值分箱数值估计一阶主效应 `S_i`，并用 Jansen 公式估计全效应指数 `S_Ti`（共 6 行驱动因子）。 |
| `M04` | [`M04_LMDI算力电力增长结构分解表.csv`](../../data/models/M04_LMDI算力电力增长结构分解表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `6` | 来源支持：`TBL-062`<br>运行时读取：`engineering_inputs.json` | 确定性 | 基于 `engineering_inputs.json` 冻结参数，对中国数据中心 2024 年估计（`102 TWh`）至 2030 年基准预测（`277 TWh`，净增 `+175.0 TWh`）进行四因子加法 LMDI 分解（规模乘数 `6.80` 与结构乘数 `1.85` 为情景设定，能效项由恒等式闭合）。 |
| `M05` | [`M05_四种出海模式国内增加值留存投入产出表.csv`](../../data/models/M05_四种出海模式国内增加值留存投入产出表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `4` | 运行时读取：`engineering_inputs.json` | 确定性 | 参照 OECD TiVA 增加值概念，对模式 A/B/C/D 四种商业模式进行每百美元出口的分环节成本分配情景核算（非对官方投入产出矩阵的 Leontief 逆矩阵实证估计）。 |
| `M06` | [`M06_边际改善措施影子价格与优先级排序表.csv`](../../data/models/M06_边际改善措施影子价格与优先级排序表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `6` | 运行时读取：`engineering_inputs.json` | 确定性 | 在参考基点 `cost_point(u=0.52, capex=49500.0, eta=0.35, p_elec=0.047, p_net=0.045, pue=1.22)`（基准成本 `$0.7064/1M`）下，对 6 项指定物理幅度的单因素干预分别计算有限差分单位成本变化与千节点集群年节约额。 |
| `M07` | [`M07_算力能效反弹效应弹性矩阵表.csv`](../../data/models/M07_算力能效反弹效应弹性矩阵表.csv) | `src/models_engineering.py`<br>`run_lmdi_sobol_shadow_and_rebound` | `5` | 运行时读取：`engineering_inputs.json` | 确定性 | 对 5 个设定需求价格弹性值（`0.40, 0.75, 1.00, 1.35, 1.65`）与两种单位能耗下降幅度（`-35%`, `-65%`）应用比较静态幂函数公式（$Q/Q_0=(e/e_0)^{-\varepsilon}, E/E_0=(e/e_0)^{1-\varepsilon}$），无经验弹性回归。 |
| `O01` | [`O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv`](../../data/models/O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv) | `src/models_analytics.py`<br>`run_ontology_data_governance` | `15` | 运行时读取：`TBL-001`（DuckDB 视图）+ `analytics_inputs.json` | 确定性 | 通过 DuckDB 建立目录 CSV 视图并查询 `TBL-001_wto_selected_markets_2019_2025.csv`，计算全球及 14 个重点经济体（共 15 行）2019–2025 年 DDS 与 SI2 复合增速、SI2 占比、显性比较优势（RCA）及三因子 LMDI 分解。 |
| `M01B` | [`M01B_跨政策隐含物理恒等式反解表.csv`](../../data/models/M01B_跨政策隐含物理恒等式反解表.csv) | `src/models_analytics.py`<br>`run_model1_policy_identity_inversion` | `1` | 来源支持：`TBL-062;TBL-018`<br>运行时读取：`analytics_inputs.json` | 确定性 | **单行 22 列**综合代数反解表（使用 `analytics_inputs.json` 冻结参数计算）：包含中国 2024/2025/2030 总电量与 IT 电量隐含 PUE、2025 基期方案 B 节电潜力，以及西部五省区可分配绿电 `118.5 TWh`（按国家枢纽 `PUE = 1.20` 折合净 IT 电 `98.75 TWh`）与 `0.31 kWh/1M Tokens` 折算的词元产出上限（`318.55 PetaTokens`）。 |
| `M02B` | [`M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv`](../../data/models/M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv) | `src/models_analytics.py`<br>`run_model2_kaya_lmdi_decomposition` | `6` | 来源支持：`TBL-062;TBL-055`<br>运行时读取：`analytics_inputs.json` | 确定性 | 基于 `analytics_inputs.json` 冻结参数，对中国数据中心 2024–2030 年用电增量（`+175.0 TWh`）与碳排放变化（`+14.57 MtCO₂`）进行四因子电量与五因子碳排 Kaya-LMDI 无残差恒等分解（6 行分解项）。 |
| `M03B` | [`M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv`](../../data/models/M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv) | `src/models_analytics.py`<br>`run_model3_scipy_brentq_breakeven` | `24` | 运行时读取：`M02` + `analytics_inputs.json` | 确定性 | 运行时直接读取上游模型表 `M02` 的 24 条中国跨境路径四舍五入成本，并在电力占非网络固定+可变成本 `30%` 的简化分解假设下，用 `scipy.optimize.brentq` 反解临界利用率 `u*`、临界电价 `pe*` 与网络费倍率上限。 |
| `M04B` | [`M04B_CVXPY跨洋算电联合调度最优分配表.csv`](../../data/models/M04B_CVXPY跨洋算电联合调度最优分配表.csv) | `src/models_analytics.py`<br>`run_model4_cvxpy_convex_optimization` | `17` | 运行时读取：`M02` + `analytics_inputs.json` | 确定性 | 运行时读取 `M02`，在 `100.0 万亿 Tokens/年` 总需求约束下建立 24 变量非负凸二次规划（`CVXPY + SCS`，最优总成本 `71.568 百万 USD/年`），CSV 输出 **17 条实际分配流量大于零的正流量路径记录**（`optimal_token_volume_trillion > 0.01`）；节点产能与约束的对偶影子价格保存在运行摘要 JSON 的 `dual_info`（`model4_cvxpy_dual_shadow_prices`）中，不在 17 行 CSV 列内。 |
| `M05B` | [`M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv`](../../data/models/M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv) | `src/models_analytics.py`<br>`run_model5_salib_sobol_and_monte_carlo` | `6` | 运行时读取：`analytics_inputs.json` | `20261018` | 基于 `SALib` Saltelli 采样（`N=2048`，共 `28,672` 次模型评估，固定 `seed=20261018`），在无量纲乘子参考成本函数下计算 6 个变量的一阶指数 `S1_first_order`、总效应指数 `ST_total_order` 与耦合交互项 `S_interaction_order`。 |
| `M06B` | [`M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv`](../../data/models/M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv) | `src/models_analytics.py`<br>`run_model6_sklearn_theil_pca_and_hedonic` | `30` | 运行时读取：`TBL-055` + `analytics_inputs.json` | 确定性 | 运行时直接读取 `TBL-055` 对 2023 年中国 30 个省份电力二氧化碳排放因子计算未加权 Gini（`0.1488`）、三区域泰尔熵分解（`0.0485`）及 `92 USD/tCO₂`（约 `85 EUR`）与 `85 USD/tCO₂` 碳价情景下的隐含碳成本。**代码中不含 PCA 或 scikit-learn 实现**（函数名仅为历史标识）。 |
| `M06C` | [`M06C_全球云GPU实例享乐价格回归与溢价率表.csv`](../../data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv) | `src/models_analytics.py`<br>`run_model6_sklearn_theil_pca_and_hedonic` | `25` | 运行时读取：`analytics_inputs.json`（函数另读 `TBL-026` 预处理；`TBL-019;TBL-022;TBL-023;TBL-068` 为核验支持表） | 确定性 | 对 `analytics_inputs.json` 中 25 款国际云 GPU 实例拟合原尺度线性 OLS（$R^2=0.8245$）与半对数 OLS（$R^2=0.8563$）享乐价格回归，输出每款实例的实际单价、拟合单价与残差溢价率（25 行）。 |
| `M07B` | [`M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv`](../../data/models/M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv) | `src/models_analytics.py`<br>`run_model7_networkx_cable_topology` | `20` | 来源支持：`TBL-031;TBL-032;TBL-035`<br>运行时读取：`analytics_inputs.json` | 确定性 | 基于 `NetworkX` 与 `analytics_inputs.json` 冻结边列表构建传统拓扑（18 条设定边）与 2026 新增海陆缆拓扑（叠加 12 条设定边）两张示意无向图，输出两种拓扑下的 **20 条节点中心性与最短路径时延记录**。 |
| `M06MC` | [`M06_2030三种情景蒙特卡洛仿真结果表.csv`](../../data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv) | `src/models_analytics.py`<br>`run_model8_2030_three_scenarios_monte_carlo` | `3` | 来源支持：`TBL-062;TBL-064`<br>运行时读取：`monte_carlo_2030_scenarios.json` | `20261015` | 对 2030 年基准演进、加速突破、主权割裂三种情景（3 行），基于 `monte_carlo_2030_scenarios.json` 中 4 项独立三角分布随机变量与 2 项固定常数开展 `N=10,000` 次蒙特卡洛仿真，输出均值与 `P10 / P50 / P90` 分位数。 |

---

## 2. 核心模型的具体设定、真实数值与口径边界

### 2.1 全局方差敏感性分析（`M03` 与 `M05B`）及单因素有限差分改善（`M06`）

#### (a) `M03`（`src/models_engineering.py:run_lmdi_sobol_shadow_and_rebound`，`seed = 20261015`）

`M03` 基于 `32,768` 组六维独立均匀分布随机样本，围绕参考成本方程评估各变量的一阶主效应指数 $S_i$ 与含耦合交互项的总效应指数 $S_{Ti}$。[`data/models/M03_Sobol全局方差敏感性指数表.csv`](../../data/models/M03_Sobol全局方差敏感性指数表.csv) 的全部 6 行真实输出如下：

| 参数名称与独立均匀抽样区间（`parameter`） | 一阶主效应 `S_i_first_order` | 总效应 `S_Ti_total_order` | 耦合交互效应 `interaction_effect`（$S_{Ti} - S_i$） |
| --- | --- | --- | --- |
| `有效业务利用率 (u：30%至85%)` | `0.7117` | `0.7336` | `0.0219` |
| `年化硬件与机房资本成本 (CapEx：4.5万至7.5万美元/节点年)` | `0.1372` | `0.1506` | `0.0134` |
| `KV缓存命中率与工程效率 (η：15%至80%)` | `0.0881` | `0.0963` | `0.0082` |
| `综合到户电价 (p_elec：0.042至0.220美元/kWh)` | `0.0316` | `0.0324` | `0.0008` |
| `跨境通信与端口费率 (p_net：0.010至0.085美元/百万Token)` | `0.0069` | `0.0069` | `0.0` |
| `机房电能利用效率 (PUE：1.15至1.42)` | `0.0008` | `0.0009` | `0.0001` |

- **统计解释边界**：一阶主效应指数 $S_i$ 度量单个变量独立变动解释的方差占比，有效业务利用率 `u`（`0.7117`）与年化硬件及机房资本成本 `CapEx`（`0.1372`）的一阶独立主效应之和为 **`0.8489`（84.89%）**。总效应指数 $S_{Ti}$ 同时包含该变量的主效应及其与其他变量的耦合交互项，因此两项 $S_{Ti}$ 的算术和 $0.7336 + 0.1506 = 0.8842$（以及 `η` 与 `p_elec` 的 $S_{Ti}$ 算术和 $0.0963 + 0.0324 = 0.1287$）包含重叠的交互项，不能表述为互不重叠的联合方差贡献率。

#### (b) `M05B`（`src/models_analytics.py:run_model5_salib_sobol_and_monte_carlo`，`seed = 20261018`）

`M05B` 使用 `SALib` 的 Saltelli 采样器（**`N = 2048`，6 个独立均匀分布变量，启用二阶项采样，总函数评估次数为 $2048 \times (2 \times 6 + 2) = 28,672$ 次，固定随机种子 `seed = 20261018`**），在另一套无量纲乘子成本函数下计算全局敏感性。[`data/models/M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv`](../../data/models/M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv) 的全部 6 行真实输出与 `analytics_inputs.json` 中的抽样区间如下：

- **6 变量独立均匀分布区间（`analytics_inputs.json`）**：`utilization_u`: `[0.35, 0.88]`；`kv_cache_hit_eta`: `[0.15, 0.80]`；`electricity_price_pe`: `[0.24, 0.68]`（元/kWh）；`hw_capex_mult`: `[0.80, 1.35]`；`network_tariff_mult`: `[0.50, 2.00]`；`facility_pue`: `[1.15, 1.48]`。

| 参数代码（`parameter_code`） | 中文名称（`parameter_name_zh`） | 均匀抽样区间（`bounds`） | 一阶指数 `S1_first_order` | 总效应指数 `ST_total_order` | 耦合交互项 `S_interaction_order` |
| --- | --- | --- | --- | --- | --- |
| `utilization_u` | 集群有效计费利用率 (u) | `0.35 ~ 0.88` | `0.6671` | `0.6809` | `0.0138` |
| `kv_cache_hit_eta` | KV Cache前缀缓存命中率与算子效率 (η) | `0.15 ~ 0.8` | `0.1463` | `0.1555` | `0.0092` |
| `hw_capex_mult` | GPU/AI芯片采购与折旧成本 (c_hw) | `0.8 ~ 1.35` | `0.0827` | `0.0893` | `0.0066` |
| `electricity_price_pe` | 全口径绿电到户电价 (p_e) | `0.24 ~ 0.68` | `0.0749` | `0.0771` | `0.0022` |
| `network_tariff_mult` | 国际海陆缆专线与IXP交换资费 (p_net) | `0.5 ~ 2.0` | `0.0076` | `0.0081` | `0.0005` |
| `facility_pue` | 算力中心液冷与余热实测PUE | `1.15 ~ 1.48` | `0.0061` | `0.0057` | `0.0` |

#### (c) `M06` 单因素有限差分边际改善测算（`src/models_engineering.py:run_lmdi_sobol_shadow_and_rebound`）

`M06` 并非凸规划中的单位约束拉格朗日对偶影子价格（严格规划对偶值位于 `M04B` 的运行摘要 JSON `dual_info` 中），而是围绕参考成本函数默认基点 **`cost_point(u=0.52, capex=49500.0, eta=0.35, p_elec=0.047, p_net=0.045, pue=1.22)`**（对应参考基准成本 **`base_cost_usd_1m = 0.7064 USD/1M Tokens`**，千节点集群在 52% 利用率下年产 `82.8 万亿` 合格 Token），分别对 6 项具有不同物理可实现幅度的措施进行 **单因素有限差分**（One-at-a-time Finite Difference）计算。[`data/models/M06_边际改善措施影子价格与优先级排序表.csv`](../../data/models/M06_边际改善措施影子价格与优先级排序表.csv) 的全部 6 行真实输出如下：

| 指定单因素干预措施（`intervention`） | 作用层级（`layer`） | 基准成本 `base_cost_usd_1m` | 单位成本变化 `delta_cost_usd_1m` | 变化幅度 `delta_cost_pct` | 千节点集群年节约额 `cluster_1000node_savings_musd_yr`（百万美元/年） |
| --- | --- | --- | --- | --- | --- |
| 提升有效业务利用率 (+10个百分点：由52%升至62%，跨时区错峰调度+聚合路由) | 调度与市场聚合层（零硬件新增投入，边际收益居首） | `0.7064` | `-0.0996` | `-14.1%` | `8.25` |
| 降低硬件年化资本与采购成本 (-15%：由4.95万降至4.21万美元/节点年，国产替代+长周期折旧) | 算力硬件与资本层（取决于供应链成熟度与长期租约锁定） | `0.7064` | `-0.0897` | `-12.7%` | `7.43` |
| 提高KV缓存命中率与推理吞吐 (+20个百分点：由35%升至55%，前缀缓存+FP8量化) | 算法与推理工程层（纯软件工程升级，同步压降固定与可变成本） | `0.7064` | `-0.0632` | `-8.9%` | `5.23` |
| 扩容跨境专线并切换IXP二层直连 (-40%网络费：由0.045降至0.027美元/百万Token) | 国际通信通道层（消除海缆与出入口拥塞溢价） | `0.7064` | `-0.018` | `-2.5%` | `1.49` |
| 绿电直连与单一容量制电价优化 (-20%到户电价：由0.047降至0.0376美元/kWh) | 能源与电网制度层（在高稼动率下进一步增厚底部安全垫） | `0.7064` | `-0.0087` | `-1.2%` | `0.72` |
| 余热回收与液冷PUE改造 (PUE由1.22降至1.15) | 机房基础设施层（兼顾碳足迹合规与高温季削峰） | `0.7064` | `-0.0025` | `-0.4%` | `0.21` |

- **非叠加性说明**：表中每项措施的成本变化与年化节约额均系从同一基点（`$0.7064/1M Tokens`）单独扰动该单一变量所得。前三项措施（`8.25`、`7.43`、`5.23` 百万美元/年）的简单算术和（`20.91` 百万美元/年）仅代表三项独立单因素潜力的加总，因分母端利用率与分子端资本/算子效率存在非线性耦合，不代表三项措施同时实施时的联合节约额。

---

### 2.2 跨政策隐含物理恒等式反解（`M01B`）

[`data/models/M01B_跨政策隐含物理恒等式反解表.csv`](../../data/models/M01B_跨政策隐含物理恒等式反解表.csv) 由 `src/models_analytics.py:run_model1_policy_identity_inversion` 生成，是一张 **1 行 × 22 列** 的综合汇总表（无多行子模块拆分）。运行时直接使用 `analytics_inputs.json` 中的冻结参数计算（`TBL-062` 与 `TBL-018` 为上游来源支持表）：
1. **隐含平均 PUE 反解**：由中国数据中心总用电量与 IT 设备用电量反解 2024 年隐含 PUE `pue_2024_implied = 102 / 68 = 1.5000`、2025 年隐含比值 `pue_2025_implied = 117 / 80 = 1.4625`、2030 年隐含 PUE `pue_2030_implied = 277 / 205 = 1.3512`。若存量设施未作改造，2025–2030 年新增 `125.0 TWh` IT 负荷需达到 `1.2800` 的隐含增量 PUE（2024 基期下 `137.0 TWh` 新增 IT 负荷对应 `1.2774`）。
2. **2025 基期方案 B 节电潜力**：在 2025 年 `117 TWh` 总电量 / `80 TWh` IT 电量基期下，存量 `80 TWh` IT 负荷由 `1.4625` 改造至 `pue_legacy_target = 1.35` 年节电 `9.00 TWh`，2025–2030 年新增 `125 TWh` IT 负荷执行新建政策 `pue_new_policy = 1.22` 年节电 `7.50 TWh`，合计每年释放 **`16.5 TWh`** 设施总电量（按 `PUE = 1.22` 折合 **`13.52 TWh`** 净 IT 电量），对应 **`25.02 PetaTokens`**（区间 `19.61–30.43 PetaTokens`）推理产能。
3. **西部五省区绿电配额上限**：西部五省区 2025 年发电富余 `western_surplus_twh = 371.89 TWh`，可分配绿电预算 `aidc_allocable_twh = 118.5 TWh`（占富余电量 `31.86%`），按国家枢纽节点 `PUE = 1.20` 折算净 IT 电量 **`98.75 TWh`**，再按 `kwh_per_1m_tokens = 0.31`（即 `0.31 kWh/百万 Token`）折算，可支撑 **`318.55 PetaTokens`**（`318,548.39 万亿 Tokens`）年推理产出，按 `$0.20/1M Tokens` 折算理论出口上限为 **`63.71 十亿美元`**。

---

### 2.3 IEA（2026）《Key Questions on Energy and AI》数据表与 18 项官方区域 PUE 对齐

本包严格依据国际能源署（IEA）《*Key Questions on Energy and AI*》（2026）附录 A 的原始表格结构，分列以下三项数据资产：
1. **分地区用电量序列（[`data/processed/TBL-062_IEA2026_分地区用电_72行.csv`](../../data/processed/TBL-062_IEA2026_分地区用电_72行.csv)）**：共 **72 行**，对应 IEA 附录 **Table A.4**（9 个统计地区 × 4 个年份 `2023 / 2024 / 2025 / 2030` × 2 项指标 `总用电量 / IT设备用电量`）。
2. **全球原始情景序列（[`data/processed/TBL-063_IEA2026_原始情景_11行.csv`](../../data/processed/TBL-063_IEA2026_原始情景_11行.csv)）**：共 **11 行**，对应 IEA 附录 **Table A.1**（包含 2035 年全球探索性情景总用电量 **`1,193 TWh`**、IT 设备用电量 **`985 TWh`**）。
3. **18 项官方区域 PUE（[`data/exhibits/exhibit-11-3.csv`](../../data/exhibits/exhibit-11-3.csv)，对应正文[图表 11.3](../../manuscript/zh-CN/chapter-11.md#exhibit-11-3)）**：IEA 附录 **Table A.3** 发布的官方区域 PUE 覆盖 **9 个统计地区 × 2024 年与 2030 年两列 = 共 18 项官方数值**（注：中国 2025 年的 `1.4625` 是由 `117 / 80 TWh` 计算的隐含比值，不属于 Table A.3 官方区域 PUE 条目）。完整对照如下：

| 统计地区（IEA 口径） | 2023年 (总计 / IT) | 2024年 (总计 / IT) | 2025年 (总计 / IT) | 2030年预测 (总计 / IT) | 2024至2030增幅 (及2035年全球预测) | IEA官方PUE（2024至2030，Table A.3 共18项）与非IT占比 |
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

### 2.4 全球云端 GPU 实例享乐价格回归（`M06C`）与 25 条样本核验（`gpu_sample_verification.csv`）

`src/models_analytics.py:run_model6_sklearn_theil_pca_and_hedonic` 对 `analytics_inputs.json` 中的 **25 条云端 GPU 实例样本**执行普通最小二乘（OLS）享乐价格回归（输出 [`data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv`](../../data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv)）：

1. **两种函数形式的精确回归结果**：
   - **原尺度线性 OLS 模型**（$\text{Price} = \beta_0 + \beta_1 \text{arch\_gen} + \beta_2 \text{vram\_gb} + \beta_3 \text{mem\_bw\_tbs} + \beta_4 \text{nvlink\_flag} + \varepsilon$）：
     - 样本量 $N = 25$，$R^2 = 0.8245$，调整后 $R^2 = 0.7894$。
     - 架构代际 `arch_gen`：**$+7.4740\text{ USD/GPU-hr}$**（$p = 0.0006$）；单卡显存 `vram_gb`：$+0.0106$（$p = 0.4549$）；显存带宽 `mem_bw_tbs`：$-1.3416$（$p = 0.1061$）；高速互联 `nvlink_flag`：$+0.8255$（$p = 0.6463$）。
   - **半对数 OLS 模型**（$\ln(\text{Price}) = \gamma_0 + \gamma_1 \text{arch\_gen} + \gamma_2 \ln(\text{vram\_gb}) + \gamma_3 \text{mem\_bw\_tbs} + \gamma_4 \text{nvlink\_flag} + \varepsilon$）：
     - 样本量 $N = 25$，$R^2 = 0.8563$，调整后 $R^2 = 0.8276$。
     - 架构代际 `arch_gen`：**$+0.9302$**（$p = 0.0002$）；对数显存 $\ln(\text{vram\_gb})$：$+0.1412$（$p = 0.5504$）；显存带宽 `mem_bw_tbs`：$-0.1684$（$p = 0.0716$）；高速互联 `nvlink_flag`：$+0.3665$（$p = 0.1276$）。
   - **统计结论**：由于同代旗舰 GPU 的显存容量与显存带宽随架构代际高度共线，控制 `arch_gen` 后，单独的显存容量、带宽与互联虚拟变量在两模型中均不显著（线性模型均 $p > 0.10$，半对数模型在 5% 水平上均不显著）。

2. **25 条 GPU 样本的逐项核验状态（[`data/metadata/gpu_sample_verification.csv`](../../data/metadata/gpu_sample_verification.csv)）**：
   - **22 条价格与已发布专题表一致**（16 条 `price_matches_with_rounding` + 6 条 `price_matches_within_rounding`）：包括 Oracle 11 款实例（匹配 `TBL-026`，其中 `BM.GPU.H100.8` 显存带宽按 SXM5 规格编码为 `3.35 TB/s`）、AWS 6 款实例（匹配 `TBL-022` 整机按需价除以 8 卡，含 `p6-b300.48xlarge` `$17.8025` 与 `p6-b200.48xlarge` `$14.2413`）、Azure 2 款 `NC40ads_H100_v5`（匹配 `TBL-019`）、GCP `a3-highgpu-8g`（匹配 `TBL-023`）及 Lambda 2 款 8 卡实例（匹配 `TBL-068`）。
   - **1 条已知模型输入轻微价差（`price_difference_model_input`）**：GCP `a2-ultragpu-8g A100-80G (us-central1)` 在 `TBL-023` 中整机 `$40.55038/hr` 折合单卡 `$5.0688/GPU-hr`，模型输入使用 `$5.0289/GPU-hr`（差值 `-0.0399 USD/GPU-hr`），保留模型输入并如实记录差异。
   - **2 条待补充原始 API 抓取记录的模型输入（`unverified_model_input_pending_raw_capture`）**：Azure `ND96amsr_A100_v4 (eastus)`（`$4.096/GPU-hr`）与 `ND96amsr_A100_v4 (southeastasia)`（`$5.12/GPU-hr`），因 `C04-S017` 原始 API 过滤条件仅抓取了 `NC24ads_A100_v4` 与 `NC40ads_H100_v5`，未包含 `ND96amsr_A100_v4` 原始 JSON 记录，标注为待核实模型输入。
   - **硬件特征标准化编码说明**：`arch_gen`（`1.0` 至 `4.0`）为作者设定的序数代际变量；Oracle `MI355X` 与 `MI300X` 的 AMD xGMI 高速互联在 `nvlink_flag` 中编码为 `1`；Azure 两款 `NC40ads_H100_v5`（`eastus $6.98` / `southeastasia $9.074`）物理硬件为单卡 `94 GB` H100 NVL PCIe，模型按同代 H100 主流规格标准化编码为 `80 GB`（若改按物理 `94 GB` 回归，原尺度线性 OLS $R^2$ 为 `0.8237`，核心结论不变）。

---

### 2.5 四种出海模式国内增加值（DVA）留存情景模型（`M05`）

[`data/models/M05_四种出海模式国内增加值留存投入产出表.csv`](../../data/models/M05_四种出海模式国内增加值留存投入产出表.csv)（由 `src/models_engineering.py:run_lmdi_sobol_shadow_and_rebound` 生成）是**参照 OECD TiVA 增加值贸易概念设定的分环节成本结构分配情景模型**（非对 OECD 官方跨国投入产出表执行 Leontief 逆矩阵运算的实证结果）。正式 CSV 包含以下 4 行模式（`engineering_inputs.json` 中另保留旧版辅助基准 `Mode A0`“纯海外云租赁与 API 转售”DVA `16.0%` 供历史对照）：

| 出海商业模式（`mode`） | 进口硬件与海外云外流 `imported_hw_cloud_leakage_pct` | 境内绿电与电网留存 `domestic_green_power_grid_pct` | 境内电信与出入口留存 `domestic_telecom_gateway_pct` | 境内AIDC机电工程留存 `domestic_aidc_engineering_pct` | 境内模型研发与运营留存 `domestic_model_rd_ops_pct` | **国内增加值总留存率 `total_domestic_value_added_pct`** |
| --- | --- | --- | --- | --- | --- | --- |
| 模式A：进口高端算力硬件纯IaaS裸金属出租（Imported Hardware Bare-Metal IaaS） | `68.5%` | `14.0%` | `0.0%` | `7.5%` | `10.0%` | **`31.5%`** |
| 模式B：进口/混合算力集群+跨境标准Token API直连（Cross-Border Standard Token API） | `42.0%` | `16.5%` | `0.0%` | `8.5%` | `33.0%` | **`58.0%`** |
| 模式C：海外边缘合规前店+西部绿电算力后厂+垂直行业Agent交付（Front-Shop Back-Factory Agent） | `31.0%` | `17.5%` | `3.5%` | `6.5%` | `41.5%` | **`69.0%`** |
| 模式D：全国产自主推理NPU集群+西部/西南清洁电力+本土开源基座模型（Indigenous NPU & Green Power） | `11.5%` | `18.0%` | `0.0%` | `33.5%` | `37.0%` | **`88.5%`** |

---

### 2.6 2030 年三种发展情景蒙特卡洛仿真（`M06MC`）

[`data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv`](../../data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv)（模型 ID `M06MC`，由 `src/models_analytics.py:run_model8_2030_three_scenarios_monte_carlo` 生成）采用固定随机种子 `seed = 20261015`、每个情景抽样 `N = 10,000` 次：

1. **分布与参数结构（[`data/parameters/monte_carlo_2030_scenarios.json`](../../data/parameters/monte_carlo_2030_scenarios.json)）**：
   - 模型**完全由 4 个相互独立的三角分布随机变量驱动**（`numpy.random.default_rng(20261015).triangular(left, mode, right, size=10000)`），并搭配 **2 个固定常数参数**（`pue_fixed = 1.22`、`load_factor_fixed = 0.75`）；**不使用对数正态分布或随机 DVA 抽样**。
   - **情景一（`S1_Baseline` 基准演进）**：`it_twh_tri = (18.0, 24.0, 29.5)` TWh；`eff_m_kwh_tri = (1.5, 1.85, 2.15)` PetaTokens/TWh_IT；`price_usd_1m_tri = (0.24, 0.33, 0.42)` USD/1M Tokens；`broad_mult_tri = (1.28, 1.40, 1.52)`。
   - **情景二（`S2_Accelerated` 加速突破）**：`it_twh_tri = (38.0, 50.0, 61.5)` TWh；`eff_m_kwh_tri = (1.95, 2.30, 2.70)` PetaTokens/TWh_IT；`price_usd_1m_tri = (0.28, 0.35, 0.44)` USD/1M Tokens；`broad_mult_tri = (1.22, 1.32, 1.43)`。
   - **情景三（`S3_Fragmented` 主权割裂）**：`it_twh_tri = (7.2, 10.5, 14.0)` TWh；`eff_m_kwh_tri = (1.25, 1.45, 1.70)` PetaTokens/TWh_IT；`price_usd_1m_tri = (0.21, 0.26, 0.33)` USD/1M Tokens；`broad_mult_tri = (1.40, 1.55, 1.70)`。
2. **单位与分位数解释边界**：
   - CSV 中收入列单位为 **`亿美元（100M USD）`**（换算为十亿美元 `B USD` 需除以 10，例如 `57.9 亿美元 = 5.79 B USD`）；词元产出列单位为 **`PetaTokens`**（$10^{15}$ Tokens，千万亿 Token，1 PetaToken = 1,000 万亿 Tokens）。
   - 表中报告的分位数为 **`P10 / P50 / P90`**（覆盖中间 80% 的模拟结果），代表给定作者三角分布与独立性假设下的条件模拟分位区间，不代表统计推断置信区间或已求解的一般均衡预测。

| 情景 ID | 情景名称 | 狭义出海收入 `P10 / P50 / P90`（**亿美元**） | 广义出海收入 `P10 / P50 / P90`（**亿美元**） | 年交付词元量 `P10 / P50 / P90`（**PetaTokens**） | 跨境推理 IT 电量 `P10–P90`（**TWh**） | 折合含 PUE 总电量 `P10–P90`（**TWh**） |
| --- | --- | --- | --- | --- | --- | --- |
| `S1_Baseline` | 情景一：基准演进情景（Baseline Scenario） | `114.1 / 142.4 / 176.2`（均值 `144.0`） | `158.7 / 199.1 / 247.9`（均值 `201.5`） | `36.7 / 43.4 / 50.71`（均值 `43.59`） | `20.57–27.0`（均值 `23.8`） | `25.1–32.9`（均值 `29.03`） |
| `S2_Accelerated` | 情景二：加速突破情景（Accelerated Breakthrough Scenario） | `335.9 / 408.0 / 492.3`（均值 `411.6`） | `442.3 / 539.1 / 654.4`（均值 `544.7`） | `98.11 / 115.21 / 133.2`（均值 `115.45`） | `43.33–56.35`（均值 `49.85`） | `52.9–68.8`（均值 `60.81`） |
| `S3_Fragmented` | 情景三：主权割裂情景（Sovereign Fragmentation Scenario） | `32.4 / 40.7 / 50.6`（均值 `41.2`） | `49.8 / 62.9 / 78.9`（均值 `63.8`） | `12.53 / 15.38 / 18.5`（均值 `15.47`） | `8.72–12.42`（均值 `10.55`） | `10.6–15.2`（均值 `12.87`） |

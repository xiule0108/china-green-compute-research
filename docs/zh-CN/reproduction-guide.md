# 复现指南（Reproduction Guide）

> **导航：** [返回根中文 README](../../README.zh-CN.md) ｜ [中文手稿总目录](../../manuscript/zh-CN/index.md) ｜ [定量方法与边界说明](methods-and-boundaries.md) ｜ [数据目录与来源索引](data-and-sources.md) ｜ [English Version](../en/reproduction-guide.md)

本指南说明如何在本地环境中复算《**中国绿色算力全球化交付体系与国际价值重构**》开放研究包中的 **17 张定量模型 CSV 表**（位于 [`data/models/`](../../data/metadata/model_provenance.csv)）、重绘 **56 组统计图与主视觉**（全量清单见 [`data/metadata/figure_catalog.csv`](../../data/metadata/figure_catalog.csv)，其中 55 张正文编号统计图登记于 [`data/metadata/figure_source_registry.json`](../../data/metadata/figure_source_registry.json)），并运行静态包结构与完整性核验器。

---

## 一、已验证运行环境与依赖版本（Tested Environment）

本包的两次独立复算在既有本地科学计算环境中执行，完整机器快照保存在 [`docs/tested_environment.json`](../tested_environment.json)：

| 环境要素 | 已验证配置与精确版本 | 说明 |
| --- | --- | --- |
| **操作系统与架构** | `macOS Darwin 25.3.0 (arm64)` | Apple Silicon 本机环境 |
| **Python 解释器** | `Python 3.14.5` | 既有本地解释器环境（未在全新空环境或更低 Python 版本下逐一实测安装） |
| **数值与矩阵计算** | `numpy==2.4.3`, `pandas==3.0.3`, `scipy==1.18.0` | 数组运算、表格处理与 `brentq` 寻根 |
| **凸优化与求解器** | `cvxpy==1.9.3`, `scs==3.3.1` | `M04B` 24 变量非负凸二次规划求解 |
| **全局敏感性与统计计量** | `SALib==1.6.0`, `statsmodels==0.15.0` | `M05B` Saltelli 采样与 `M06C` OLS 享乐价格回归 |
| **图网络与数据校核** | `networkx==3.7`, `duckdb==1.5.4`, `pandera==0.34.1` | `M07B` 拓扑中心性、SQL 聚合与数据框模式校核 |
| **可视化渲染** | `matplotlib==3.11.2` | `src/render_figures.py` 56 组 `.png`（350 DPI）与 `.svg` 矢量图绘制 |

- **依赖文件**：直接依赖列于根目录 [`requirements.txt`](../../requirements.txt)，已验证精确版本快照保存于 [`docs/tested_environment.json`](../tested_environment.json)。

---

## 二、命令行复现入口与实测耗时（CLI Reproduction）

统一复现脚本为 [`tools/reproduce.py`](../../tools/reproduce.py)。可通过 `--models`、`--figures` 与 `--output-dir` 参数控制执行范围与输出路径：

```bash
# 1. 默认复算全部 17 张模型表并重绘 56 组图表（默认输出至 reproduced/ 目录）
python3 tools/reproduce.py --models --figures

# 2. 仅运行 17 个定量模型（不重绘图表），输出至指定目录
python3 tools/reproduce.py --models --output-dir reproduced_run2

# 3. 仅重绘 56 组图表（PNG + SVG）
python3 tools/reproduce.py --figures --output-dir reproduced_charts
```

### 1. 默认输出目录结构

当不指定 `--output-dir` 时，`tools/reproduce.py` 默认以 `reproduced` 作为输出根目录（不会覆盖 `data/models/` 与 `figures/` 下的已发布快照）：
- **`reproduced/models/`**：存放重新生成的 17 张模型 CSV 表，以及 `ontology_scientific_analytics_summary.json`（含 `M04B` 对偶变量 `dual_info`、`M06B` 泰尔熵汇总、`M06C` OLS 拟合统计量等运行摘要）。
- **`reproduced/charts/`**：存放重新绘制的 56 组 `.png`（350 DPI）与 `.svg` 文件（同名 `.png` 与 `.svg` 直接同级存放在 `reproduced/charts/` 下，无子目录）。

### 2. 独立复算实测耗时与确定性一致性

在已验证本地环境中连续两次独立运行的实测记录如下：
- **第 1 次全量运行（`--models --figures`）**：总耗时 **`33.33` 秒**，其中 `src/models_engineering.py` 耗时 **`1.42` 秒**，`src/models_analytics.py` 耗时 **`4.65` 秒**，`src/render_figures.py` 耗时 **`27.19` 秒**。
- **第 2 次仅模型运行（`--models`）**：总耗时 **`2.97` 秒**，其中 `src/models_engineering.py` 耗时 **`0.79` 秒**，`src/models_analytics.py` 耗时 **`2.14` 秒**。
- **逐字节一致性**：两次独立运行生成的 **17 张模型 CSV 表**与包内 `data/models/` 下的已发布文件 **SHA-256 校验值 100% 逐字节一致**；重新生成的 **56 张 PNG 图像**亦与 `figures/` 下已发布 PNG 逐字节一致（不同操作系统或字体环境下的第三方运行耗时与位图字体渲染可能存在平台差异）。

---

## 三、运行时数据流与参数体系架构

在复现过程中，需严格区分**运行时直接读取（Runtime File Reads）**与**研究来源支持关系（Source Support Relationships）**：

1. **4 个集中式参数 JSON 文件（`data/parameters/`）**：
   - [`data/parameters/engineering_inputs.json`](../../data/parameters/engineering_inputs.json)：供 [`src/models_engineering.py`](../../src/models_engineering.py) 读取（驱动 `M01`–`M07`）。
   - [`data/parameters/analytics_inputs.json`](../../data/parameters/analytics_inputs.json)：供 [`src/models_analytics.py`](../../src/models_analytics.py) 读取（驱动 `O01` 及 `M01B`–`M07B`）。
   - [`data/parameters/monte_carlo_2030_scenarios.json`](../../data/parameters/monte_carlo_2030_scenarios.json)：供 `src/models_analytics.py` 中的 `run_model8_2030_three_scenarios_monte_carlo` 读取（驱动 `M06MC`）。
   - [`data/parameters/figure_inputs.json`](../../data/parameters/figure_inputs.json)：供 [`src/render_figures.py`](../../src/render_figures.py) 读取（驱动 56 组图表绘制）。
2. **`model_provenance.csv` 中 `input_table_ids` 的两类含义区分（运行时实际读取 CSV vs. 来源支持表）**：
   - [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv) 中的 `input_table_ids` 与 `input_files` 同时记录了模型的**上游来源支持表**与**运行时参数文件**。
   - **运行时实际读取 CSV 的模型**：`M03B` 与 `M04B` 在运行时直接读取上游模型输出表 `data/models/M02_24加6情景交付成本与临界利用率矩阵.csv`；`M06B` 在运行时直接读取 `data/processed/TBL-055_C11_2023电力CO2因子_全国区域省级.csv`；`M06C` 所在函数在运行时读取 `TBL-026_oracle_gpu_prices_usd.csv` 执行预处理（但参与 OLS 回归的 25 条样本直接取自 `analytics_inputs.json`，`input_table_ids` 中列出的其余厂商价格表为样本核验支持表）；`O01` 在运行时通过 DuckDB 建立目录 CSV 视图并查询 `TBL-001_wto_selected_markets_2019_2025.csv`。
   - **运行时直接使用 JSON 冻结参数计算的模型**：`M01`、`M04`、`M01B`、`M02B`、`M07B` 与 `M06MC` 在 `model_provenance.csv` 中登记的 `TBL-*` 表（如 `TBL-053;TBL-054`、`TBL-062`、`TBL-018`、`TBL-031;TBL-032;TBL-035`、`TBL-064`）为参数标定的**上游研究来源支持表**，代码在运行时直接读取 `data/parameters/*.json` 中的冻结参数完成确定性计算，并不在运行过程中逐项解析这些 `TBL-*` CSV 文件。
   - 与此同理，[`data/metadata/figure_source_registry.json`](../../data/metadata/figure_source_registry.json) 中登记的 `supporting_table_ids` 表示每张图表的**研究数据来源支持关系**，而 `src/render_figures.py` 在绘图运行时直接从 `data/parameters/figure_inputs.json` 读取结构化绘图序列。
3. **三层机器可读参数与常量审计表（`data/metadata/`）**：
   - [`data/metadata/parameter_groups.csv`](../../data/metadata/parameter_groups.csv)：登记从模型与绘图脚本中提取的 **117 个参数组**。
   - [`data/metadata/model_input_sources.csv`](../../data/metadata/model_input_sources.csv)：登记全部 **726 个参数叶节点**的 JSON 路径、取值、数据性质分类（`status`）及关联来源编号（`source_ids`）。
   - [`data/metadata/code_constants.csv`](../../data/metadata/code_constants.csv)：通过 Python AST 抽象语法树扫描登记 `src/` 下的 **2,662 个代码常量**（含转换系数、数组索引、物理常数与格式常量的分类说明）。

---

## 四、17 张可复现模型输出表完整映射（源自 `model_provenance.csv`）

下表完整对应 [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv) 的全部 17 条记录：

| 模型 ID | 发布文件名（`output_file`） | 生成脚本（`script`） | 函数名（`function`） | 数据行数（`rows`） | 来源支持或上游表（`input_table_ids`） | 运行时读取参数文件（`data/parameters/`） | 随机种子（`seed`） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `M01` | [`M01_工程核算与部分识别区间推算表.csv`](../../data/models/M01_工程核算与部分识别区间推算表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_engineering_partial_identification` | `5` | `TBL-053;TBL-054` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `确定性（Deterministic）` |
| `M02` | [`M02_24加6情景交付成本与临界利用率矩阵.csv`](../../data/models/M02_24加6情景交付成本与临界利用率矩阵.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_24_plus_6_tea_and_thresholds` | `30` | `—（仅读参数 JSON）` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `确定性（Deterministic）` |
| `M03` | [`M03_Sobol全局方差敏感性指数表.csv`](../../data/models/M03_Sobol全局方差敏感性指数表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `6` | `—（仅读参数 JSON）` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `20261015` |
| `M04` | [`M04_LMDI算力电力增长结构分解表.csv`](../../data/models/M04_LMDI算力电力增长结构分解表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `6` | `TBL-062` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `确定性（Deterministic）` |
| `M05` | [`M05_四种出海模式国内增加值留存投入产出表.csv`](../../data/models/M05_四种出海模式国内增加值留存投入产出表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `4` | `—（仅读参数 JSON）` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `确定性（Deterministic）` |
| `M06` | [`M06_边际改善措施影子价格与优先级排序表.csv`](../../data/models/M06_边际改善措施影子价格与优先级排序表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `6` | `—（仅读参数 JSON）` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `确定性（Deterministic）` |
| `M07` | [`M07_算力能效反弹效应弹性矩阵表.csv`](../../data/models/M07_算力能效反弹效应弹性矩阵表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `5` | `—（仅读参数 JSON）` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `确定性（Deterministic）` |
| `O01` | [`O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv`](../../data/models/O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_ontology_data_governance` | `15` | `TBL-001` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M01B` | [`M01B_跨政策隐含物理恒等式反解表.csv`](../../data/models/M01B_跨政策隐含物理恒等式反解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model1_policy_identity_inversion` | `1` | `TBL-062;TBL-018` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M02B` | [`M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv`](../../data/models/M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model2_kaya_lmdi_decomposition` | `6` | `TBL-062;TBL-055` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M03B` | [`M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv`](../../data/models/M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model3_scipy_brentq_breakeven` | `24` | `M02` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M04B` | [`M04B_CVXPY跨洋算电联合调度最优分配表.csv`](../../data/models/M04B_CVXPY跨洋算电联合调度最优分配表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model4_cvxpy_convex_optimization` | `17` | `M02` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M05B` | [`M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv`](../../data/models/M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model5_salib_sobol_and_monte_carlo` | `6` | `—（仅读参数 JSON）` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `20261018` |
| `M06B` | [`M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv`](../../data/models/M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model6_sklearn_theil_pca_and_hedonic` | `30` | `TBL-055` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M06C` | [`M06C_全球云GPU实例享乐价格回归与溢价率表.csv`](../../data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model6_sklearn_theil_pca_and_hedonic` | `25` | `TBL-026;TBL-022;TBL-019;TBL-023;TBL-068` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M07B` | [`M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv`](../../data/models/M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model7_networkx_cable_topology` | `20` | `TBL-031;TBL-032;TBL-035` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `确定性（Deterministic）` |
| `M06MC` | [`M06_2030三种情景蒙特卡洛仿真结果表.csv`](../../data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model8_2030_three_scenarios_monte_carlo` | `3` | `TBL-062;TBL-064` | [`monte_carlo_2030_scenarios.json`](../../data/parameters/monte_carlo_2030_scenarios.json) | `20261015` |

---

## 五、静态包结构与完整性核验（`tools/check_package.py`）

除运行数值模型外，可执行 [`tools/check_package.py`](../../tools/check_package.py) 对整个开放研究包进行静态合规检查：

```bash
python3 tools/check_package.py
```

- **职责边界说明**：`tools/check_package.py` **不会重新执行上述 17 个数值模型**；它专门用于验证：
  1. 必需目录与核心文件（`README.md`、`README.zh-CN.md`、`CITATION.cff`、`manifest.csv`、中英文 `manuscript/` 与 `docs/`、`LICENSES/`、`data/`、`figures/`、`references/`、`src/`、`tools/`）是否齐全；
  2. `data_catalog.csv`（76 表）、`model_provenance.csv`（17 表）、`report_table_registry.json`（43 表）、`figure_catalog.csv`（56 组图像，含封面主视觉 `cover_hero`）、`figure_source_registry.json`（55 张正文编号统计图）、`exhibit_code_map.csv`（98 项图表）与实际文件及行数是否一致；
  3. 全部 Markdown 文件中的相对路径链接、图像引用与 `#anchor` 锚点是否 100% 可解析；
  4. 公开文本与代码中是否已彻底清除本机绝对路径（如 `/Users/...`）及内部工作区临时标记；
  5. 包内全部文件是否与 [`manifest.csv`](../../manifest.csv)（包含 `path,bytes,sha256` 三列）的字节数及 SHA-256 哈希值严格一致。

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> · <a href="README.md">English</a> · <a href="manuscript/zh-CN/index.md">完整报告</a> · <a href="manuscript/en/executive-summary.md">Executive Summary</a> · <a href="https://github.com/xiule0108/china-green-compute-research/releases/latest">下载 / Download</a>
</p>

# 中国绿色算力全球化交付体系与国际价值重构：全球 AI 推理分工演进下，能源禀赋、物理通道、主权治理与商业闭环的全景研究（2026）（开放研究包）

**英文题名（Official English Title）：** *China's Green Compute Global Delivery System and International Value Restructuring*  
**研究与发布机构（Rights Holder & Institution）：** 介子九维（JIEZIJIUWEI）  
**数据与政策基准日（Baseline Cutoff Date）：** 2026年10月15日 ｜ **开放研究包整理日期：** 2026年10月19日  
**语言切换（Language）：** **简体中文** ｜ [English (`README.md`)](README.md)

<p align="center">
  <a href="manuscript/zh-CN/index.md"><img src="assets/report-cover.png" alt="中国绿色算力全球化交付体系与国际价值重构 · 介子九维独立版封面" width="520"></a>
</p>

> **快速阅读入口：** [完整中文报告手稿总目录（`manuscript/zh-CN/index.md`）](manuscript/zh-CN/index.md) ｜ [中文执行摘要](manuscript/zh-CN/executive-summary.md) ｜ [English Executive Summary](manuscript/en/executive-summary.md) ｜ [English Manuscript Index](manuscript/en/index.md) ｜ [复现指南](docs/zh-CN/reproduction-guide.md) ｜ [定量方法与边界说明](docs/zh-CN/methods-and-boundaries.md) ｜ [数据目录与来源索引](docs/zh-CN/data-and-sources.md) ｜ [分层许可声明](LICENSES/LICENSE-SCOPE.md)

---

## 一、研究对象与开放研究包范围

本仓库是 **介子九维（JIEZIJIUWEI）** 旗舰研究报告《**中国绿色算力全球化交付体系与国际价值重构**》（副标题：*全球 AI 推理分工演进下，能源禀赋、物理通道、主权治理与商业闭环的全景研究（2026）*）的完整本地开放研究包。详细研究结论、核心发现提要（`01`–`06`）与跨章节论证请直接阅读[《中文执行摘要》](manuscript/zh-CN/executive-summary.md)、[*English Executive Summary*](manuscript/en/executive-summary.md)及[《完整中文报告手稿总目录》](manuscript/zh-CN/index.md)。本包采用原生 GitHub Flavored Markdown（GFM）与结构化 CSV、JSON、Python 组织，包含以下核心部分：

1. **完整 12 章中文报告手稿（[`manuscript/zh-CN/`](manuscript/zh-CN/index.md)）**：涵盖前置声明与研究方法、执行摘要、第一篇至第六篇共 12 章（54 节）、98 项图表（55 张数据可视化统计图 + 43 张内嵌结构化 GFM 表格）、12 个专题专栏、14 条方法论尾注（`[i]`–`[xiv]`）与 126 条正式参考文献（`[1]`–`[126]`）。
2. **完整英文执行摘要与章节导航（[`manuscript/en/`](manuscript/en/index.md)）**：提供英文执行摘要全文（[`manuscript/en/executive-summary.md`](manuscript/en/executive-summary.md)，含核心结论 `01`–`06` 与 `ES.1`–`ES.3`）及 12 章中英对照导航索引。
3. **76 张目录登记 CSV 数据表与 43 张正文内嵌表快照（[`data/`](data/metadata/data_catalog.csv)）**：[`data/metadata/data_catalog.csv`](data/metadata/data_catalog.csv) 共登记 **76 张** CSV 表，包含 [`data/processed/`](data/metadata/data_catalog.csv) 下的 **59 张**整理研究数据表（58 张 `processed_reference` 专题表 + 1 张公式参考表 `TBL-071_测算公式与适用范围.csv`）和 [`data/models/`](data/metadata/model_provenance.csv) 下的 **17 张**可复现模型输出表（`reported_model_snapshot`）。此外，[`data/exhibits/`](data/metadata/report_table_registry.json) 提供正文中 **43 张**内嵌结构化表格的独立 CSV 快照（`exhibit-es-3.csv` 至 `exhibit-12-9.csv`）。
4. **完全参数化的 Python 建模与制图代码（[`src/`](src/models_engineering.py) 与 [`tools/`](tools/reproduce.py)）**：全部 17 张模型表与 56 组图像（`.png` 350 DPI 与 `.svg` 同级存放于 `figures/`）均由 `src/models_engineering.py`、`src/models_analytics.py` 与 `src/render_figures.py` 生成，运行时参数集中在 `data/parameters/` 下的 4 个 JSON 文件中。

---

<details>
<summary><strong>二、仓库真实目录结构（Repository Structure）</strong></summary>

```text
china-green-compute-research/
├── README.md                          # 英文主说明文档（Root English README）
├── README.zh-CN.md                    # 中文主说明文档（Root Chinese README）
├── CITATION.cff                       # 标准学术引用元数据（CFF 1.2.0 Schema 校验通过）
├── LICENSE                            # 顶层分层许可入口说明
├── requirements.txt                   # Python 科学计算与制图依赖声明
├── manifest.csv                       # 包内全文件清单（path, bytes, sha256 三列校验表）
├── LICENSES/                          # 分层开源与知识共享许可证全文
│   ├── MIT.txt                        # 代码许可证（适用于 src/ 与 tools/）
│   ├── CC-BY-NC-4.0.txt               # 原创文本、整理数据与自制图表许可证
│   ├── CC-BY-NC-SA-4.0.txt            # IEA 2026 附录 A 衍生数据表与序列许可证
│   └── LICENSE-SCOPE.md               # 逐层授权边界与署名规范说明
├── manuscript/                        # 报告手稿（原生 GitHub Flavored Markdown）
│   ├── zh-CN/                         # 完整中文手稿（17 个文件：12章正文 + 5个前后置与索引文件）
│   │   ├── index.md                   # 中文总目录、阅读顺序、98项图表与12个专栏索引
│   │   ├── front-matter-and-methodology.md  # 前置声明与六项核心研究方法准则
│   │   ├── executive-summary.md       # 中文执行摘要（含核心结论 01–06 及 ES.1–ES.3）
│   │   ├── chapter-01.md .. chapter-12.md   # 第1章至第12章完整正文（12个文件，54节，内嵌43张GFM表）
│   │   ├── notes.md                   # 方法论与统计口径尾注汇编（[i]–[xiv]）
│   │   └── references.md              # 正式参考文献列表（[1]–[126]）及跨库映射
│   └── en/                            # 英文手稿组件（2 个文件）
│       ├── index.md                   # 英文手稿导航与 12 章对照索引
│       └── executive-summary.md       # 完整英文执行摘要（Full English Executive Summary）
├── docs/                              # 双语技术与数据说明文档
│   ├── tested_environment.json        # 已验证本地运行环境与精确依赖版本快照
│   ├── zh-CN/
│   │   ├── reproduction-guide.md      # 中文复现指南
│   │   ├── methods-and-boundaries.md  # 中文定量方法、参数溯源与适用边界说明
│   │   └── data-and-sources.md        # 中文数据表总目录、来源映射与图表溯源说明
│   └── en/
│       ├── reproduction-guide.md      # English Reproduction Guide
│       ├── methods-and-boundaries.md  # English Quantitative Methods & Boundaries
│       └── data-and-sources.md        # English Data Catalog & Source Crosswalk
├── data/                              # 结构化数据、模型输出、正文表快照、参数与元数据
│   ├── processed/                     # 59 张整理研究数据表（TBL-001 至 TBL-071，含1张公式参考表）
│   ├── models/                        # 17 张可复现定量模型输出 CSV 表（M01–M07, O01, M01B–M07B, M06MC）
│   ├── exhibits/                      # 43 张报告正文内嵌表格的独立 CSV 快照（exhibit-es-3 至 exhibit-12-9）
│   ├── parameters/                    # 4 个集中式参数 JSON 文件
│   │   ├── engineering_inputs.json    # M01–M07 工程与 TEA 模型输入参数
│   │   ├── analytics_inputs.json      # O01, M01B–M07B 分析模型输入参数
│   │   ├── monte_carlo_2030_scenarios.json  # M06MC 2030 三情景三角分布与固定参数
│   │   └── figure_inputs.json         # 56 组统计图表的结构化绘图输入参数
│   └── metadata/                      # 12 个机器可读注册表与溯源清单
│       ├── data_catalog.csv           # 76 张数据表总目录（59 processed + 17 models）
│       ├── model_provenance.csv       # 17 张模型表的脚本、函数、来源支持/上游表、参数文件与随机种子映射
│       ├── parameter_groups.csv       # 117 个参数组级溯源表
│       ├── model_input_sources.csv    # 726 个参数叶节点级状态与来源映射表
│       ├── code_constants.csv         # 2,662 个 AST 代码常量分类扫描表
│       ├── exhibit_code_map.csv       # 98 项正文图表（55图 + 43表）与文件/代码映射表
│       ├── figure_catalog.csv         # 56 组图像（55张统计图 + 封面图 cover_hero）完整清单
│       ├── figure_source_registry.json# 55 张正文编号统计图的生成函数、支持表与图注注册表
│       ├── report_table_registry.json # 43 张正文内嵌表快照的行数、列数与来源注册表
│       ├── report_references.csv      # 126 条正式参考文献与调研来源库（Cxx-Sxxx）跨库映射表
│       ├── fact_register.csv          # 分章结构化事实与证据等级登记表
│       └── gpu_sample_verification.csv# M06C 25 条云 GPU 样本逐项价格与硬件特征核验表
├── figures/                           # 56 组统计图与封面主视觉（同名 .png 350 DPI 与 .svg 同级存放）
├── references/                        # 原始调研来源登记与上游权利说明
│   ├── references.csv                 # 347 条分章调研来源目录（C01-S001 至 C12-S015）
│   └── upstream_rights.csv            # 逐来源版权、许可证与重分发条件核查表
├── src/                               # 核心建模与制图源代码
│   ├── models_engineering.py          # 生成 M01–M07（7 张工程、TEA、Sobol、LMDI、DVA 与反弹模型表）
│   ├── models_analytics.py            # 生成 O01、M01B–M07B、M06MC（10 张高级计量、优化、拓扑与蒙特卡洛表）
│   ├── render_figures.py              # 生成 figures/ 下的全部 56 组 .png（350 DPI）与 .svg 图像
│   └── release_io.py                  # 路径解析、参数加载与确定性输出辅助模块
└── tools/                             # 统一复现入口与包结构校验脚本
    ├── reproduce.py                   # 统一命令行复现入口（默认输出至 reproduced/models 与 reproduced/charts）
    ├── check_package.py               # 包目录结构、元数据、相对链接/锚点与 manifest.csv 校验入口
    ├── validate_research_package.py   # 底层结构、Schema 与引用完整性检查实现
    └── build_manifest.py              # 重新生成 manifest.csv（path, bytes, sha256）的工具脚本
```

</details>

---

<details>
<summary><strong>三、全报告六篇十二章目录与文件导航</strong></summary>

> 章节与六篇名称严格沿用源元数据（详见 [`manuscript/zh-CN/index.md`](manuscript/zh-CN/index.md)）。

| 篇章 | 章节 | 章节标题（点击阅读中文全文） | 包含小节 | 核心内容与关联模型/数据表 |
| --- | --- | --- | --- | --- |
| **前置与导读** | 前置声明 | [前置声明与研究方法](manuscript/zh-CN/front-matter-and-methodology.md) | 六项准则 | 四维时间分列、四级证据标识（`[O]`/`[D]`/`[M]`/`[S]`）与研究独立性声明 |
| **导读与执行摘要** | ES | [执行摘要：中国绿色算力全球化交付体系与跨洋价值链重估](manuscript/zh-CN/executive-summary.md)<br>（[English Version](manuscript/en/executive-summary.md)） | `ES.1`–`ES.3` | 六大核心结论提要、图表 `ES.1`–`ES.3` |
| **第一篇：研究对象与全球需求** | 第1章 | [Token出海的概念、发展现状与统计口径](manuscript/zh-CN/chapter-01.md) | `1.1`–`1.4` | 五级物理转化链、SNA 2025 / BPM7 核算边界、WTO 14 经济体 DDS/SI2 序列（`O01`, `TBL-001`, `TBL-004`, `TBL-005`） |
| **第一篇：研究对象与全球需求** | 第2章 | [全球需求结构、目标市场与可承接空间](manuscript/zh-CN/chapter-02.md) | `2.1`–`2.4` | Prefill/Decode 负载特征、11 国官方企业 AI 调查、WTO 30 市场 SI2 进口（`TBL-006`, `TBL-008`–`TBL-010`, `TBL-012`） |
| **第二篇：中国供给与全球竞争** | 第3章 | [中国的能源、算力、模型与服务供给基础](manuscript/zh-CN/chapter-03.md) | `3.1`–`3.5` | 34 电网输配电价分项（`TBL-014`）、区域电力与算力规格（`TBL-013`, `TBL-015`–`TBL-018`）、部分识别（`M01`）、政策恒等反解（`M01B`） |
| **第二篇：中国供给与全球竞争** | 第4章 | [全球供给格局与竞争机制](manuscript/zh-CN/chapter-04.md) | `4.1`–`4.4` | 北美云厂商 CapEx、Oracle 21 款 GPU 与跨区标价、25 样本 GPU 享乐回归（`M06C`, `TBL-019`–`TBL-027`） |
| **第三篇：国际通信与跨境交付** | 第5章 | [国际通信基础设施与物理通道全景](manuscript/zh-CN/chapter-05.md) | `5.1`–`5.6` | 亚太海缆（SJC2/SEA-H2X/ADC/ALC）、跨境陆缆、四城新出入口局、HKIX/SGIX、拓扑中心性（`M07B`, `TBL-028`, `TBL-029`, `TBL-031`–`TBL-033`, `TBL-035`） |
| **第三篇：国际通信与跨境交付** | 第6章 | [从物理连接到跨境服务交付能力](manuscript/zh-CN/chapter-06.md) | `6.1`–`6.5` | 五类跨境部署（`TBL-038`）、时延匹配、30 情景 TEA（`M02`）、Brentq 临界值（`M03B`）、CVXPY 联合调度（`M04B`） |
| **第四篇：制度环境与合规治理** | 第7章 | [中国的政策方向、准入制度与试点安排](manuscript/zh-CN/chapter-07.md) | `7.1`–`7.5` | 四大政策支柱、电信与 AI 准入、网信办 16 号令、沪琼汕来数加工试点、绿电直连与绿证（`TBL-039`–`TBL-042`） |
| **第四篇：制度环境与合规治理** | 第8章 | [境外市场准入、数据安全与权利关系](manuscript/zh-CN/chapter-08.md) | `8.1`–`8.4` | 12 法域准入规则、美国 EAR §744.23 与 DOJ DSP、API 数据条款、开放权重许可证（`TBL-043`–`TBL-046`） |
| **第五篇：商业模式与区域协同** | 第9章 | [商业模式、综合经济性与价值分配](manuscript/zh-CN/chapter-09.md) | `9.1`–`9.5` | 六大商业模式、LCoT 全成本、主流 API 分档价格（`TBL-047`, `TBL-049`, `TBL-050`, `TBL-068`）、Sobol 敏感性（`M03`, `M05B`）与单因素有限差分（`M06`） |
| **第五篇：商业模式与区域协同** | 第10章 | [国内区域分工、跨区域协作与典型案例](manuscript/zh-CN/chapter-10.md) | `10.1`–`10.4` | 10 个重点区域算力项目、8 家运营商与算力上市企业 2026H1 财务及减值对照（`TBL-052`–`TBL-054`） |
| **第六篇：综合影响与行动方案** | 第11章 | [综合经济影响、关键变量与发展情景](manuscript/zh-CN/chapter-11.md) | `11.1`–`11.4` | 四模式 DVA 留存（`M05`）、IEA 2026（`TBL-062`, `TBL-063`）、30 省碳因子泰尔熵（`M06B`, `TBL-055`–`TBL-064`）、LMDI（`M04`, `M02B`）、2030 蒙特卡洛（`M06MC`） |
| **第六篇：综合影响与行动方案** | 第12章 | [中国Token出海的发展路径与行动建议](manuscript/zh-CN/chapter-12.md) | `12.1`–`12.4` | 国家制度建设、工信部 17 个区域算力互联互通节点、13 项地方算力券/Token 券（`TBL-065`–`TBL-067`）、四阶段路线图 |
| **后置附录** | 尾注与文献 | [尾注汇编（`notes.md`）](manuscript/zh-CN/notes.md) ｜ [正式参考文献（`references.md`）](manuscript/zh-CN/references.md) | `[i]`–`[xiv]`<br>`[1]`–`[126]` | 14 条方法论注释与 126 条正式文献（映射见 `data/metadata/report_references.csv`） |

</details>

---

## 四、快速复现与包完整性核验（Quick Start）

### 1. 已验证运行环境说明

本包在既有本地科学计算环境下完成两次独立复算验证，实测环境与精确版本快照记录于 [`docs/tested_environment.json`](docs/tested_environment.json)：
- **操作系统与解释器**：macOS（`Darwin 25.3.0 arm64`），Python **`3.14.5`**
- **核心依赖版本**：`numpy==2.4.3`, `pandas==3.0.3`, `scipy==1.18.0`, `cvxpy==1.9.3`, `scs==3.3.1`, `duckdb==1.5.4`, `networkx==3.7`, `pandera==0.34.1`, `SALib==1.6.0`, `statsmodels==0.15.0`, `matplotlib==3.11.2`（依赖声明见根目录 [`requirements.txt`](requirements.txt)，已验证精确版本见 [`docs/tested_environment.json`](docs/tested_environment.json)）。
- **环境边界说明**：上述验证系在既有本地环境下执行，未在全新隔离环境或更低版本 Python 下逐一实测安装，不对未测试环境作跨版本兼容性承诺。

### 2. 重新运行全部 17 个定量模型与 56 组图表

```bash
# 同时复算 17 张模型 CSV 表并重绘 56 组图表（默认输出至 reproduced/models/ 与 reproduced/charts/）
python3 tools/reproduce.py --models --figures

# 仅复算 17 张模型 CSV 表（输出至指定目录）
python3 tools/reproduce.py --models --output-dir reproduced_models_only
```

- **默认输出路径**：`tools/reproduce.py` 默认将复算结果写入 `reproduced/models/`（17 张 CSV）与 `reproduced/charts/`（56 组同名 `.png` 与 `.svg` 同级存放），不会覆盖 `data/models/` 与 `figures/` 下的正式发布快照。
- **实测运行耗时**：在本机验证环境中，首次全量运行 `--models --figures` 耗时 **`33.33` 秒**（其中 `models_engineering.py` `1.42` 秒、`models_analytics.py` `4.65` 秒、`render_figures.py` `27.19` 秒）；第二次独立运行 `--models` 耗时 **`2.97` 秒**（`0.79` 秒 + `2.14` 秒）。两次运行生成的 17 张 CSV 与 56 张 PNG 均与包内已发布文件逐字节一致。

### 3. 运行包结构、元数据与文件哈希校验器

```bash
python3 tools/check_package.py
```

- **校验范围说明**：`tools/check_package.py` 是静态包结构与元数据验证器（**该命令本身不重新运行 17 个数值模型**），负责核验必需目录与文件存在性、JSON/CSV 格式合法性、Markdown 内部相对链接与标题/显式锚点可达性、98 项正文图表与 43 张内嵌表注册一致性、本机绝对路径与内部工作区词条残留清零，以及 [`manifest.csv`](manifest.csv)（包含 `path,bytes,sha256` 三列）的字节数与 SHA-256 校验和一致性。

---

## 五、引用格式与分层许可证（Citation & Licensing）

- **学术与行业引用**：标准机器可读引用信息见 [`CITATION.cff`](CITATION.cff)。引用时请同时注明报告机构（**介子九维 JIEZIJIUWEI**）、报告正式题名《**中国绿色算力全球化交付体系与国际价值重构**》（*China's Green Compute Global Delivery System and International Value Restructuring*）、版本日期（`2026-10-19`）及具体使用的表/图编号与原始来源。
- **分层许可安排（详见 [`LICENSES/LICENSE-SCOPE.md`](LICENSES/LICENSE-SCOPE.md) 与 [`LICENSE`](LICENSE)）**：
  - `src/` 与 `tools/` 下的原创代码适用 **[MIT License](LICENSES/MIT.txt)**；
  - `manuscript/`、`figures/`、`data/parameters/`、`data/metadata/` 与 `docs/` 中由介子九维（JIEZIJIUWEI）原创的部分适用 **[CC BY-NC 4.0](LICENSES/CC-BY-NC-4.0.txt)**；
  - 源自或改编自 IEA《Key Questions on Energy and AI》（2026）附录 A 的数据表与模型序列（含 `TBL-062`、`TBL-063`、`M04`、`M01B`、`M02B` 及图 `chart_11_4`、`chart_11_1b_lmdi` 的对应部分）适用 **[CC BY-NC-SA 4.0](LICENSES/CC-BY-NC-SA-4.0.txt)**；
  - 第三方原始事实、引用与商标权利由各原始权利人保留（逐来源核查见 [`references/upstream_rights.csv`](references/upstream_rights.csv)）。

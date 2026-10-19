# Data Catalog, Source Crosswalk & Figure Provenance

> **Navigation:** [Root English README](../../README.md) ｜ [English Manuscript Index](../../manuscript/en/index.md) ｜ [Reproduction Guide](reproduction-guide.md) ｜ [Methods & Boundaries](methods-and-boundaries.md) ｜ [中文版数据与来源说明](../zh-CN/data-and-sources.md)

This document describes the data architecture, **76 catalogued CSV tables** (59 processed research tables + 17 model output tables), **43 inline exhibit table snapshots**, **56 figure pairs (`figure_catalog.csv`) and 55 numbered statistical charts (`figure_source_registry.json`)**, **three-tier parameter/constant provenance registries**, and the **crosswalk between the 126 formal report references and 347 research sources** for the open research package of **"China's Green Compute Global Delivery System and International Value Restructuring"** (《中国绿色算力全球化交付体系与国际价值重构》). All table IDs, file paths, row counts, and status enumerations below are generated directly from the machine-readable registries in `data/metadata/`.

---

## 1. Overview of Data & Metadata Assets

| Asset Collection | Directory & Registry | Exact Count | Identifier Scheme & Scope |
| --- | --- | --- | --- |
| **Processed Research Tables** | `data/processed/`<br>Registered in [`data/metadata/data_catalog.csv`](../../data/metadata/data_catalog.csv) | **59 tables** | Numbered `TBL-001` through `TBL-071` (gaps in numbering reflect historical consolidation; no files are missing), comprising **58** `processed_reference` tables and **1** `formula_reference` table (`TBL-071_测算公式与适用范围.csv`). |
| **Reproducible Model Output Tables** | `data/models/`<br>Registered in [`data/metadata/data_catalog.csv`](../../data/metadata/data_catalog.csv) & [`model_provenance.csv`](../../data/metadata/model_provenance.csv) | **17 tables** | Category `reported_model_snapshot` (`M01`–`M07`, `O01`, `M01B`–`M07B`, `M06MC`). Together with the 59 processed tables, they form the **76 tables** in `data_catalog.csv`. |
| **Inline Exhibit Table Snapshots** | `data/exhibits/`<br>Registered in [`data/metadata/report_table_registry.json`](../../data/metadata/report_table_registry.json) | **43 tables** | Named `exhibit-es-3.csv` through `exhibit-12-9.csv`, corresponding 1-to-1 to the 43 inline GFM tables in the manuscript (distinct from the `TBL-*` numbering system). |
| **Figures & Hero Visual** | `figures/`<br>Registered in [`data/metadata/figure_catalog.csv`](../../data/metadata/figure_catalog.csv) (56 pairs) & [`figure_source_registry.json`](../../data/metadata/figure_source_registry.json) (55 statistical charts) | **56 pairs** | **55 numbered report charts** registered in `figure_source_registry.json` + 1 cover visual (`cover_hero`), with all 56 pairs catalogued in `figure_catalog.csv` and stored as matching `.png` and `.svg` files side-by-side in `figures/`. |
| **Centralized Parameter JSONs** | `data/parameters/` | **4 files** | `engineering_inputs.json`, `analytics_inputs.json`, `monte_carlo_2030_scenarios.json`, and `figure_inputs.json`. |

---

## 2. Complete Catalog of the 59 Processed Research Tables (Exported from `data_catalog.csv`)

The table below lists all **59 processed research tables** in `data/processed/` from [`data/metadata/data_catalog.csv`](../../data/metadata/data_catalog.csv) (for the remaining **17 model output tables** in `data/models/`, see [Section 4 of the Reproduction Guide](reproduction-guide.md) and [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv)):

| Table ID (`table_id`) | Title (`title`) | Category (`category`) | Published Path (`path`) | Rows (`rows`) | Research Source IDs (`source_ids`) |
| --- | --- | --- | --- | --- | --- |
| `TBL-001` | wto_selected_markets_2019_2025 | `processed_reference` | [`data/processed/TBL-001_wto_selected_markets_2019_2025.csv`](../../data/processed/TBL-001_wto_selected_markets_2019_2025.csv) | `240` | `["C01-S002"]` |
| `TBL-004` | WTO DDS指标与覆盖字典 | `processed_reference` | [`data/processed/TBL-004_C01_WTO_DDS_indicator_dictionary.csv`](../../data/processed/TBL-004_C01_WTO_DDS_indicator_dictionary.csv) | `9` | `["C01-S002"]` |
| `TBL-005` | 业务形态—国际统计项目条件映射 | `processed_reference` | [`data/processed/TBL-005_C01_business_forms_statistical_mapping.csv`](../../data/processed/TBL-005_C01_business_forms_statistical_mapping.csv) | `12` | `["C01-S001", "C01-S008", "C01-S014"]` |
| `TBL-006` | enterprise_survey_comparison | `processed_reference` | [`data/processed/TBL-006_enterprise_survey_comparison.csv`](../../data/processed/TBL-006_enterprise_survey_comparison.csv) | `15` | `["C02-S003", "C02-S013", "C02-S014", "C02-S015", "C02-S016", "C02-S017", "C02-S018"]` |
| `TBL-008` | 土耳其企业AI行业、规模与采用障碍 | `processed_reference` | [`data/processed/TBL-008_C02_Turkiye_AI_sector_size_barriers_2025_2026.csv`](../../data/processed/TBL-008_C02_Turkiye_AI_sector_size_barriers_2025_2026.csv) | `81` | `["C02-S024"]` |
| `TBL-009` | 美国BTOS最新已归档截面 | `processed_reference` | [`data/processed/TBL-009_C02_US_BTOS_AI_latest_snapshot.csv`](../../data/processed/TBL-009_C02_US_BTOS_AI_latest_snapshot.csv) | `21` | `["C02-S013"]` |
| `TBL-010` | 美国BTOS企业AI全国/行业/规模时序 | `processed_reference` | [`data/processed/TBL-010_C02_US_BTOS_AI_time_series.csv`](../../data/processed/TBL-010_C02_US_BTOS_AI_time_series.csv) | `483` | `["C02-S013"]` |
| `TBL-012` | 五个新增市场的企业调查对照 | `processed_reference` | [`data/processed/TBL-012_C02_new_markets_enterprise_surveys.csv`](../../data/processed/TBL-012_C02_new_markets_enterprise_surveys.csv) | `95` | `["C02-S020", "C02-S021", "C02-S022", "C02-S023", "C02-S024"]` |
| `TBL-013` | 2021—2025算力基础设施序列与平台监测样本 | `processed_reference` | [`data/processed/TBL-013_compute_infrastructure_2021_2025.csv`](../../data/processed/TBL-013_compute_infrastructure_2021_2025.csv) | `18` | `["C03-S025"]` |
| `TBL-014` | 34个电网输配电价分项长表 | `processed_reference` | [`data/processed/TBL-014_electricity_tariffs_34_grids.csv`](../../data/processed/TBL-014_electricity_tariffs_34_grids.csv) | `595` | `["C03-S003"]` |
| `TBL-015` | FlashMLA 2026-09-30算子峰值与适配边界 | `processed_reference` | [`data/processed/TBL-015_flashmla_kernel_reported_metrics.csv`](../../data/processed/TBL-015_flashmla_kernel_reported_metrics.csv) | `6` | `["C03-S029"]` |
| `TBL-016` | Atlas 800I A2与HGX H100/H200/B200硬件规格指标 | `processed_reference` | [`data/processed/TBL-016_hardware_specification_metrics.csv`](../../data/processed/TBL-016_hardware_specification_metrics.csv) | `27` | `["C03-S026", "C03-S027"]` |
| `TBL-017` | MLPerf v6.1可供货closed数据中心LLM/VLM结果 | `processed_reference` | [`data/processed/TBL-017_mlperf_v61_available_llm_results.csv`](../../data/processed/TBL-017_mlperf_v61_available_llm_results.csv) | `340` | `["C03-S028"]` |
| `TBL-018` | 全国与五省区2025年电力供给/用电实数表 | `processed_reference` | [`data/processed/TBL-018_regional_electricity_2025.csv`](../../data/processed/TBL-018_regional_electricity_2025.csv) | `51` | `["C03-S019", "C03-S020", "C03-S021", "C03-S022", "C03-S023", "C03-S024"]` |
| `TBL-019` | azure_gpu_regional_prices_20261015 | `processed_reference` | [`data/processed/TBL-019_azure_gpu_regional_prices_20261015.csv`](../../data/processed/TBL-019_azure_gpu_regional_prices_20261015.csv) | `55` | `["C04-S017"]` |
| `TBL-020` | capex_comparison | `processed_reference` | [`data/processed/TBL-020_capex_comparison.csv`](../../data/processed/TBL-020_capex_comparison.csv) | `4` | `["C04-S003", "C04-S006", "C04-S011", "C04-S012", "C04-S014", "C04-S015", "C04-S020"]` |
| `TBL-021` | capex_metric_ledger | `processed_reference` | [`data/processed/TBL-021_capex_metric_ledger.csv`](../../data/processed/TBL-021_capex_metric_ledger.csv) | `23` | `["C04-S003", "C04-S005", "C04-S007", "C04-S011", "C04-S012", "C04-S014", "C04-S015", "C04-S020"]` |
| `TBL-022` | AWS三地区GPU实例按需价格与硬件规格 | `processed_reference` | [`data/processed/TBL-022_aws_gpu_prices_3_regions.csv`](../../data/processed/TBL-022_aws_gpu_prices_3_regions.csv) | `146` | `["C04-S029", "C04-S030", "C04-S031", "C04-S032", "C04-S033"]` |
| `TBL-023` | Google Iowa GPU完整VM及各折扣价格 | `processed_reference` | [`data/processed/TBL-023_google_gpu_prices_iowa.csv`](../../data/processed/TBL-023_google_gpu_prices_iowa.csv) | `28` | `["C04-S024"]` |
| `TBL-024` | Google GPU zone×机型系列支持范围 | `processed_reference` | [`data/processed/TBL-024_google_gpu_zone_families.csv`](../../data/processed/TBL-024_google_gpu_zone_families.csv) | `258` | `["C04-S025"]` |
| `TBL-025` | Oracle/AMD季度财务、现金支出与交付证据 | `processed_reference` | [`data/processed/TBL-025_oracle_amd_financial_capacity_metrics.csv`](../../data/processed/TBL-025_oracle_amd_financial_capacity_metrics.csv) | `71` | `["C04-S027", "C04-S028"]` |
| `TBL-026` | Oracle 21种GPU shape公共USD价格与规格 | `processed_reference` | [`data/processed/TBL-026_oracle_gpu_prices_usd.csv`](../../data/processed/TBL-026_oracle_gpu_prices_usd.csv) | `21` | `["C04-S022", "C04-S023", "C04-S034"]` |
| `TBL-027` | Oracle区域、realm和可用域数量 | `processed_reference` | [`data/processed/TBL-027_oracle_regions_and_domains.csv`](../../data/processed/TBL-027_oracle_regions_and_domains.csv) | `45` | `["C04-S026"]` |
| `TBL-028` | NCP许可与统计时间线 | `processed_reference` | [`data/processed/TBL-028_NCP许可与统计时间线.csv`](../../data/processed/TBL-028_NCP许可与统计时间线.csv) | `8` | `["C05-S032", "C05-S033", "C05-S049", "C05-S050", "C05-S051", "C05-S056", "C05-S058"]` |
| `TBL-029` | 公开端口与国际通信资费 | `processed_reference` | [`data/processed/TBL-029_公开端口与国际通信资费.csv`](../../data/processed/TBL-029_公开端口与国际通信资费.csv) | `44` | `["C05-S036", "C05-S037", "C05-S040", "C05-S042"]` |
| `TBL-031` | 四城出入口进度 | `processed_reference` | [`data/processed/TBL-031_四城出入口进度.csv`](../../data/processed/TBL-031_四城出入口进度.csv) | `4` | `["C05-S002", "C05-S009", "C05-S010", "C05-S016", "C05-S017", "C05-S018", "C05-S019", "C05-S029", "C05-S030", "C05-S031"]` |
| `TBL-032` | 海缆容量与阶段 | `processed_reference` | [`data/processed/TBL-032_海缆容量与阶段.csv`](../../data/processed/TBL-032_海缆容量与阶段.csv) | `6` | `["C05-S003", "C05-S004", "C05-S005", "C05-S006", "C05-S007", "C05-S008", "C05-S021", "C05-S024", "C05-S026", "C05-S027", "C05-S028", "C05-S032", "C05-S033", "C05-S034", "C05-S035", "C05-S048", "C05-S050", "C05-S056", "C05-S058"]` |
| `TBL-033` | 维修程序与历史观测 | `processed_reference` | [`data/processed/TBL-033_维修程序与历史观测.csv`](../../data/processed/TBL-033_维修程序与历史观测.csv) | `8` | `["C05-S038", "C05-S044", "C05-S045", "C05-S052"]` |
| `TBL-035` | 陆缆走廊与缺口 | `processed_reference` | [`data/processed/TBL-035_陆缆走廊与缺口.csv`](../../data/processed/TBL-035_陆缆走廊与缺口.csv) | `7` | `["C05-S009", "C05-S010", "C05-S015", "C05-S019", "C05-S022", "C05-S023", "C05-S043", "C05-S047", "C05-S048", "C05-S054", "C05-S055"]` |
| `TBL-038` | 部署字段矩阵 | `processed_reference` | [`data/processed/TBL-038_部署字段矩阵.csv`](../../data/processed/TBL-038_部署字段矩阵.csv) | `5` | `["C06-S001", "C06-S002", "C06-S010", "C06-S013", "C06-S014"]` |
| `TBL-039` | 国内制度触发条件、材料与办理链 | `processed_reference` | [`data/processed/TBL-039_C07_制度触发条件与办理链.csv`](../../data/processed/TBL-039_C07_制度触发条件与办理链.csv) | `14` | `["C07-S006", "C07-S023", "C07-S036", "C07-S024", "C07-S025", "C07-S035", "C07-S007", "C07-S008", "C07-S030", "C07-S037", "C07-S038", "C07-S029", "C07-S012", "C07-S018", "C07-S026", "C07-S027", "C07-S014", "C07-S015", "C07-S021", "C07-S039", "C07-S017", "C07-S022", "C07-S034", "C07-S041", "C07-S042", "C07-S043"]` |
| `TBL-040` | 绿电、绿证计量与制度参数 | `processed_reference` | [`data/processed/TBL-040_C07_绿电绿证计量与制度参数.csv`](../../data/processed/TBL-040_C07_绿电绿证计量与制度参数.csv) | `13` | `["C07-S040", "C07-S041", "C07-S042", "C07-S043"]` |
| `TBL-041` | 国内试点范围与证据阶段对照 | `processed_reference` | [`data/processed/TBL-041_C07_试点范围与证据阶段.csv`](../../data/processed/TBL-041_C07_试点范围与证据阶段.csv) | `7` | `["C07-S024", "C07-S025", "C07-S035", "C07-S012", "C07-S018", "C07-S026", "C07-S027", "C07-S019", "C07-S020", "C07-S028", "C07-S032", "C07-S033"]` |
| `TBL-042` | 跨境服务税收分类与所需证据 | `processed_reference` | [`data/processed/TBL-042_C07_跨境服务税收分类参照.csv`](../../data/processed/TBL-042_C07_跨境服务税收分类参照.csv) | `5` | `["C07-S039", "C07-S021"]` |
| `TBL-043` | 开放权重模型许可条件与上游边界 | `processed_reference` | [`data/processed/TBL-043_C08_开放权重许可条件对照.csv`](../../data/processed/TBL-043_C08_开放权重许可条件对照.csv) | `4` | `["C08-S013", "C08-S014", "C08-S015", "C08-S025", "C08-S057", "C08-S058"]` |
| `TBL-044` | 三家模型API平台的数据处理与权利条款 | `processed_reference` | [`data/processed/TBL-044_C08_模型API数据处理与权利条款.csv`](../../data/processed/TBL-044_C08_模型API数据处理与权利条款.csv) | `3` | `["C08-S051", "C08-S052", "C08-S053", "C08-S054", "C08-S055", "C08-S056"]` |
| `TBL-045` | 目标市场数据规则与版本状态矩阵 | `processed_reference` | [`data/processed/TBL-045_C08_目标市场规则矩阵.csv`](../../data/processed/TBL-045_C08_目标市场规则矩阵.csv) | `12` | `["C08-S001", "C08-S002", "C08-S018", "C08-S019", "C08-S020", "C08-S021", "C08-S007", "C08-S036", "C08-S037", "C08-S022", "C08-S033", "C08-S040", "C08-S009", "C08-S039", "C08-S034", "C08-S035", "C08-S041", "C08-S031", "C08-S042", "C08-S043", "C08-S044", "C08-S045", "C08-S046", "C08-S047", "C08-S048", "C08-S049", "C08-S008"]` |
| `TBL-046` | 金融、医疗、劳动和数据处理服务规则 | `processed_reference` | [`data/processed/TBL-046_C08_行业与特定主体规则.csv`](../../data/processed/TBL-046_C08_行业与特定主体规则.csv) | `7` | `["C08-S032", "C08-S050", "C08-S043", "C08-S044"]` |
| `TBL-047` | C09_Claude_基础与缓存分档价格 | `processed_reference` | [`data/processed/TBL-047_C09_Claude_基础与缓存分档价格.csv`](../../data/processed/TBL-047_C09_Claude_基础与缓存分档价格.csv) | `21` | `["C09-S014"]` |
| `TBL-049` | C09_R2_存储请求取回费用 | `processed_reference` | [`data/processed/TBL-049_C09_R2_存储请求取回费用.csv`](../../data/processed/TBL-049_C09_R2_存储请求取回费用.csv) | `12` | `["C09-S016"]` |
| `TBL-050` | C09_Together_文本模型输入输出缓存价格 | `processed_reference` | [`data/processed/TBL-050_C09_Together_文本模型输入输出缓存价格.csv`](../../data/processed/TBL-050_C09_Together_文本模型输入输出缓存价格.csv) | `28` | `["C09-S013"]` |
| `TBL-052` | C10_君逸智算项目_投资构成预算 | `processed_reference` | [`data/processed/TBL-052_C10_君逸智算项目_投资构成预算.csv`](../../data/processed/TBL-052_C10_君逸智算项目_投资构成预算.csv) | `6` | `["C10-S018"]` |
| `TBL-053` | C10_新增区域项目_规模与阶段 | `processed_reference` | [`data/processed/TBL-053_C10_新增区域项目_规模与阶段.csv`](../../data/processed/TBL-053_C10_新增区域项目_规模与阶段.csv) | `10` | `["C10-S013", "C10-S014", "C10-S015"]` |
| `TBL-054` | C10_运营商与对照企业_财务同比 | `processed_reference` | [`data/processed/TBL-054_C10_运营商与对照企业_财务同比.csv`](../../data/processed/TBL-054_C10_运营商与对照企业_财务同比.csv) | `8` | `["C10-S016", "C10-S017"]` |
| `TBL-055` | C11_2023电力CO2因子_全国区域省级 | `processed_reference` | [`data/processed/TBL-055_C11_2023电力CO2因子_全国区域省级.csv`](../../data/processed/TBL-055_C11_2023电力CO2因子_全国区域省级.csv) | `40` | `["C11-S012", "C11-S013"]` |
| `TBL-056` | C11_2024电力生命周期碳足迹因子 | `processed_reference` | [`data/processed/TBL-056_C11_2024电力生命周期碳足迹因子.csv`](../../data/processed/TBL-056_C11_2024电力生命周期碳足迹因子.csv) | `11` | `["C11-S014", "C11-S016"]` |
| `TBL-057` | C11_2026能效论文_七类基准任务 | `processed_reference` | [`data/processed/TBL-057_C11_2026能效论文_七类基准任务.csv`](../../data/processed/TBL-057_C11_2026能效论文_七类基准任务.csv) | `7` | `["C11-S019"]` |
| `TBL-058` | C11_2026能效论文_硬件与测量边界 | `processed_reference` | [`data/processed/TBL-058_C11_2026能效论文_硬件与测量边界.csv`](../../data/processed/TBL-058_C11_2026能效论文_硬件与测量边界.csv) | `6` | `["C11-S019"]` |
| `TBL-059` | C11_Google生产推理_两种计量边界 | `processed_reference` | [`data/processed/TBL-059_C11_Google生产推理_两种计量边界.csv`](../../data/processed/TBL-059_C11_Google生产推理_两种计量边界.csv) | `10` | `["C11-S018"]` |
| `TBL-060` | C11_Mistral_生命周期与400Token边际数据 | `processed_reference` | [`data/processed/TBL-060_C11_Mistral_生命周期与400Token边际数据.csv`](../../data/processed/TBL-060_C11_Mistral_生命周期与400Token边际数据.csv) | `6` | `["C11-S021"]` |
| `TBL-061` | C11_生成式AI工作模式RCT_14项效应 | `processed_reference` | [`data/processed/TBL-061_C11_生成式AI工作模式RCT_14项效应.csv`](../../data/processed/TBL-061_C11_生成式AI工作模式RCT_14项效应.csv) | `14` | `["C11-S022"]` |
| `TBL-062` | IEA2026分地区用电 | `processed_reference` | [`data/processed/TBL-062_IEA2026_分地区用电_72行.csv`](../../data/processed/TBL-062_IEA2026_分地区用电_72行.csv) | `72` | `["C11-S001"]` |
| `TBL-063` | IEA2026原始机构情景 | `processed_reference` | [`data/processed/TBL-063_IEA2026_原始情景_11行.csv`](../../data/processed/TBL-063_IEA2026_原始情景_11行.csv) | `11` | `["C11-S001"]` |
| `TBL-064` | LBNL2026发布版_2030情景_7行 | `processed_reference` | [`data/processed/TBL-064_LBNL2026发布版_2030情景_7行.csv`](../../data/processed/TBL-064_LBNL2026发布版_2030情景_7行.csv) | `7` | `["C11-S008"]` |
| `TBL-065` | C12_地方算力券与Token券_政策条件矩阵 | `processed_reference` | [`data/processed/TBL-065_C12_地方算力券与Token券_政策条件矩阵.csv`](../../data/processed/TBL-065_C12_地方算力券与Token券_政策条件矩阵.csv) | `13` | `["C12-S011", "C12-S012", "C12-S013", "C12-S015", "C12-S016", "C12-S019", "C12-S021"]` |
| `TBL-066` | C12_宁夏算力券_预算与绩效目标 | `processed_reference` | [`data/processed/TBL-066_C12_宁夏算力券_预算与绩效目标.csv`](../../data/processed/TBL-066_C12_宁夏算力券_预算与绩效目标.csv) | `5` | `["C12-S018"]` |
| `TBL-067` | C12_烟台2026拟奖补_四笔2025智算交易 | `processed_reference` | [`data/processed/TBL-067_C12_烟台2026拟奖补_四笔2025智算交易.csv`](../../data/processed/TBL-067_C12_烟台2026拟奖补_四笔2025智算交易.csv) | `4` | `["C12-S017"]` |
| `TBL-068` | API_GPU_平台收费快照 | `processed_reference` | [`data/processed/TBL-068_API_GPU_平台收费快照.csv`](../../data/processed/TBL-068_API_GPU_平台收费快照.csv) | `24` | `["C09-S001", "C09-S002", "C09-S005", "C09-S006", "C09-S007"]` |
| `TBL-071` | 测算公式与适用范围 | `formula_reference` | [`data/processed/TBL-071_测算公式与适用范围.csv`](../../data/processed/TBL-071_测算公式与适用范围.csv) | `11` | `[]` |

---

## 3. Parameter & Code Constant Provenance (117 Groups / 726 Leaf Entries / 2,662 Constants)

[`data/metadata/`](../../data/metadata/parameter_groups.csv) provides three machine-readable provenance registries:

### 3.1 Parameter Groups Registry ([`data/metadata/parameter_groups.csv`](../../data/metadata/parameter_groups.csv))
- Catalogues **117 parameter groups** extracted across the modeling and figure-rendering scripts, linking each group to its `script`, `function`, `parameter_file`, and serialized JSON value.

### 3.2 Leaf-Level Parameter Input Sources ([`data/metadata/model_input_sources.csv`](../../data/metadata/model_input_sources.csv))
- Catalogues **726 leaf-level parameter entries** across the parameter JSON files, documenting each leaf's `value_path`, `status`, `source_ids`, and `explanation`. The exact distribution of `status` values across all 726 rows is:

| Provenance Status (`status`) | Leaf Count |
| --- | --- |
| `scenario_or_unverified_calibration` | `240` |
| `mixed_price_match_and_unverified_features` | `173` |
| `definition_or_design_choice` | `121` |
| `scenario_network_edges` | `120` |
| `mixed_disclosure_and_assumption` | `55` |
| `matched_published_estimate_and_forecast` | `16` |
| `known_source_conflict` | `1` |
| **Total** | **`726`** |

### 3.3 AST-Scanned Code Constants ([`data/metadata/code_constants.csv`](../../data/metadata/code_constants.csv))
- Catalogues **2,662 numeric and string constants** scanned via Python AST across `src/`, classified as follows:

| Constant Classification (`classification`) | Constant Count |
| --- | --- |
| `formula_constant_or_model_setting; inspect context` | `2662` |
| **Total** | **`2,662`** |

---

## 4. Crosswalk Between 126 Formal Report References and 347 Research Sources

The package maintains two complementary bibliographic registries:
1. **Chapter-Level Research Source Registry ([`references/references.csv`](../../references/references.csv) & [`references/upstream_rights.csv`](../../references/upstream_rights.csv)):** Records **347 primary research sources** (`C01-S001` through `C12-S015`) gathered during chapter-by-chapter investigation, along with source-level copyright and license boundaries in `upstream_rights.csv`.
2. **Formal Report Bibliography ([`manuscript/zh-CN/references.md`](../../manuscript/zh-CN/references.md) & [`data/metadata/report_references.csv`](../../data/metadata/report_references.csv)):** Records the **126 formal references** (`[1]` through `[126]`) cited in the report body, figure captions, and table notes.
3. **Crosswalk Rules & Coverage:**
   - Out of the 126 formal references in [`data/metadata/report_references.csv`](../../data/metadata/report_references.csv), **58 entries** are deterministically linked to `Cxx-Sxxx` IDs in `references/references.csv` via exact URL matching, normalized URL matching, or title/document-number matching.
   - The remaining **68 entries** retain their complete formal citations and public URLs in `manuscript/zh-CN/references.md` and `report_references.csv` without fabricating artificial `Cxx-Sxxx` mappings. The breakdown by `match_rule` across all 126 references is:

| Match Rule (`match_rule`) | Reference Count |
| --- | --- |
| `bibliographic_record_only` | `68` |
| `literal_url_or_title` | `58` |
| **Total** | **`126`** |

---

## 5. End-to-End Crosswalk for All 98 Exhibits (55 Figures + 43 Inline Tables)

- [`data/metadata/exhibit_code_map.csv`](../../data/metadata/exhibit_code_map.csv) maps all **98 report exhibits** (`Exhibit ES.1` through `Exhibit 12.9`) to their manuscript paths, anchor IDs, `.png`/`.svg` figure files or `data/exhibits/*.csv` snapshots, generator scripts/functions, parameter files, and supporting table IDs.
- [`data/metadata/report_table_registry.json`](../../data/metadata/report_table_registry.json) records the dimensions and headers for all 43 inline table snapshots (in `exhibit-11-5.csv`, where the two side-by-side provincial columns share identical headers in the manuscript, a `[2]` suffix is appended to the right-hand CSV header columns for column-name uniqueness while the manuscript table preserves the original display headers).

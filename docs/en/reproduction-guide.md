# Reproduction Guide

> **Navigation:** [Root English README](../../README.md) ｜ [English Manuscript Index](../../manuscript/en/index.md) ｜ [Methods & Boundaries](methods-and-boundaries.md) ｜ [Data & Sources](data-and-sources.md) ｜ [中文版复现指南](../zh-CN/reproduction-guide.md)

This guide explains how to reproduce the **17 quantitative model CSV tables** (in [`data/models/`](../../data/metadata/model_provenance.csv)), re-render the **56 figure pairs** (catalogued in [`data/metadata/figure_catalog.csv`](../../data/metadata/figure_catalog.csv), with the 55 numbered statistical charts registered in [`data/metadata/figure_source_registry.json`](../../data/metadata/figure_source_registry.json)), and run the static package validator for the open research package of **"China's Green Compute Global Delivery System and International Value Restructuring"** (《中国绿色算力全球化交付体系与国际价值重构》).

---

## 1. Tested Runtime Environment & Dependencies

Two independent reproduction runs were executed in a pre-existing local scientific Python environment documented in [`docs/tested_environment.json`](../tested_environment.json):

| Component | Verified Specification & Exact Version | Role |
| --- | --- | --- |
| **OS & Architecture** | `macOS Darwin 25.3.0 (arm64)` | Apple Silicon local workstation |
| **Python Interpreter** | `Python 3.14.5` | Tested in an existing local environment (fresh clean installs or older Python versions were not separately tested) |
| **Numerical & Tabular Core** | `numpy==2.4.3`, `pandas==3.0.3`, `scipy==1.18.0` | Array math, CSV processing, and SciPy `brentq` root-finding |
| **Convex Optimization** | `cvxpy==1.9.3`, `scs==3.3.1` | Solves the 24-variable nonnegative convex QP in `M04B` |
| **Sensitivity & Econometrics** | `SALib==1.6.0`, `statsmodels==0.15.0` | Saltelli Sobol sampling (`M05B`) and OLS hedonic regression (`M06C`) |
| **Graph & Data Validation** | `networkx==3.7`, `duckdb==1.5.4`, `pandera==0.34.1` | Cable topology centrality (`M07B`), SQL aggregation, and DataFrame checks |
| **Visualization** | `matplotlib==3.11.2` | Renders all 56 `.png` (350 DPI) and `.svg` vector figure pairs in `src/render_figures.py` |

- **Dependency Manifests:** Direct package requirements are listed in root [`requirements.txt`](../../requirements.txt), and exact verified versions from the tested environment are recorded in [`docs/tested_environment.json`](../tested_environment.json).

---

## 2. Command-Line Reproduction & Measured Runtime

The unified reproduction entry point is [`tools/reproduce.py`](../../tools/reproduce.py):

```bash
# 1. Re-run all 17 model CSV tables and re-render all 56 figure pairs (writes to reproduced/ by default)
python3 tools/reproduce.py --models --figures

# 2. Re-run only the 17 quantitative models into a custom output directory
python3 tools/reproduce.py --models --output-dir reproduced_run2

# 3. Re-render only the 56 figure pairs (PNG + SVG)
python3 tools/reproduce.py --figures --output-dir reproduced_charts
```

### 1. Default Output Directory Structure

When `--output-dir` is omitted, `tools/reproduce.py` writes outputs to `reproduced/` (leaving the published snapshots in `data/models/` and `figures/` untouched):
- **`reproduced/models/`**: Contains the 17 regenerated model CSV tables plus `ontology_scientific_analytics_summary.json` (which stores Lagrangian dual shadow prices under `model4_cvxpy_dual_shadow_prices` for `M04B`, Theil decomposition summaries for `M06B`, and OLS diagnostic statistics for `M06C`).
- **`reproduced/charts/`**: Contains the 56 regenerated `.png` (350 DPI) and `.svg` files stored side-by-side in `reproduced/charts/` (no `png/` or `svg/` subdirectories).

### 2. Measured Execution Time & Byte-for-Byte Determinism

Across two independent verification runs on the tested machine:
- **Run 1 (`--models --figures`):** Completed in **`33.33` seconds** total (`src/models_engineering.py`: **`1.42s`**, `src/models_analytics.py`: **`4.65s`**, `src/render_figures.py`: **`27.19s`**).
- **Run 2 (`--models` only):** Completed in **`2.97` seconds** total (`src/models_engineering.py`: **`0.79s`**, `src/models_analytics.py`: **`2.14s`**).
- **Determinism:** All **17 regenerated model CSV files** matched the published files in `data/models/` **byte-for-byte (100% identical SHA-256 hashes)** across both runs, and all **56 regenerated PNG files** matched the published files in `figures/` byte-for-byte. (Third-party runs on different operating systems, CPU architectures, or font configurations may exhibit different wall-clock times or minor raster font differences.)

---

## 3. Runtime Data Flow & Parameter Provenance Architecture

It is important to distinguish between **direct runtime file reads** executed by the Python scripts and **upstream source support relationships** recorded in metadata registries:

1. **4 Centralized JSON Parameter Files (`data/parameters/`):**
   - [`data/parameters/engineering_inputs.json`](../../data/parameters/engineering_inputs.json): Read by [`src/models_engineering.py`](../../src/models_engineering.py) (`M01`–`M07`).
   - [`data/parameters/analytics_inputs.json`](../../data/parameters/analytics_inputs.json): Read by [`src/models_analytics.py`](../../src/models_analytics.py) (`O01`, `M01B`–`M07B`).
   - [`data/parameters/monte_carlo_2030_scenarios.json`](../../data/parameters/monte_carlo_2030_scenarios.json): Read by `run_model8_2030_three_scenarios_monte_carlo` in `src/models_analytics.py` (`M06MC`).
   - [`data/parameters/figure_inputs.json`](../../data/parameters/figure_inputs.json): Read by [`src/render_figures.py`](../../src/render_figures.py) to render all 56 figure pairs.
2. **Distinguishing Runtime CSV Reads vs. Upstream Supporting Tables in `model_provenance.csv`:**
   - In [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv), `input_table_ids` and `input_files` document both **upstream supporting research tables** and **runtime parameter inputs**.
   - **Models that directly read CSV files at runtime:** `M03B` and `M04B` read the upstream model output `data/models/M02_24加6情景交付成本与临界利用率矩阵.csv` at runtime; `M06B` directly reads `data/processed/TBL-055_C11_2023电力CO2因子_全国区域省级.csv`; the function generating `M06C` reads `TBL-026_oracle_gpu_prices_usd.csv` for preprocessing (while the 25 regression samples themselves come from `analytics_inputs.json`, and the other vendor pricing tables listed in `input_table_ids` serve as sample verification supporting tables); and `O01` creates DuckDB views over the catalogued CSVs and queries `TBL-001_wto_selected_markets_2019_2025.csv`.
   - **Models computed directly from frozen JSON parameters at runtime:** For `M01`, `M04`, `M01B`, `M02B`, `M07B`, and `M06MC`, the `TBL-*` tables listed in `model_provenance.csv` (e.g., `TBL-053;TBL-054`, `TBL-062`, `TBL-018`, `TBL-031;TBL-032;TBL-035`, `TBL-064`) record the **upstream source support tables** from which parameter values were calibrated, whereas the Python functions compute outputs directly from the frozen parameters in `data/parameters/*.json` without parsing those `TBL-*` CSV files at runtime.
   - Similarly, `supporting_table_ids` in [`data/metadata/figure_source_registry.json`](../../data/metadata/figure_source_registry.json) records the **research source support relationship** for each chart, while `src/render_figures.py` reads plotting series directly from `data/parameters/figure_inputs.json`.
3. **Three-Tier Parameter & Constant Provenance Registries (`data/metadata/`):**
   - [`data/metadata/parameter_groups.csv`](../../data/metadata/parameter_groups.csv): Catalogues **117 parameter groups** across the modeling and plotting scripts.
   - [`data/metadata/model_input_sources.csv`](../../data/metadata/model_input_sources.csv): Catalogues **726 leaf-level parameter entries**, recording their JSON value paths, values, provenance status (`status`), and source IDs (`source_ids`).
   - [`data/metadata/code_constants.csv`](../../data/metadata/code_constants.csv): Catalogues **2,662 AST-scanned numeric/string constants** in `src/` with explicit classifications.

---

## 4. Complete 17-Model Provenance Table (from `model_provenance.csv`)

The table below reflects all 17 entries in [`data/metadata/model_provenance.csv`](../../data/metadata/model_provenance.csv):

| Model ID | Published File (`output_file`) | Script (`script`) | Function (`function`) | Rows (`rows`) | Supporting / Upstream Tables (`input_table_ids`) | Parameter JSON (`data/parameters/`) | Random Seed (`seed`) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `M01` | [`M01_工程核算与部分识别区间推算表.csv`](../../data/models/M01_工程核算与部分识别区间推算表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_engineering_partial_identification` | `5` | `TBL-053;TBL-054` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `Deterministic` |
| `M02` | [`M02_24加6情景交付成本与临界利用率矩阵.csv`](../../data/models/M02_24加6情景交付成本与临界利用率矩阵.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_24_plus_6_tea_and_thresholds` | `30` | `— (JSON parameters only)` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `Deterministic` |
| `M03` | [`M03_Sobol全局方差敏感性指数表.csv`](../../data/models/M03_Sobol全局方差敏感性指数表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `6` | `— (JSON parameters only)` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `20261015` |
| `M04` | [`M04_LMDI算力电力增长结构分解表.csv`](../../data/models/M04_LMDI算力电力增长结构分解表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `6` | `TBL-062` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `Deterministic` |
| `M05` | [`M05_四种出海模式国内增加值留存投入产出表.csv`](../../data/models/M05_四种出海模式国内增加值留存投入产出表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `4` | `— (JSON parameters only)` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `Deterministic` |
| `M06` | [`M06_边际改善措施影子价格与优先级排序表.csv`](../../data/models/M06_边际改善措施影子价格与优先级排序表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `6` | `— (JSON parameters only)` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `Deterministic` |
| `M07` | [`M07_算力能效反弹效应弹性矩阵表.csv`](../../data/models/M07_算力能效反弹效应弹性矩阵表.csv) | [`src/models_engineering.py`](../../src/models_engineering.py) | `run_lmdi_sobol_shadow_and_rebound` | `5` | `— (JSON parameters only)` | [`engineering_inputs.json`](../../data/parameters/engineering_inputs.json) | `Deterministic` |
| `O01` | [`O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv`](../../data/models/O01_WTO数字服务与计算机服务RCA及LMDI分解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_ontology_data_governance` | `15` | `TBL-001` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M01B` | [`M01B_跨政策隐含物理恒等式反解表.csv`](../../data/models/M01B_跨政策隐含物理恒等式反解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model1_policy_identity_inversion` | `1` | `TBL-062;TBL-018` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M02B` | [`M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv`](../../data/models/M02B_Kaya_LMDI电量与碳排五因子完全分解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model2_kaya_lmdi_decomposition` | `6` | `TBL-062;TBL-055` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M03B` | [`M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv`](../../data/models/M03B_SciPy_Brentq跨洋交付三维临界值反解表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model3_scipy_brentq_breakeven` | `24` | `M02` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M04B` | [`M04B_CVXPY跨洋算电联合调度最优分配表.csv`](../../data/models/M04B_CVXPY跨洋算电联合调度最优分配表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model4_cvxpy_convex_optimization` | `17` | `M02` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M05B` | [`M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv`](../../data/models/M05B_SALib_Sobol全局敏感性与耦合交互效应表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model5_salib_sobol_and_monte_carlo` | `6` | `— (JSON parameters only)` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `20261018` |
| `M06B` | [`M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv`](../../data/models/M06B_30省电力碳因子泰尔熵与影子碳成本衍生表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model6_sklearn_theil_pca_and_hedonic` | `30` | `TBL-055` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M06C` | [`M06C_全球云GPU实例享乐价格回归与溢价率表.csv`](../../data/models/M06C_全球云GPU实例享乐价格回归与溢价率表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model6_sklearn_theil_pca_and_hedonic` | `25` | `TBL-026;TBL-022;TBL-019;TBL-023;TBL-068` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M07B` | [`M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv`](../../data/models/M07B_NetworkX跨境海陆光缆拓扑中心性与咽喉识别表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model7_networkx_cable_topology` | `20` | `TBL-031;TBL-032;TBL-035` | [`analytics_inputs.json`](../../data/parameters/analytics_inputs.json) | `Deterministic` |
| `M06MC` | [`M06_2030三种情景蒙特卡洛仿真结果表.csv`](../../data/models/M06_2030三种情景蒙特卡洛仿真结果表.csv) | [`src/models_analytics.py`](../../src/models_analytics.py) | `run_model8_2030_three_scenarios_monte_carlo` | `3` | `TBL-062;TBL-064` | [`monte_carlo_2030_scenarios.json`](../../data/parameters/monte_carlo_2030_scenarios.json) | `20261015` |

---

## 5. Static Package Structure & Integrity Verification (`tools/check_package.py`)

To verify structural completeness, metadata alignment, internal links, and file checksums, run [`tools/check_package.py`](../../tools/check_package.py):

```bash
python3 tools/check_package.py
```

- **Scope of `check_package.py`:** This script is a static package validator (**it does not re-run the 17 numerical models**). It verifies:
  1. Presence of all required directories and files (`README.md`, `README.zh-CN.md`, `CITATION.cff`, `manifest.csv`, `LICENSES/`, `manuscript/`, `docs/`, `data/`, `figures/`, `references/`, `src/`, `tools/`);
  2. Exact row-count and path consistency across `data_catalog.csv` (76 tables), `model_provenance.csv` (17 tables), `report_table_registry.json` (43 exhibit tables), `figure_catalog.csv` (56 figure pairs including `cover_hero`), `figure_source_registry.json` (55 numbered statistical charts), and `exhibit_code_map.csv` (98 exhibits);
  3. 100% resolution of relative file links, image paths, and `#anchor` fragments across all Markdown files;
  4. Absence of local absolute paths (`/Users/...`) or internal workspace markers;
  5. Exact byte-size and SHA-256 hash agreement against [`manifest.csv`](../../manifest.csv) (which contains three columns: `path,bytes,sha256`).

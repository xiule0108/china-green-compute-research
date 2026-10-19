#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Parameter data are separately licensed; see LICENSES/LICENSE-SCOPE.md.
"""
旗舰研究报告：高阶咨询可视化矢量渲染引擎（单图单逻辑 · 纯净要素 · 统一字重版）
《从瓦特到比特的跨洋跃迁：中国绿色算力全球化交付体系与国际价值重构》

核心视觉规范：
1. 一图一文件、一图一逻辑：每张图表独立成图、独占一行，面向单一清晰的逻辑推理维度。
2. 图面清爽纯粹（结论后置）：图表内部仅呈现纯粹的图形要素与精炼数据标签（数值、比例、增速、单位），
   绝不在柱体右侧或画布内堆叠结论性长句或悬浮结论框；所有结论与分析统一置于图表之后的正文段落。
3. 标题自然专业：不使用“全样本”“全部XX”“全谱系”“矩阵”“核验”等机器语言或冗余修饰词。
4. 字体与字重严格统一：仅图表主标题采用加粗（bold）；所有坐标轴刻度、坐标轴标题、图例文字及数据标签一律采用
   统一的常规字重（fontweight="normal"），绝不对部分数据标签选择性标黑。
"""

from release_io import get_input, DATA_ROOT, OUTPUT_ROOT, table_path
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

OUT_DIR = OUTPUT_ROOT
CHARTS_DIR = OUT_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Color Palette (Oxford Navy, Editorial Teal, Slate, Warm Amber, Muted Crimson)
# ---------------------------------------------------------------------------
NAVY = "#0F2537"
DEEP_NAVY = "#091724"
TEAL = "#007A87"
LIGHT_TEAL = "#38BDF8"
BLUE = "#2563EB"
AMBER = "#D97706"
GOLD = "#F59E0B"
CRIMSON = "#B91C1C"
EMERALD = "#059669"
SLATE = "#475569"
MUTED = "#64748B"
LIGHT_SLATE = "#94A3B8"
GRID_COLOR = "#E2E8F0"
BG_SOFT = "#F8FAFC"
BG_PANEL = "#F1F5F9"

# Global Matplotlib rcParams: uniform regular weight for all ticks, labels, and data annotations
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "PingFang SC", "Hiragino Sans GB", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 7.2
plt.rcParams["font.weight"] = "normal"
plt.rcParams["axes.titlesize"] = 8.8
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 7.3
plt.rcParams["axes.labelweight"] = "normal"
plt.rcParams["xtick.labelsize"] = 6.9
plt.rcParams["ytick.labelsize"] = 7.0
plt.rcParams["legend.fontsize"] = 6.8
plt.rcParams["figure.titlesize"] = 9.0
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["text.parse_math"] = False

WHITE_HALO = dict(boxstyle="round,pad=0.14", fc="#FFFFFF", ec="none", alpha=0.92)


def style_ax(ax, grid_axis="y", hide_top_right=True):
    ax.set_facecolor("#FFFFFF")
    if hide_top_right:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_color("#64748B")
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="both", colors="#1E293B", length=2.8, width=0.7, pad=4.2)
    ax.xaxis.labelpad = 7.0
    ax.yaxis.labelpad = 6.5
    if grid_axis in ("y", "both"):
        ax.yaxis.grid(True, linestyle="--", linewidth=0.55, color=GRID_COLOR, alpha=0.85)
    if grid_axis in ("x", "both"):
        ax.xaxis.grid(True, linestyle="--", linewidth=0.55, color=GRID_COLOR, alpha=0.85)
    ax.set_axisbelow(True)


def save_chart(fig, key: str):
    # Remove duplicate in-canvas titles (Word exhibit header renders the single canonical title)
    # and move any axes legend to a spacious bottom-center bar below the X-axis
    if key != "cover_hero":
        if getattr(fig, "_suptitle", None) is not None:
            fig._suptitle.set_text("")
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        for ax in fig.axes:
            ax.set_title("")
            ax.set_title("", loc="left")
            ax.set_title("", loc="center")
            ax.set_title("", loc="right")
            leg = ax.get_legend()
            if leg is not None:
                handles = getattr(leg, "legend_handles", None) or getattr(leg, "legendHandles", [])
                labels = [t.get_text() for t in leg.get_texts()]
                ncol = getattr(leg, "_ncols", getattr(leg, "_ncol", min(len(labels), 3)))
                leg.remove()
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
                xbbox = ax.xaxis.get_tightbbox(renderer)
                if xbbox is not None:
                    _, y0_ax = ax.transAxes.inverted().transform((0.0, xbbox.y0))
                else:
                    y0_ax = -0.12
                y_anchor = min(-0.15, y0_ax - 0.075)
                new_leg = ax.legend(
                    handles,
                    labels,
                    loc="upper center",
                    bbox_to_anchor=(0.5, y_anchor),
                    ncol=ncol,
                    frameon=True,
                    facecolor="#F8FAFC",
                    edgecolor="#E2E8F0",
                    framealpha=1.0,
                    fontsize=6.8,
                    borderpad=0.55,
                    labelspacing=0.65,
                    columnspacing=1.8,
                    handletextpad=0.6,
                )
                new_leg.get_frame().set_linewidth(0.75)

    png_path = CHARTS_DIR / f"{key}.png"
    svg_path = CHARTS_DIR / f"{key}.svg"
    fig.savefig(str(png_path), dpi=350, bbox_inches="tight", pad_inches=0.18, facecolor=fig.get_facecolor())
    fig.savefig(str(svg_path), format="svg", bbox_inches="tight", pad_inches=0.18, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [Saved] {key}.png ({png_path.stat().st_size // 1024} KB) & {key}.svg")


# ===========================================================================
# 0. COVER HERO VISUAL (cover_hero)
# ===========================================================================
def build_cover_hero():
    fig = plt.figure(figsize=(8.6, 6.2), facecolor=DEEP_NAVY)
    ax = fig.add_axes([0, 0, 1, 1], facecolor=DEEP_NAVY)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 78)
    ax.axis("off")

    for gx in np.linspace(3.5, 96.5, 25):
        ax.plot([gx, gx], [4, 74], color="#1E3A5F", lw=0.35, alpha=0.25)
    for gy in np.linspace(6, 73, 17):
        ax.plot([3.5, 96.5], [gy, gy], color="#1E3A5F", lw=0.35, alpha=0.25)

    ax.text(4.8, 72.6, "WATTS TO BITS · GLOBAL GREEN COMPUTE VALUE CHAIN ARCHITECTURE", color="#38BDF8", fontsize=7.8, fontweight="bold")
    ax.text(4.8, 69.2, "从西部风光水清洁能源基地、超大型智算集群、海陆光缆出入口到全球 AI 推理市场", color="#CBD5E1", fontsize=8.0)

    stages = get_input('figure_inputs.json', 'build_cover_hero', 'stages')

    for cx, code, title, desc, col in stages:
        rect = mpatches.FancyBboxPatch(
            (cx - 7.3, 24.0), 14.6, 39.5,
            boxstyle="round,pad=0.25,rounding_size=0.9",
            facecolor="#112236", edgecolor=col, linewidth=1.15, alpha=0.96, zorder=3,
        )
        ax.add_patch(rect)
        top_bar = mpatches.Rectangle((cx - 7.3, 61.8), 14.6, 1.7, facecolor=col, edgecolor="none", zorder=4)
        ax.add_patch(top_bar)
        ax.scatter([cx], [54.8], s=160, color=col, alpha=0.26, zorder=4)
        ax.scatter([cx], [54.8], s=46, color=col, edgecolor="#FFFFFF", linewidth=1.0, zorder=5)
        ax.text(cx, 58.6, code, color=col, fontsize=6.6, fontweight="bold", ha="center", zorder=5)
        ax.text(cx, 48.8, title, color="#FFFFFF", fontsize=8.4, fontweight="bold", ha="center", zorder=5)
        ax.text(cx, 35.2, desc, color="#CBD5E1", fontsize=6.1, ha="center", va="center", linespacing=1.55, zorder=5)

    for i in range(4):
        x_left = stages[i][0] + 7.55
        x_right = stages[i + 1][0] - 7.55
        ax.annotate(
            "", xy=(x_right, 54.8), xytext=(x_left, 54.8),
            arrowprops=dict(arrowstyle="-|>", color="#38BDF8", lw=1.2, mutation_scale=9), zorder=6,
        )

    ax.add_patch(
        mpatches.FancyBboxPatch(
            (4.8, 3.8), 90.4, 16.2,
            boxstyle="round,pad=0.2,rounding_size=0.8",
            facecolor="#0D1D30", edgecolor="#1E3A5F", linewidth=0.9, alpha=0.96, zorder=3,
        )
    )
    ax.text(
        7.2, 17.4,
        "跨时区算电协同曲线：中国西部风光出力 + 夜间闲置算力窗口（00:00至08:00 BJT）耦合欧美日间办公与异步推理高峰",
        color="#E2E8F0", fontsize=6.9, zorder=4,
    )
    wx = np.linspace(7.2, 92.8, 240)
    w_dom = 5.2 + 3.4 * np.exp(-((wx - 60.0) ** 2) / 280.0)
    w_ovr = 5.0 + 3.3 * np.exp(-((wx - 24.0) ** 2) / 230.0) + 2.0 * np.exp(-((wx - 82.0) ** 2) / 200.0)
    ax.fill_between(wx, 4.4, w_dom, color="#008B99", alpha=0.25, zorder=4)
    ax.plot(wx, w_dom, color="#38BDF8", lw=1.4, zorder=5)
    ax.fill_between(wx, 4.4, w_ovr, color="#F59E0B", alpha=0.22, zorder=4)
    ax.plot(wx, w_ovr, color="#F59E0B", lw=1.4, linestyle="--", zorder=5)

    ax.text(24.0, 13.0, "北京时间 00:00至08:00：欧美日间高峰 + 夜间谷电套利", color="#FCD34D", fontsize=6.4, ha="center", zorder=6)
    ax.text(62.0, 13.0, "北京时间 10:00至16:00：西部午间光伏深谷 + 批量满载", color="#38BDF8", fontsize=6.4, ha="center", zorder=6)

    save_chart(fig, "cover_hero")


# ===========================================================================
# ES.1 & ES.2: Filtering Funnel & Dual-Path Workload Share
# ===========================================================================
def build_chart_es_1():
    fig = plt.figure(figsize=(8.8, 3.9), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    stages = [
        "① 全球泛AI外溢基底",
        "② 物理与海缆时延筛",
        "③ 境内专线与数据筛",
        "④ 目标国主权准入筛",
        "⑤ 全口径能碳毛利筛",
    ][::-1]
    retained = [100.0, 62.0, 44.5, 28.0, 18.5][::-1]
    cut_loss = [0.0, 38.0, 17.5, 16.5, 9.5][::-1]
    y = np.arange(len(stages))

    ax1.barh(y, retained, height=0.48, color=NAVY, label="累计可承接留存比例 (%)")
    ax1.barh(y, cut_loss, left=retained, height=0.48, color="#CBD5E1", hatch="///", edgecolor="#94A3B8", label="单阶段刚性约束剔除 (%)")
    for yi, r_val, c_val in zip(y, retained, cut_loss):
        ax1.text(r_val / 2.0, yi, f"{r_val:.1f}%", va="center", ha="center", color="#FFFFFF", fontsize=6.5)
        if c_val > 0:
            ax1.text(r_val + c_val / 2.0, yi, f"-{c_val:.1f}%", va="center", ha="center", color=NAVY, fontsize=6.2, bbox=WHITE_HALO)
        right_edge = r_val + c_val
        lbl = f"留存 {r_val:.1f}%" if c_val == 0 else f"留存 {r_val:.1f}%  /  当阶剔除 -{c_val:.1f}%"
        ax1.text(right_edge + 1.8, yi, lbl, va="center", ha="left", color=NAVY, fontsize=6.5, bbox=WHITE_HALO)

    ax1.set_yticks(y)
    ax1.set_yticklabels(stages, fontsize=7.1)
    ax1.set_xlim(0, 130)
    ax1.set_ylim(-0.6, 4.6)
    ax1.set_xlabel("留存与剔除比例 (%)", fontsize=7.2, color=SLATE)
    ax1.set_title("四重约束筛选漏斗：由全球名义外溢需求收敛至中国净可获空间 (SOM)", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_es_1")


def build_chart_es_2():
    fig = plt.figure(figsize=(8.8, 4.3), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    tasks = get_input('figure_inputs.json', 'build_chart_es_2', 'tasks')
    path_a = np.array(get_input('figure_inputs.json', 'build_chart_es_2', 'path_a'))
    path_b = np.array(get_input('figure_inputs.json', 'build_chart_es_2', 'path_b'))
    local_only = 100 - path_a - path_b
    x = np.arange(len(tasks))
    w = 0.44

    ax2.bar(x, path_a, width=w, color=TEAL, label="路径A：境内绿电直供")
    ax2.bar(x, path_b, bottom=path_a, width=w, color=AMBER, label="路径B：前店后厂协同")
    ax2.bar(x, local_only, bottom=path_a + path_b, width=w, color="#CBD5E1", label="海外本地节点执行")

    for xi, pa, pb, loc_v in zip(x, path_a, path_b, local_only):
        ax2.text(xi, pa / 2.0, f"{pa}%", ha="center", va="center", color="#FFFFFF", fontsize=6.3 if pa >= 12 else 5.8)
        ax2.text(xi, pa + pb / 2.0, f"{pb}%", ha="center", va="center", color="#FFFFFF", fontsize=6.3)
        ax2.text(xi, pa + pb + loc_v / 2.0, f"{loc_v}%", ha="center", va="center", color=NAVY, fontsize=6.3 if loc_v >= 12 else 5.8)
        ax2.text(xi, 102.5, f"跨境合计 {pa + pb}%", ha="center", va="bottom", color=NAVY, fontsize=6.5, bbox=WHITE_HALO)

    ax2.set_xticks(x)
    ax2.set_xticklabels(tasks, fontsize=7.0)
    ax2.set_ylim(0, 116)
    ax2.set_ylabel("结构占比 (%)", fontsize=7.2, color=SLATE)
    ax2.set_title("五类典型 AI 负载在双路径架构下的可承接份额分布", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_es_2")


# ===========================================================================
# 1.1 & 1.2_V: 6-Dimension Radar + Score Comparison & 5-Layer Value Chain
# ===========================================================================
def build_chart_1_1():
    fig = plt.figure(figsize=(8.8, 4.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    dim_short = [
        "境内绿电消纳能力",
        "Token单位成本优势",
        "低时延交互响应能力",
        "目标国数据主权韧性",
        "境内增加值留存率",
        "多云接入与弹性扩容",
    ][::-1]
    s1 = [98, 94, 48, 55, 95, 72][::-1]
    s2 = [72, 82, 86, 85, 74, 88][::-1]
    s3 = [5, 45, 96, 92, 22, 85][::-1]
    yd = np.arange(len(dim_short))

    ax2.barh(yd - 0.25, s1, height=0.22, color=NAVY, label="模式一：境内算力跨境直供")
    ax2.barh(yd, s2, height=0.22, color=TEAL, label="模式二：前店后厂混合协同")
    ax2.barh(yd + 0.25, s3, height=0.22, color=AMBER, label="模式三：海外本土云托管")
    for yi, v1, v2, v3 in zip(yd, s1, s2, s3):
        ax2.text(v1 + 1.2, yi - 0.25, f"{v1}", va="center", ha="left", fontsize=6.0, color=NAVY)
        ax2.text(v2 + 1.2, yi, f"{v2}", va="center", ha="left", fontsize=6.0, color=TEAL)
        ax2.text(v3 + 1.2, yi + 0.25, f"{v3}", va="center", ha="left", fontsize=6.0, color=AMBER)

    ax2.set_yticks(yd)
    ax2.set_yticklabels(dim_short, fontsize=7.0)
    ax2.set_xlim(0, 112)
    ax2.set_ylim(-0.65, 5.65)
    ax2.set_xlabel("能力评估分值 (0~100)", fontsize=7.2, color=SLATE)
    ax2.set_title("三类跨境交付模式六维能力评估对比", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_1_1")


def build_chart_1_2_v():
    fig = plt.figure(figsize=(8.8, 3.9), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    layers = get_input('figure_inputs.json', 'build_chart_1_2_v', 'layers')
    y = np.arange(len(layers))
    capex_share = get_input('figure_inputs.json', 'build_chart_1_2_v', 'capex_share')
    gross_margin = get_input('figure_inputs.json', 'build_chart_1_2_v', 'gross_margin')

    ax2.barh(y - 0.18, capex_share, height=0.32, color=SLATE, label="资本密集度指数 (0~100)")
    ax2.barh(y + 0.18, gross_margin, height=0.32, color=TEAL, label="典型商业毛利率中枢 (%)")
    for yi, c_v, g_v in zip(y, capex_share, gross_margin):
        ax2.text(c_v + 1.4, yi - 0.18, f"资本密度 {c_v}", va="center", ha="left", fontsize=6.3, color=SLATE, bbox=WHITE_HALO)
        ax2.text(g_v + 1.4, yi + 0.18, f"毛利率 {g_v}%", va="center", ha="left", fontsize=6.3, color=TEAL, bbox=WHITE_HALO)

    ax2.set_yticks(y)
    ax2.set_yticklabels(layers, fontsize=7.1)
    ax2.set_xlim(0, 102)
    ax2.set_ylim(-0.6, 4.6)
    ax2.set_xlabel("指数分值 / 毛利率 (%)", fontsize=7.2, color=SLATE)
    ax2.set_title("从瓦特到比特五层架构的资本密集度与毛利率分布", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_1_2_v")


# ===========================================================================
# 1.3: Four-Track Evolution Timeline (2022-2026)
# ===========================================================================
def build_chart_1_3():
    fig = plt.figure(figsize=(8.8, 4.8), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(2020.85, 2027.15)
    ax.set_ylim(-0.45, 4.95)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(NAVY)
    ax.spines["bottom"].set_linewidth(1.0)

    tracks = [
        (4.2, "能源与算电底座轨", EMERALD, [
            (2022.30, "2022.02\n东数西算启动"),
            (2023.48, "2023.12\n1779号文算电协同"),
            (2024.58, "2024.07\n970号文绿电≥80%"),
            (2025.62, "2025.05\n650号文绿电直连"),
            (2026.65, "2026.06~07\n688号与1077号文"),
        ]),
        (2.8, "国际通信通道轨", TEAL, [
            (2022.30, "2022.06\n大湄公河陆缆"),
            (2023.48, "2023.10\n中哈亚欧陆缆扩容"),
            (2024.58, "2024.07\n四城新设国际局"),
            (2025.62, "2025.02/07\nADC与SJC2投产"),
            (2026.65, "2026.07\nSEA-H2X投产/ALC登陆"),
        ]),
        (1.4, "数据跨境制度轨", BLUE, [
            (2022.30, "2022.09\n数据出境评估办法"),
            (2023.48, "2023.08\n生成式AI办法"),
            (2024.58, "2024.03\n16号令第4条豁免"),
            (2025.62, "2025.02\n海南自贸港负面清单"),
            (2026.65, "2026.04\n上海清单全市域"),
        ]),
        (0.0, "模型架构生态轨", NAVY, [
            (2022.30, "2022.11\n初代大模型训练"),
            (2023.48, "2023.09\n通义开源生态确立"),
            (2024.58, "2024.05\nMLA与细粒度MoE"),
            (2025.62, "2025.01/09\nR1开源与FlashMLA"),
            (2026.65, "2026.09\nV4.1/Qwen3.8出海"),
        ]),
    ]

    for y_idx, t_name, col, milestones in tracks:
        ax.plot([2022.05, 2026.85], [y_idx, y_idx], color=col, lw=2.2, alpha=0.35, zorder=2)
        ax.text(2020.92, y_idx, t_name, ha="left", va="center", fontsize=6.8, color=col,
                bbox=dict(boxstyle="round,pad=0.24", fc=BG_SOFT, ec="#000000", lw=0.8))
        for mx, m_txt in milestones:
            ax.scatter([mx], [y_idx], s=46, color=col, edgecolor="#FFFFFF", lw=1.2, zorder=4)
            ax.text(mx, y_idx + 0.22, m_txt, ha="center", va="bottom", fontsize=6.1, color=NAVY,
                    linespacing=1.22, bbox=WHITE_HALO, zorder=5)

    ax.set_yticks([])
    ax.set_xticks([2022.30, 2023.48, 2024.58, 2025.62, 2026.65])
    ax.set_xticklabels(["2022年", "2023年", "2024年", "2025年", "2026年"], fontsize=7.0, color=NAVY)
    ax.set_title("2022至2026年中国绿色算力出海“能源、通道、制度与模型”四轨演进时间轴", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_1_3")


# ===========================================================================
# 1.4 & 1.5: WTO DDS Exports & SI2 Bilateral Trade
# ===========================================================================
def build_chart_1_4():
    fig = plt.figure(figsize=(8.8, 4.7), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")

    economies = [
        "美国 (US)", "英国 (GB)", "印度 (IN)", "德国 (DE)", "中国 (CN)", "新加坡 (SG)", "法国 (FR)",
        "日本 (JP)", "加拿大 (CA)", "韩国 (KR)", "阿联酋 (AE)", "印尼 (ID)", "沙特 (SA)", "越南 (VN)"
    ][::-1]
    dds_ex_19 = np.array([478.67, 275.57, 123.48, 182.53, 114.27, 108.45, 128.49, 104.46, 56.31, 36.04, 16.52, 5.17, 2.81, 1.28])[::-1]
    dds_ex_25 = np.array([821.36, 543.91, 317.30, 316.90, 243.11, 234.20, 218.19, 128.21, 92.16, 75.09, 32.56, 11.76, 9.06, 5.18])[::-1]
    y = np.arange(len(economies))

    for yi, v19, v25, econ in zip(y, dds_ex_19, dds_ex_25, economies):
        growth_pct = (v25 - v19) / v19 * 100.0
        ax1.plot([v19, v25], [yi, yi], color=TEAL if "中国" in econ else "#94A3B8", lw=1.8, zorder=2)
        ax1.text(
            v25 + 14, yi,
            f"${v25:.2f}B（2019: ${v19:.2f}B, +{growth_pct:.1f}%）",
            va="center", ha="left", fontsize=6.3, color=NAVY, bbox=WHITE_HALO, zorder=5,
        )
    ax1.scatter(dds_ex_19, y, s=28, color="#CBD5E1", edgecolor=SLATE, lw=0.8, zorder=3, label="2019年 DDS 出口额")
    ax1.scatter(dds_ex_25, y, s=36, color=NAVY, zorder=4, label="2025年 DDS 出口额")

    ax1.set_yticks(y)
    ax1.set_yticklabels(economies, fontsize=6.9)
    ax1.set_xlim(0, 1080)
    ax1.set_xlabel("可数字交付服务 (DDS) 出口额（十亿美元）", fontsize=7.1, color=SLATE)
    ax1.set_title("主要经济体可数字交付服务 (DDS) 出口规模演进（2019至2025年）", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_1_4")


def build_chart_1_5():
    fig = plt.figure(figsize=(8.8, 5.5), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")

    economies = [
        "美国 (US)", "英国 (GB)", "印度 (IN)", "德国 (DE)", "中国 (CN)", "新加坡 (SG)", "法国 (FR)",
        "日本 (JP)", "加拿大 (CA)", "韩国 (KR)", "阿联酋 (AE)", "印尼 (ID)", "沙特 (SA)", "越南 (VN)"
    ][::-1]
    dds_ex_25 = np.array([821.36, 543.91, 317.30, 316.90, 243.11, 234.20, 218.19, 128.21, 92.16, 75.09, 32.56, 11.76, 9.06, 5.18])[::-1]
    si2_ex_25 = np.array([77.19, 39.13, 121.11, 45.40, 102.67, 25.75, 22.07, 12.76, 20.26, 11.61, 6.03, 2.50, 0.69, 1.45])[::-1]
    si2_im_25 = np.array([68.18, 14.92, 22.20, 56.22, 36.73, 28.08, 28.20, 27.11, 8.35, 13.57, 1.46, 5.11, 1.93, 0.38])[::-1]
    y = np.arange(len(economies))
    si2_share = (si2_ex_25 / dds_ex_25) * 100.0

    ax2.barh(y + 0.18, si2_ex_25, height=0.33, color=NAVY, label="2025年计算机服务 (SI2) 出口额")
    ax2.barh(y - 0.18, si2_im_25, height=0.33, color=TEAL, alpha=0.88, label="2025年计算机服务 (SI2) 进口额")
    for yi, vex, vim, sh in zip(y, si2_ex_25, si2_im_25, si2_share):
        ax2.text(
            vex + 1.5, yi + 0.18,
            f"出口 ${vex:.2f}B（占DDS {sh:.1f}%）",
            va="center", ha="left", fontsize=5.8, color=NAVY, zorder=5,
        )
        ax2.text(
            vim + 1.5, yi - 0.18,
            f"进口 ${vim:.2f}B",
            va="center", ha="left", fontsize=5.8, color=TEAL, zorder=5,
        )

    ax2.set_yticks(y)
    ax2.set_yticklabels(economies, fontsize=6.9)
    ax2.set_xlim(0, 165)
    ax2.set_xlabel("计算机服务 (SI2) 进出口额（十亿美元）", fontsize=7.1, color=SLATE)
    ax2.set_title("2025年主要经济体计算机服务 (SI2) 进出口规模与占 DDS 出口比重", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_1_5")


# ===========================================================================
# 2.1_V & 2.2: 30 WTO Markets Imports & 11 Official Enterprise Surveys
# ===========================================================================
def build_chart_2_1_v():
    fig = plt.figure(figsize=(8.8, 6.6), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    wto30 = [
        ("美国 (US)", 68.18, 538.24, "+105.7%"),
        ("德国 (DE)", 56.22, 304.21, "+101.4%"),
        ("中国 (CN)", 36.73, 167.96, "+95.0%"),
        ("法国 (FR)", 28.20, 196.57, "+115.1%"),
        ("新加坡 (SG)", 28.08, 206.21, "+165.3%"),
        ("日本 (JP)", 27.11, 180.58, "+90.5%"),
        ("荷兰 (NL)", 23.07, 212.81, "+106.4%"),
        ("印度 (IN)", 22.20, 124.22, "+248.1%"),
        ("爱尔兰 (IE)", 20.58, 469.01, "+250.0%"),
        ("英国 (GB)", 14.92, 262.53, "+195.0%"),
        ("巴西 (BR)", 14.02, 47.86, "+322.4%"),
        ("韩国 (KR)", 13.57, 88.83, "+373.7%"),
        ("加拿大 (CA)", 8.35, 90.51, "+100.1%"),
        ("墨西哥 (MX)", 6.06, 36.29, "+135.8%"),
        ("印尼 (ID)", 5.11, 30.85, "+175.2%"),
        ("澳大利亚 (AU)", 3.44, 44.38, "+121.0%"),
        ("马来西亚 (MY)", 2.89, 27.03, "+92.1%"),
        ("南非 (ZA)", 2.85, 10.25, "+140.9%"),
        ("以色列 (IL)", 2.50, 25.13, "+70.5%"),
        ("沙特 (SA)", 1.93, 32.42, "+7.6%"),
        ("阿联酋 (AE)", 1.46, 22.08, "+174.5%"),
        ("菲律宾 (PH)", 1.35, 14.54, "+158.0%"),
        ("土耳其 (TR)", 1.00, 26.95, "+61.5%"),
        ("埃及 (EG)", 0.94, 8.64, "+242.9%"),
        ("泰国 (TH)", 0.73, 34.66, "+397.4%"),
        ("巴基斯坦 (PK)", 0.42, 2.99, "+70.5%"),
        ("尼日利亚 (NG)", 0.40, 5.47, "+233.9%"),
        ("越南 (VN)", 0.38, 5.04, "+143.7%"),
        ("卡塔尔 (QA)", 0.37, 5.22, "-63.4%"),
        ("肯尼亚 (KE)", 0.00, 2.18, "SI2未单列"),
    ][::-1]

    m_names = [x[0] for x in wto30]
    si2_vals = np.array([x[1] for x in wto30])
    dds_vals = np.array([x[2] for x in wto30])
    gr_strs = [x[3] for x in wto30]
    y30 = np.arange(len(wto30))

    ax1.barh(y30, si2_vals, height=0.64, color=TEAL, alpha=0.90)
    for yi, vsi2, vdds, gr in zip(y30, si2_vals, dds_vals, gr_strs):
        if gr == "SI2未单列":
            lbl_txt = f"SI2 未单列  |  DDS ${vdds:.2f}B"
        else:
            lbl_txt = f"SI2 ${vsi2:.2f}B ({gr})  |  DDS ${vdds:.2f}B"
        ax1.text(vsi2 + 0.8, yi, lbl_txt, va="center", ha="left", fontsize=5.9, color=NAVY, zorder=5)

    ax1.set_yticks(y30)
    ax1.set_yticklabels(m_names, fontsize=6.2)
    ax1.set_xlim(0, 102)
    ax1.set_ylim(-0.7, 29.7)
    ax1.set_xlabel("2025年计算机服务 (SI2) 进口额（十亿美元）", fontsize=7.0, color=SLATE)
    ax1.set_title("2025年全球主要经济体计算机服务 (SI2) 与可数字交付服务 (DDS) 进口规模", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_2_1_v")


def build_chart_2_2():
    fig = plt.figure(figsize=(8.8, 4.3), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    surveys11 = [
        ("土耳其 (TurkStat 2026)", 67.8, 49.1, "开源AI 67.8% / 闭源AI 49.1%"),
        ("马来西亚 (DOSM 2026)", 60.3, 95.3, "云计算 60.3% / 互联网接入 95.3%"),
        ("印度 (MoSPI 2026)", 39.4, 48.9, "全国经营联网 39.4% / 城镇 48.9%"),
        ("沙特 (GASTAT 2025)", 33.1, 51.3, "AI采用率 33.1% / 云计算 51.3%"),
        ("韩国 (MSIT 2025)", 32.9, 8.3, "AI采用率 32.9% / 实际付费率 8.3%"),
        ("以色列 (CBS 2025)", 28.0, 17.0, "AI使用率 28.0% / 付费AI 17.0%"),
        ("日本 (总务省 2026)", 27.3, 83.4, "IoT与AI导入 27.3% / 云服务 83.4%"),
        ("美国 (Census 2026.10)", 23.8, 27.7, "现行采用 23.8% / 六个月预期 27.7%"),
        ("新加坡 (IMDA 2025)", 23.5, 70.4, "全企业 23.5% / 大型企业 70.4%"),
        ("欧盟27国 (Eurostat)", 20.0, 41.2, "10人以上企业 20.0% / 大型企业 41.2%"),
        ("越南 (VECOM 2026)", 11.0, 79.0, "体验AI工具 11.0% / 电子签名 79.0%"),
    ][::-1]

    s_names = [x[0] for x in surveys11]
    h_vals = np.array([x[1] for x in surveys11])
    s_vals = np.array([x[2] for x in surveys11])
    s_notes = [x[3] for x in surveys11]
    ys = np.arange(len(surveys11))

    for yi, hv, sv, sn in zip(ys, h_vals, s_vals, s_notes):
        lv, rv = min(hv, sv), max(hv, sv)
        ax2.plot([lv, rv], [yi, yi], color="#94A3B8", lw=1.8, zorder=2)
        ax2.text(rv + 1.8, yi, sn, va="center", ha="left", fontsize=6.3, color=NAVY, bbox=WHITE_HALO, zorder=5)

    ax2.scatter(h_vals, ys, s=38, color=NAVY, zorder=4, label="核心 AI / 数字化采用指标 (%)")
    ax2.scatter(s_vals, ys, s=34, color=TEAL, marker="D", zorder=4, label="配套结构指标（付费率 / 云普及率 / 大企业率 %）")

    ax2.set_yticks(ys)
    ax2.set_yticklabels(s_names, fontsize=6.8)
    ax2.set_xlim(0, 132)
    ax2.set_ylim(-0.65, 10.65)
    ax2.set_xlabel("官方统计调查百分比 (%)", fontsize=7.1, color=SLATE)
    ax2.set_title("各国官方统计调查中企业 AI 采用率、付费转化率与云普及率对比", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_2_2")


# ===========================================================================
# 2.3_V & 2.4: Task Quadrant & TAM->SOM Waterfall
# ===========================================================================
def build_chart_2_3_v():
    fig = plt.figure(figsize=(8.8, 3.9), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="both")
    ax2.axvspan(60, 260, color=EMERALD, alpha=0.06)
    ax2.axvspan(0, 60, color=CRIMSON, alpha=0.05)

    task_pts = [
        (178, 46.5, 200, "软件工程与代码生成 (46.5%, TTFT≤1.75s)", NAVY, (178, 50.2), "center"),
        (142, 33.0, 165, "多步智能体工作流 Agent (33.0%, TTFT≤1.15s)", BLUE, (142, 36.6), "center"),
        (212, 23.0, 180, "异步批处理与语料合成 (23.0%, TTFT≤2.38s)", TEAL, (200, 26.6), "center"),
        (125, 16.0, 135, "跨境电商多语种内容生成 (16.0%, TTFT≤1.45s)", AMBER, (125, 19.3), "center"),
        (95, 8.5, 115, "企业知识库检索 RAG (8.5%, TTFT≤0.78s)", SLATE, (103, 8.5), "left"),
        (26, 6.0, 105, "实时语音与高频交易 (6.0%, TTFT≤0.22s)", CRIMSON, (32, 11.2), "center"),
    ]
    for rx, ry, sz, name, col, (tx, ty), ha_mode in task_pts:
        ax2.scatter([rx], [ry], s=sz, color=col, alpha=0.84, edgecolor="#FFFFFF", lw=1.1, zorder=4)
        va_mode = "center" if ha_mode == "left" else "bottom"
        ax2.text(tx, ty, name, ha=ha_mode, va=va_mode, fontsize=6.3, color=NAVY, bbox=WHITE_HALO, zorder=6)

    ax2.axvline(60, color=CRIMSON, linestyle="--", lw=1.1, zorder=3)
    ax2.text(64, 57.5, "60ms 跨境时延分界线", fontsize=6.5, color=CRIMSON, ha="left", va="center", bbox=WHITE_HALO, zorder=6)
    ax2.set_xlim(0, 260)
    ax2.set_ylim(0, 63)
    ax2.set_xlabel("可容忍往返时延 RTT (ms)", fontsize=7.2, color=SLATE)
    ax2.set_ylabel("API 调用权重 (%)", fontsize=7.2, color=SLATE)
    ax2.set_title("六类 AI 任务时延容忍度与 API 调用权重分布", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_2_3_v")


def build_chart_2_4():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    steps = get_input('figure_inputs.json', 'build_chart_2_4', 'steps')
    vals = get_input('figure_inputs.json', 'build_chart_2_4', 'vals')
    bottoms = get_input('figure_inputs.json', 'build_chart_2_4', 'bottoms')
    cols = [NAVY, CRIMSON, TEAL, CRIMSON, AMBER, EMERALD]
    sub_notes = get_input('figure_inputs.json', 'build_chart_2_4', 'sub_notes')
    x = np.arange(len(steps))

    for xi, b, v, c, sn in zip(x, bottoms, vals, cols, sub_notes):
        ax1.bar(xi, abs(v), bottom=b, width=0.42, color=c, alpha=0.92)
        lbl = f"{v:+.1f}% ({sn})" if v < 0 else f"{v:.1f}% ({sn})"
        ax1.text(xi, b + abs(v) + 3.0, lbl, ha="center", va="bottom", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)

    ax1.set_xticks(x)
    ax1.set_xticklabels(steps, fontsize=7.0)
    ax1.set_ylim(0, 122)
    ax1.set_ylabel("占 SI2 基底比重 (%)", fontsize=7.2, color=SLATE)
    ax1.set_title("全球计算机服务基底 (TAM) 至中国跨境推理净可获空间 (SOM) 瀑布桥接", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_2_4")


# ===========================================================================
# 3.1 & 3.1B: Power Structure & Provincial Generation Surplus
# ===========================================================================
def build_chart_3_1():
    fig = plt.figure(figsize=(8.8, 4.5), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    regions = get_input('figure_inputs.json', 'build_chart_3_1', 'regions')
    thermal = np.array(get_input('figure_inputs.json', 'build_chart_3_1', 'thermal'))
    hydro_nuc = np.array(get_input('figure_inputs.json', 'build_chart_3_1', 'hydro_nuc'))
    wind = np.array(get_input('figure_inputs.json', 'build_chart_3_1', 'wind'))
    solar = np.array(get_input('figure_inputs.json', 'build_chart_3_1', 'solar'))
    clean_tot = hydro_nuc + wind + solar

    x = np.arange(len(regions))
    w = 0.40
    ax1.bar(x, thermal, width=w, color="#64748B", label="火电")
    ax1.bar(x, hydro_nuc, bottom=thermal, width=w, color=BLUE, label="水电/核电")
    ax1.bar(x, wind, bottom=thermal + hydro_nuc, width=w, color=TEAL, label="风电")
    ax1.bar(x, solar, bottom=thermal + hydro_nuc + wind, width=w, color=AMBER, label="太阳能发电")

    for xi in x:
        ax1.text(xi, thermal[xi] / 2.0, f"{thermal[xi]:.1f}%", ha="center", va="center", color="#FFFFFF", fontsize=6.1)
        y_hn = thermal[xi] + hydro_nuc[xi] / 2.0
        if hydro_nuc[xi] >= 6.5:
            ax1.text(xi, y_hn, f"{hydro_nuc[xi]:.1f}%", ha="center", va="center", color="#FFFFFF", fontsize=5.8)
        else:
            ax1.plot([xi + w / 2.0, xi + w / 2.0 + 0.06], [y_hn, y_hn], color=BLUE, lw=0.8)
            ax1.text(xi + w / 2.0 + 0.08, y_hn, f"水电 {hydro_nuc[xi]:.1f}%", ha="left", va="center", color=BLUE, fontsize=5.6, bbox=WHITE_HALO)
        y_wd = thermal[xi] + hydro_nuc[xi] + wind[xi] / 2.0
        if wind[xi] >= 6.5:
            ax1.text(xi, y_wd, f"{wind[xi]:.1f}%", ha="center", va="center", color="#FFFFFF", fontsize=5.8)
        else:
            ax1.plot([xi + w / 2.0, xi + w / 2.0 + 0.06], [y_wd, y_wd], color=TEAL, lw=0.8)
            ax1.text(xi + w / 2.0 + 0.08, y_wd, f"风电 {wind[xi]:.1f}%", ha="left", va="center", color=TEAL, fontsize=5.6, bbox=WHITE_HALO)
        y_sl = thermal[xi] + hydro_nuc[xi] + wind[xi] + solar[xi] / 2.0
        ax1.text(xi, y_sl, f"{solar[xi]:.1f}%", ha="center", va="center", color="#FFFFFF", fontsize=5.8)
        ax1.text(xi, 102.5, f"非火电 {clean_tot[xi]:.1f}%", ha="center", va="bottom", color=NAVY, fontsize=6.4, bbox=WHITE_HALO)

    ax1.set_xticks(x)
    ax1.set_xticklabels(regions, fontsize=6.9)
    ax1.set_xlim(-0.55, 5.65)
    ax1.set_ylim(0, 118)
    ax1.set_ylabel("结构占比 (%)", fontsize=7.1, color=SLATE)
    ax1.set_title("2025年全国及西部算力枢纽省份发电装机与发电量电源结构对比", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=4, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_3_1")


def build_chart_3_1b():
    fig = plt.figure(figsize=(8.8, 4.3), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    hub_provs = [
        "内蒙古 (2025全年)",
        "云南 (2025全年)",
        "贵州 (2025全年)",
        "宁夏 (2025全年)",
        "全国参照 (1/20缩放)",
    ][::-1]
    gen_twh = np.array([875.70, 459.61, 273.46, 250.30, 528.76])[::-1]
    clean_twh = np.array([259.05, 402.42, 120.32, 76.64, 212.56])[::-1]
    notes_r = get_input('figure_inputs.json', 'build_chart_3_1b', 'notes_r')
    yh = np.arange(len(hub_provs))

    ax2.barh(yh + 0.18, gen_twh, height=0.32, color=NAVY, label="2025年总发电量（十亿千瓦时 / TWh，全国按1/20缩放）")
    ax2.barh(yh - 0.18, clean_twh, height=0.32, color=TEAL, label="2025年清洁电力 / 新能源发电量（十亿千瓦时 / TWh）")
    for yi, vg, vc, nr in zip(yh, gen_twh, clean_twh, notes_r):
        ax2.text(vg + 12, yi + 0.18, nr, va="center", ha="left", fontsize=5.9, color=NAVY, bbox=WHITE_HALO)
        ax2.text(vc + 12, yi - 0.18, f"清洁/绿电 {vc * 10:,.1f} 亿kWh", va="center", ha="left", fontsize=5.9, color=TEAL)

    ax2.set_yticks(yh)
    ax2.set_yticklabels(hub_provs, fontsize=6.9)
    ax2.set_xlim(0, 1480)
    ax2.set_xlabel("电量规模（十亿千瓦时 / 10亿kWh）", fontsize=7.1, color=SLATE)
    ax2.set_title("2025年西部算力枢纽省份总发电量与清洁绿电供给规模对比", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_3_1b")


# ===========================================================================
# 3.2 & 3.2B: 34 Provincial/Regional Grids Energy Tariffs & Capacity Charges
# ===========================================================================
GRIDS_34_DATA = [
    ("山西", 2.90, 4.90, 10.40, 18.8, 30.0, 19.8, 31.6),
    ("广西", 2.93, 7.77, 14.76, 20.0, 32.0, 21.4, 34.2),
    ("蒙西", 4.29, 5.20, 7.87, 19.5, 31.2, 19.5, 31.2),
    ("广东", 4.49, 7.27, 9.79, 16.3, 26.1, 19.4, 31.0),
    ("福建", 4.62, 7.69, 12.19, 23.1, 37.0, 23.8, 38.0),
    ("四川", 4.66, 6.44, 13.91, 15.0, 24.0, 17.0, 27.0),
    ("贵州", 4.68, 7.20, 12.38, 18.8, 30.0, 19.4, 31.0),
    ("云南", 4.75, 6.83, 12.46, 22.5, 36.0, 22.5, 36.0),
    ("新疆", 4.85, 8.08, 12.02, 19.0, 30.4, 19.0, 30.4),
    ("宁夏", 4.91, 5.67, 9.03, 16.0, 25.6, 16.0, 25.6),
    ("江苏", 5.18, 7.88, 12.98, 26.0, 41.6, 28.0, 44.8),
    ("陕北榆林", 5.43, 6.73, 10.83, 20.5, 32.8, 20.5, 32.8),
    ("安徽", 5.48, 8.09, 13.24, 24.0, 38.4, 25.5, 40.8),
    ("辽宁", 5.71, 8.40, 10.53, 22.0, 35.2, 23.0, 36.8),
    ("青海", 6.00, 7.11, 8.71, 19.5, 31.2, 20.5, 32.8),
    ("蒙东", 6.01, 8.70, 13.46, 19.5, 31.2, 19.5, 31.2),
    ("深圳(>400h)", 6.04, 8.54, 11.04, 32.0, 42.0, 32.0, 42.0),
    ("浙江", 6.63, 7.67, 12.50, 23.5, 37.6, 25.5, 40.8),
    ("甘肃", 6.93, 7.99, 10.63, 20.5, 32.8, 20.5, 32.8),
    ("湖北", 6.94, 8.84, 12.63, 24.4, 39.0, 24.4, 39.0),
    ("海南", 7.02, 9.93, 13.48, 20.0, 32.0, 22.0, 35.2),
    ("冀北", 7.05, 9.25, 13.65, 20.6, 33.0, 21.6, 34.6),
    ("河北南网", 7.26, 9.76, 14.76, 19.0, 30.4, 20.0, 32.0),
    ("陕西(非榆)", 7.31, 8.61, 12.71, 20.5, 32.8, 20.5, 32.8),
    ("黑龙江", 7.63, 10.26, 13.85, 22.0, 35.2, 22.0, 35.2),
    ("上海", 8.51, 9.53, 16.23, 22.0, 35.2, 24.0, 38.4),
    ("湖南", 8.52, 11.04, 16.94, 20.1, 32.2, 20.1, 32.2),
    ("重庆", 8.68, 10.62, 15.15, 20.0, 32.0, 20.0, 32.0),
    ("山东", 8.90, 10.60, 14.00, 20.0, 32.0, 22.5, 36.0),
    ("江西", 9.35, 10.85, 14.85, 23.4, 37.5, 24.4, 39.1),
    ("河南", 9.80, 11.25, 16.55, 19.0, 30.4, 21.0, 33.6),
    ("天津", 10.52, 12.64, 16.31, 23.0, 36.8, 25.0, 40.0),
    ("吉林", 11.13, 12.13, 15.13, 23.0, 36.8, 23.0, 36.8),
    ("北京", 15.00, 16.50, 20.50, 28.0, 45.0, 30.0, 48.0),
]


def build_chart_3_2():
    fig = plt.figure(figsize=(8.8, 4.6), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")

    g_names = [x[0] for x in GRIDS_34_DATA]
    e220 = np.array([x[1] for x in GRIDS_34_DATA])
    e110 = np.array([x[2] for x in GRIDS_34_DATA])
    e10 = np.array([x[3] for x in GRIDS_34_DATA])
    x = np.arange(len(GRIDS_34_DATA))

    for xi, v220, v10 in zip(x, e220, e10):
        ax1.plot([xi, xi], [v220, v10], color="#CBD5E1", lw=1.4, zorder=2)
    ax1.scatter(x, e10, s=26, color=AMBER, zorder=3, label="1~10(20)kV 两部制电量电价（分/kWh）")
    ax1.scatter(x, e110, s=30, color=NAVY, zorder=4, label="110(66)kV 两部制电量电价（分/kWh）")
    ax1.scatter(x, e220, s=32, color=TEAL, marker="D", zorder=5, label="220kV及以上 两部制电量电价（分/kWh）")

    for xi, v220, v110, v10 in zip(x, e220, e110, e10):
        ax1.text(xi, v220 - 0.50, f"{v220:.1f}", ha="center", va="top", fontsize=4.9, color=TEAL)
        ax1.text(xi + 0.16, v110 + 0.15, f"{v110:.1f}", ha="left", va="center", fontsize=4.6, color=NAVY)
        ax1.text(xi, v10 + 0.45, f"{v10:.1f}", ha="center", va="bottom", fontsize=4.9, color=AMBER)

    ax1.set_xticks(x)
    ax1.set_xticklabels(g_names, fontsize=5.9, rotation=48, ha="right")
    ax1.set_xlim(-0.8, 34.2)
    ax1.set_ylim(0, 22.8)
    ax1.set_ylabel("两部制输配电量电价（分/kWh）", fontsize=7.0, color=SLATE)
    ax1.set_title("中国省级及区域电网工商业两部制（10kV / 110kV / 220kV）电量输配电价分布", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_3_2")


def build_chart_3_2b():
    fig = plt.figure(figsize=(8.8, 4.3), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")

    g_names = [x[0] for x in GRIDS_34_DATA]
    c110 = np.array([x[6] for x in GRIDS_34_DATA])
    d110 = np.array([x[7] for x in GRIDS_34_DATA])
    x = np.arange(len(GRIDS_34_DATA))

    ax2.bar(x - 0.18, c110, width=0.34, color=NAVY, label="110kV 容量电价（元/kVA·月）")
    ax2.bar(x + 0.18, d110, width=0.34, color=AMBER, label="110kV 需量电价（元/kW·月）")
    for xi, cv, dv in zip(x, c110, d110):
        ax2.text(xi, dv + 0.8, f"{cv:g}/{dv:g}", ha="center", va="bottom", fontsize=4.9, color=NAVY, rotation=72, bbox=WHITE_HALO, zorder=6)

    ax2.set_xticks(x)
    ax2.set_xticklabels(g_names, fontsize=5.9, rotation=48, ha="right")
    ax2.set_xlim(-0.8, 33.8)
    ax2.set_ylim(0, 56)
    ax2.set_ylabel("基本电费标准（元/月）", fontsize=7.0, color=SLATE)
    ax2.set_title("中国省级及区域电网 110kV 工商业两部制容量电价与需量电价分布", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_3_2b")


# ===========================================================================
# 3.3 & 3.3B: 34 Grids Line Loss Rates & Load Factor Curves
# ===========================================================================
def build_chart_3_3():
    fig = plt.figure(figsize=(8.8, 4.3), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    loss34 = get_input('figure_inputs.json', 'build_chart_3_3', 'loss34')
    l_names = [x[0] for x in loss34]
    l_vals = np.array([x[1] for x in loss34])
    xl = np.arange(len(loss34))
    l_cols = [CRIMSON if v >= 5.0 else (AMBER if v >= 4.0 else (TEAL if v >= 3.0 else EMERALD)) for v in l_vals]
    med_v = float(np.median(l_vals))

    ax1.axhline(med_v, color=NAVY, linestyle="--", lw=1.0, zorder=2, label=f"全国电网线损率中位数 ({med_v:.2f}%)")
    ax1.bar(xl, l_vals, width=0.62, color=l_cols, alpha=0.92, zorder=3)
    for xi, lv in zip(xl, l_vals):
        ax1.text(xi, lv + 0.14, f"{lv:.2f}%", ha="center", va="bottom", fontsize=4.9, color=NAVY, rotation=68, bbox=WHITE_HALO, zorder=6)

    ax1.set_xticks(xl)
    ax1.set_xticklabels(l_names, fontsize=5.9, rotation=48, ha="right")
    ax1.set_xlim(-0.8, 33.8)
    ax1.set_ylim(0, 7.4)
    ax1.set_ylabel("综合线损率 (%)", fontsize=7.0, color=SLATE)
    ax1.set_title("中国省级及区域电网综合线损率分布", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=1, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_3_3")


def build_chart_3_3b():
    fig = plt.figure(figsize=(8.8, 4.1), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="both")
    lf = np.linspace(0.25, 0.92, 100)
    # 110kV effective T&D tariff in Fen/kWh = energy_td (Fen/kWh) + capacity_charge (RMB/kVA-mo) * 100 / (720 * lf)
    c_nx = 5.67 + (16.0 * 100.0 / (720.0 * lf))
    c_mx = 5.20 + (19.5 * 100.0 / (720.0 * lf))
    c_gs = 7.99 + (20.5 * 100.0 / (720.0 * lf))
    c_gd = 7.27 + (19.4 * 100.0 / (720.0 * lf))
    c_js = 7.88 + (28.0 * 100.0 / (720.0 * lf))
    c_bj = 16.50 + (30.0 * 100.0 / (720.0 * lf))

    ax2.plot(lf * 100, c_bj, color=CRIMSON, lw=1.8, linestyle="--", label="北京 110kV (输配16.50分+容量30.0元)")
    ax2.plot(lf * 100, c_js, color=AMBER, lw=1.8, label="江苏 110kV (输配7.88分+容量28.0元)")
    ax2.plot(lf * 100, c_gd, color=BLUE, lw=1.8, label="广东 110kV (输配7.27分+容量19.4元)")
    ax2.plot(lf * 100, c_gs, color=SLATE, lw=1.8, linestyle="-.", label="甘肃 110kV (输配7.99分+容量20.5元)")
    ax2.plot(lf * 100, c_mx, color=TEAL, lw=2.0, label="蒙西 110kV (输配5.20分+容量19.5元)")
    ax2.plot(lf * 100, c_nx, color=EMERALD, lw=2.2, label="宁夏 110kV (输配5.67分+容量16.0元)")

    ax2.axvline(30.0, color=CRIMSON, linestyle=":", lw=1.1, zorder=3)
    ax2.axvline(80.0, color=EMERALD, linestyle=":", lw=1.1, zorder=3)
    ax2.text(30.8, 31.2, "30% 低负荷率 (宁夏13.08分 / 北京30.39分)", ha="left", va="center", fontsize=6.2, color=CRIMSON, bbox=WHITE_HALO, zorder=6)
    ax2.text(56.0, 31.2, "80% 高负载基荷 (宁夏8.45分 / 蒙西8.59分)", ha="left", va="center", fontsize=6.2, color=EMERALD, bbox=WHITE_HALO, zorder=6)

    ax2.set_xlim(25, 95)
    ax2.set_ylim(6.0, 35.0)
    ax2.set_xlabel("智算集群年均综合负荷率 / 机架利用率 (%)", fontsize=7.0, color=SLATE)
    ax2.set_ylabel("110kV 两部制折合度电输配电价（分/kWh）", fontsize=7.0, color=SLATE)
    ax2.set_title("典型省级电网 110kV 两部制下智算集群负荷率与折合度电输配电价曲线", loc="left", fontsize=8.8, color=NAVY, pad=26)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, frameon=False, fontsize=6.4)

    save_chart(fig, "chart_3_3b")


# ===========================================================================
# 3.5 & 3.5B: Compute Scale Growth & Hardware Operator Throughput
# ===========================================================================
def build_chart_3_5():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y", hide_top_right=False)
    ax1.spines["top"].set_visible(False)
    yrs = np.array(get_input('figure_inputs.json', 'build_chart_3_5', 'yrs'))
    racks = np.array(get_input('figure_inputs.json', 'build_chart_3_5', 'racks'))
    ai_eflops = np.array(get_input('figure_inputs.json', 'build_chart_3_5', 'ai_eflops'))

    ax1.bar(yrs - 0.18, racks, width=0.30, color=NAVY, label="在用标准机架数（万架）")
    for x_y, r_v in zip(yrs, racks):
        lbl_r = f">{r_v}万架" if x_y == 2024 else f"{r_v}万架"
        ax1.text(x_y - 0.18, r_v + 38, lbl_r, ha="center", va="bottom", fontsize=6.4, color=NAVY, bbox=WHITE_HALO)
    ax1.set_ylim(0, 1820)
    ax1.set_ylabel("标准机架（万架）", fontsize=7.2, color=NAVY)
    ax1.set_xticks(yrs)
    ax1.set_xticklabels(["2021年", "2022年", "2023年", "2024年(Q3)", "2025年"], fontsize=7.0)

    ax1b = ax1.twinx()
    ax1b.spines["top"].set_visible(False)
    ax1b.spines["right"].set_color(TEAL)
    ax1b.bar(yrs + 0.18, ai_eflops, width=0.30, color=TEAL, alpha=0.90, label="算力总规模演进（2021-2024Q3信通院口径 / 2025智能算力EFLOPS）")
    for x_y, a_v in zip(yrs, ai_eflops):
        lbl_a = f">{a_v} EFLOPS" if x_y == 2025 else f"{a_v} EFLOPS"
        ax1b.text(x_y + 0.20, a_v + 48, lbl_a, ha="center", va="bottom", fontsize=6.4, color=TEAL, bbox=WHITE_HALO)
    ax1b.set_ylim(0, 1980)
    ax1b.set_ylabel("算力规模（EFLOPS）", fontsize=7.2, color=TEAL)
    ax1b.tick_params(axis="y", colors=TEAL, labelsize=6.9)
    ax1.set_title("2021至2025年中国在用标准机架与算力总规模演进", loc="left", fontsize=8.8, color=NAVY, pad=22)

    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax1b.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.5)

    save_chart(fig, "chart_3_5")


def build_chart_3_5b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    hw_names = [
        "NVIDIA B200 (稠密融合算子)",
        "NVIDIA B200 (稀疏注意力算子)",
        "NVIDIA H800 SXM5 (FlashMLA基准)",
        "华为 Ascend 950 (稀疏算子，峰值95%/83%)",
    ][::-1]
    decode_tflops = [950, 580, 660, 360][::-1]
    prefill_tflops = [1480, 1460, 660, 420][::-1]
    yh = np.arange(len(hw_names))

    ax2.barh(yh - 0.18, decode_tflops, height=0.32, color=TEAL, label="Decode 访存密集阶段实测算子吞吐（TFLOPS）")
    ax2.barh(yh + 0.18, prefill_tflops, height=0.32, color=NAVY, label="Prefill 计算密集阶段实测算子吞吐（TFLOPS）")
    for yi, dv, pv in zip(yh, decode_tflops, prefill_tflops):
        ax2.text(dv + 22, yi - 0.18, f"Decode {dv:,} TFLOPS", va="center", ha="left", fontsize=6.3, color=TEAL, bbox=WHITE_HALO)
        ax2.text(pv + 22, yi + 0.18, f"Prefill {pv:,} TFLOPS", va="center", ha="left", fontsize=6.3, color=NAVY, bbox=WHITE_HALO)

    ax2.set_yticks(yh)
    ax2.set_yticklabels(hw_names, fontsize=6.9)
    ax2.set_xlim(0, 1880)
    ax2.set_ylim(-0.6, 3.6)
    ax2.set_xlabel("实测算子吞吐（TFLOPS）", fontsize=7.2, color=SLATE)
    ax2.set_title("主流推理硬件平台在 Prefill 与 Decode 阶段的生产算子实测吞吐对比", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_3_5b")


# ===========================================================================
# 4.1 & 4.1B: Cloud GPU Pricing (21 SKUs) & Hyperscaler CapEx
# ===========================================================================
def build_chart_4_1():
    fig = plt.figure(figsize=(8.8, 5.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    skus = [
        "Oracle BM.GPU.GB300.4 (4×B300 NVL72)",
        "AWS p6-b300.48xlarge (8×B300 美西)",
        "Oracle BM.GPU.GB200.4 (4×B200 NVL72)",
        "Oracle BM.GPU.B300.8 (8×B300 263GB)",
        "AWS p6-b200.48xlarge (8×B200 美西)",
        "Oracle BM.GPU.B200.8 (8×B200 180GB)",
        "Oracle BM.GPU.H200.8 / H100.8 (8×Hopper)",
        "Oracle BM.GPU.MI355X.8 (8×AMD CDNA4)",
        "Azure NC40ads_H100_v5 (美东至东南亚)",
        "AWS p5.48xlarge (8×H100 美东)",
        "Lambda B200 SXM6 180GB (按需)",
        "Oracle BM.GPU.MI300X.8 (8×AMD 192GB)",
        "Oracle BM.GPU.RTXPro.8 (8×RTX PRO 6000)",
        "Lambda H100 SXM 80GB (按需)",
        "Oracle BM.GPU.A100-v2.8 (8×A100 80GB)",
        "AWS p4de.24xlarge (8×A100 美东至欧亚)",
        "Oracle BM.GPU.L40S.4 (4×L40S 48GB)",
        "Oracle BM.GPU4.8 (8×A100 40GB)",
        "Oracle VM/BM.GPU3.1~8 (1~8×V100 16GB)",
        "Oracle VM/BM.GPU.A10.1~4 (1~4×A10 24GB)",
        "Oracle VM/BM.GPU2.1~2 (1~2×P100 16GB)",
    ][::-1]
    p_low = np.array([
        18.00, 17.80, 16.00, 15.00, 14.24, 14.00, 10.00, 8.60, 6.98, 6.88,
        6.69, 6.00, 4.50, 3.99, 4.00, 3.43, 3.50, 3.05, 2.95, 2.00, 1.275
    ])[::-1]
    p_high = np.array([
        18.00, 17.80, 16.00, 15.00, 14.24, 14.00, 10.00, 8.60, 9.074, 6.88,
        6.99, 6.00, 4.50, 4.29, 4.00, 4.29, 3.50, 3.05, 2.95, 2.00, 1.275
    ])[::-1]
    sku_notes = [
        "整机 $72.00/h",
        "整机 $142.42/h",
        "整机 $64.00/h",
        "整机 $120.00/h",
        "整机 $113.93/h",
        "整机 $112.00/h",
        "整机 $80.00/h",
        "整机 $68.80/h",
        "跨区溢价 +30.0%",
        "整机 $55.04/h",
        "专科云按需价",
        "整机 $48.00/h",
        "整机 $36.00/h",
        "专科云按需价",
        "整机 $32.00/h",
        "整机 $27.45~$34.29/h",
        "整机 $14.00/h",
        "整机 $24.40/h",
        "1/2/4/8卡同单价",
        "1/2/4卡同单价",
        "1/2卡同单价",
    ][::-1]
    ys = np.arange(len(skus))

    for yi, pl, ph, sn in zip(ys, p_low, p_high, sku_notes):
        col = TEAL if pl <= 4.5 else (AMBER if pl <= 10.0 else NAVY)
        ax2.barh(yi, pl, height=0.62, color=col, alpha=0.90)
        if ph > pl:
            ax2.plot([pl, ph], [yi, yi], color=CRIMSON, lw=1.8)
            ax2.scatter([pl, ph], [yi, yi], s=18, color=CRIMSON, zorder=4)
            ax2.text(ph + 0.30, yi, f"${pl:.2f}~${ph:.2f}/GPU·h（{sn}）", va="center", ha="left", fontsize=6.0, color=NAVY, bbox=WHITE_HALO)
        else:
            ax2.text(pl + 0.30, yi, f"${pl:g}/GPU·h（{sn}）", va="center", ha="left", fontsize=6.0, color=NAVY, bbox=WHITE_HALO)

    ax2.set_yticks(ys)
    ax2.set_yticklabels(skus, fontsize=6.1)
    ax2.set_xlim(0, 25.0)
    ax2.set_ylim(-0.7, len(skus) - 0.3)
    ax2.set_xlabel("单卡等效按需价格（USD / GPU·小时）", fontsize=7.0, color=SLATE)
    ax2.set_title("国际主流云厂商 GPU 算力实例按需单价对比", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_4_1")


def build_chart_4_1b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    firms = get_input('figure_inputs.json', 'build_chart_4_1b', 'firms')
    capex_prev = get_input('figure_inputs.json', 'build_chart_4_1b', 'capex_prev')
    capex_2026 = get_input('figure_inputs.json', 'build_chart_4_1b', 'capex_2026')
    x = np.arange(len(firms))

    ax1.bar(x - 0.17, capex_prev, width=0.32, color="#94A3B8", label="上期年度实绩（十亿美元）")
    ax1.bar(x + 0.17, capex_2026, width=0.32, color=NAVY, label="2026年指引或最新季年化（十亿美元）")
    for xi, v1, v2 in zip(x, capex_prev, capex_2026):
        yoy = (v2 - v1) / v1 * 100.0
        ax1.text(xi - 0.17, v1 + 5, f"${v1:.1f}B", ha="center", va="bottom", fontsize=6.5, color=SLATE, bbox=WHITE_HALO)
        ax1.text(xi + 0.17, v2 + 5, f"${v2:.1f}B (+{yoy:.0f}%)", ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)

    ax1.set_xticks(x)
    ax1.set_xticklabels(firms, fontsize=7.0)
    ax1.set_ylim(0, 255)
    ax1.set_ylabel("资本开支（十亿美元）", fontsize=7.1, color=SLATE)
    ax1.set_title("北美五大超大规模云与 AI 企业资本开支对比", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_4_1b")


# ===========================================================================
# 4.3 & 4.3B: Competitive Moat & Regional Price Index
# ===========================================================================
def build_chart_4_3():
    fig = plt.figure(figsize=(8.8, 4.4), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    factors = ["电力与基建成本", "MoE与算子工程", "单集群芯片密度", "软件生态与赠金", "多法域主权合规"][::-1]
    cn_score = [92, 88, 64, 48, 56][::-1]
    us_score = [52, 85, 96, 95, 88][::-1]
    neo_score = [62, 76, 88, 54, 65][::-1]
    yf = np.arange(len(factors))

    ax1.barh(yf - 0.25, cn_score, height=0.22, color=NAVY, label="中国绿色算力体系")
    ax1.barh(yf, us_score, height=0.22, color=TEAL, label="北美三大超大规模云")
    ax1.barh(yf + 0.25, neo_score, height=0.22, color=AMBER, label="海外专科云 (Neocloud)")
    for yi, cs, us, ns in zip(yf, cn_score, us_score, neo_score):
        ax1.text(cs + 1.2, yi - 0.25, f"{cs}", va="center", ha="left", fontsize=6.0, color=NAVY)
        ax1.text(us + 1.2, yi, f"{us}", va="center", ha="left", fontsize=6.0, color=TEAL)
        ax1.text(ns + 1.2, yi + 0.25, f"{ns}", va="center", ha="left", fontsize=6.0, color=AMBER)

    ax1.set_yticks(yf)
    ax1.set_yticklabels(factors, fontsize=7.0)
    ax1.set_xlim(0, 112)
    ax1.set_ylim(-0.65, 4.65)
    ax1.set_xlabel("竞争力评分 (0~100)", fontsize=7.2, color=SLATE)
    ax1.set_title("三类算力供给主体五维竞争能力结构对比", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_4_3")


def build_chart_4_3b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    regs = get_input('figure_inputs.json', 'build_chart_4_3b', 'regs')
    a100_idx = get_input('figure_inputs.json', 'build_chart_4_3b', 'a100_idx')
    h100_idx = get_input('figure_inputs.json', 'build_chart_4_3b', 'h100_idx')
    xr = np.arange(len(regs))

    ax2.bar(xr - 0.18, a100_idx, width=0.30, color=SLATE, label="A100 节点价格指数", zorder=3)
    ax2.bar(xr + 0.18, h100_idx, width=0.30, color=TEAL, label="H100 节点价格指数", zorder=3)
    ax2.axhline(100, color=CRIMSON, linestyle="--", lw=0.9, zorder=2)
    for xi, v1, v2 in zip(xr, a100_idx, h100_idx):
        diff_txt = "基准100" if xi == 0 else (f"+{v2 - 100:.0f}%" if v2 > 100 else f"-{100 - v2:.0f}%")
        ax2.text(xi - 0.18, v1 + 3.8, f"{v1:.0f}", ha="center", va="bottom", fontsize=6.5, color=SLATE, bbox=WHITE_HALO, zorder=6)
        ax2.text(xi + 0.20, v2 + 3.8, f"{v2:.0f} ({diff_txt})", ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO, zorder=6)
    ax2.set_xticks(xr)
    ax2.set_xticklabels(regs, fontsize=7.0)
    ax2.set_ylim(0, 155)
    ax2.set_ylabel("价格指数（美东=100）", fontsize=7.2, color=SLATE)
    ax2.set_title("跨区域云算力价格指数与中国西部绿电算力成本指数对比", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_4_3b")


# ===========================================================================
# 5.2 & 5.2B: Subsea Cable Capacity & IPLC Tariffs
# ===========================================================================
def build_chart_5_2():
    fig = plt.figure(figsize=(8.8, 4.1), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    cables = [
        "ALC 亚洲快链 (2025至2026分段登陆)",
        "SEA-H2X 亚太快线 (2026-07-22投产)",
        "ADC 亚太直达 (2025-02投产)",
        "SJC2 东南亚日本二号 (2025-07-16投产)",
        "AAE-1 亚非欧一号 (在役主干)",
    ][::-1]
    sys_cap = [325, 200, 160, 126, 100][::-1]
    len_100km = [62.0, 57.46, 99.88, 105.0, 250.0][::-1]
    cap_notes = [
        "系统 >325 Tbps（中国电信/联通联合参建，香港及陵水登陆）",
        "系统 >200 Tbps（8对光纤，中国移动披露参建权益 >100 Tbps）",
        "系统 >160 Tbps（中国电信2025年2月宣布启用 >50 Tbps）",
        "系统 126 Tbps（中国移动参建，连通香港/新加坡/日本）",
        "系统 >100 Tbps（中国联通参建，亚非欧超长距主干通道）",
    ][::-1]
    yc = np.arange(len(cables))

    ax1.barh(yc + 0.18, sys_cap, height=0.32, color=NAVY, label="全系统设计容量 (Tbps)")
    ax1.barh(yc - 0.18, len_100km, height=0.32, color=TEAL, label="海缆主干全长（百公里 / 100 km）")
    for yi, sc, lk, cn in zip(yc, sys_cap, len_100km, cap_notes):
        ax1.text(sc + 5, yi + 0.18, cn, va="center", ha="left", fontsize=5.9, color=NAVY, bbox=WHITE_HALO)
        ax1.text(lk + 5, yi - 0.18, f"主干全长 {lk * 100:,.0f} km", va="center", ha="left", fontsize=6.0, color=TEAL, bbox=WHITE_HALO)

    ax1.set_yticks(yc)
    ax1.set_yticklabels(cables, fontsize=6.9)
    ax1.set_xlim(0, 560)
    ax1.set_ylim(-0.6, 4.6)
    ax1.set_xlabel("系统设计容量 (Tbps) 与主干全长（百公里）", fontsize=7.2, color=SLATE)
    ax1.set_title("连接中国主要国际海缆系统设计容量、主干长度与中资参建实绩", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_5_2")


def build_chart_5_2b():
    fig = plt.figure(figsize=(8.8, 3.7), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    routes = get_input('figure_inputs.json', 'build_chart_5_2b', 'routes')
    iplc_usd = get_input('figure_inputs.json', 'build_chart_5_2b', 'iplc_usd')
    xr = np.arange(len(routes))

    ax2.bar(xr, iplc_usd, width=0.38, color=[TEAL, NAVY, BLUE, CRIMSON])
    for xi, v in zip(xr, iplc_usd):
        mult = v / 5.65
        ax2.text(xi, v + 2.4, f"${v:.2f}k/月 ({mult:.1f}x)", ha="center", va="bottom", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)

    ax2.set_xticks(xr)
    ax2.set_xticklabels(routes, fontsize=7.0)
    ax2.set_ylim(0, 92)
    ax2.set_ylabel("目录月租（千美元/月）", fontsize=7.2, color=SLATE)
    ax2.set_title("100Mbps IPLC/IEPL 国际专线不同路由方向公开目录月租对比", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_5_2b")


# ===========================================================================
# 5.5 & 5.5B: HKIX/SGIX Port Scale & Terrestrial Latency
# ===========================================================================
def build_chart_5_5():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="both")
    ports = get_input('figure_inputs.json', 'build_chart_5_5', 'ports')
    hkix_usd_per_gbps = get_input('figure_inputs.json', 'build_chart_5_5', 'hkix_usd_per_gbps')
    sgix_usd_per_gbps = get_input('figure_inputs.json', 'build_chart_5_5', 'sgix_usd_per_gbps')
    xp = np.arange(len(ports))

    ax1.plot(xp, hkix_usd_per_gbps, color=NAVY, marker="o", markersize=5.0, lw=2.0, label="香港 HKIX 单位带宽月费（美元/Gbps·月）", zorder=3)
    ax1.plot(xp, sgix_usd_per_gbps, color=TEAL, marker="s", markersize=5.0, lw=2.0, label="新加坡 SGIX 单位带宽月费（美元/Gbps·月）", zorder=3)
    for xi, vh, vs in zip(xp, hkix_usd_per_gbps, sgix_usd_per_gbps):
        ax1.text(xi, vh + 8.5, f"HKIX: ${vh:.1f}", ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO, zorder=6)
        ax1.text(xi, vs - 10.5, f"SGIX: ${vs:.1f}", ha="center", va="top", fontsize=6.5, color=TEAL, bbox=WHITE_HALO, zorder=6)

    ax1.set_xticks(xp)
    ax1.set_xticklabels(ports, fontsize=7.0)
    ax1.set_xlim(-0.4, 3.5)
    ax1.set_ylim(-24, 155)
    ax1.set_ylabel("单位月费（美元/Gbps）", fontsize=7.2, color=SLATE)
    ax1.set_title("香港 HKIX 与新加坡 SGIX 互联网交换中心端口单位带宽月费曲线", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_5_5")


def build_chart_5_5b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    metrics = get_input('figure_inputs.json', 'build_chart_5_5b', 'metrics')
    before_v = get_input('figure_inputs.json', 'build_chart_5_5b', 'before_v')
    after_v = get_input('figure_inputs.json', 'build_chart_5_5b', 'after_v')
    xm = np.arange(len(metrics))

    ax2.bar(xm - 0.16, before_v, width=0.28, color="#94A3B8", label="改造前绕转 / 正常态时延 (ms)")
    ax2.bar(xm + 0.16, after_v, width=0.28, color=[TEAL, TEAL, CRIMSON], label="陆缆直连后 / 海缆故障态时延 (ms)")
    for xi, v1, v2 in zip(xm, before_v, after_v):
        delta_pct = (v2 - v1) / v1 * 100.0
        ax2.text(xi - 0.16, v1 + 3.2, f"{v1} ms", ha="center", va="bottom", fontsize=6.5, color=SLATE, bbox=WHITE_HALO)
        ax2.text(xi + 0.16, v2 + 3.2, f"{v2} ms ({delta_pct:+.1f}%)", ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)

    ax2.set_xticks(xm)
    ax2.set_xticklabels(metrics, fontsize=6.9)
    ax2.set_ylim(0, 148)
    ax2.set_ylabel("往返时延 (ms)", fontsize=7.2, color=SLATE)
    ax2.set_title("跨境陆缆直连降时延实效与海缆断面故障时延冲击对比", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_5_5b")


# ===========================================================================
# 6.2 & 6.2B: Task SLA Latency & Multimodal Engineering Specs
# ===========================================================================
def build_chart_6_2():
    fig = plt.figure(figsize=(8.8, 3.9), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="both")
    ax1.axvspan(0.2, 0.8, color=CRIMSON, alpha=0.05)
    ax1.axvspan(0.8, 6.0, color=TEAL, alpha=0.05)
    ax1.axvspan(6.0, 55.0, color=EMERALD, alpha=0.06)

    pts = [
        (0.35, 22, "实时语音与数字人 (TTFT≤0.5s, TPOT≤25ms)", CRIMSON, (0.45, 26)),
        (1.3, 75, "在线客服与多轮对话 (TTFT≤2.0s, TPOT≤80ms)", TEAL, (1.65, 75)),
        (3.2, 125, "代码生成与智能体 Agent (3.2s, 125ms)", NAVY, (4.0, 125)),
        (7.5, 175, "多模态视频生成 wan3.0 (7.5s, 175ms)", AMBER, (9.2, 175)),
        (18.0, 228, "JSONL 异步批处理 (24h窗口, 50%折扣)", EMERALD, (16.5, 202)),
    ]
    for x_t, y_t, lbl, col, (tx, ty) in pts:
        ax1.scatter([x_t], [y_t], s=82, color=col, edgecolor="#FFFFFF", lw=1.1, zorder=4)
        ha_m = "center" if x_t >= 15 else "left"
        ax1.text(tx, ty, lbl, fontsize=6.5, color=NAVY, ha=ha_m, va="center", bbox=WHITE_HALO, zorder=6)

    ax1.set_xscale("log")
    ax1.set_xlim(0.2, 55)
    ax1.set_xticks([0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0, 50.0])
    ax1.set_xticklabels(["0.2s", "0.5s", "1.0s", "2.0s", "5.0s", "10s", "25s", "50s"], fontsize=6.9)
    ax1.minorticks_off()
    ax1.set_ylim(0, 260)
    ax1.set_xlabel("首字时延 TTFT（秒，对数刻度）", fontsize=7.2, color=SLATE)
    ax1.set_ylabel("生成间隔 TPOT (ms)", fontsize=7.2, color=SLATE)
    ax1.set_title("典型 AI 推理任务的首字时延 (TTFT) 与生成间隔 (TPOT) 分布", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_6_2")


def build_chart_6_2b():
    fig = plt.figure(figsize=(8.8, 3.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    items = [
        "SLA 一档违约赔付 (99.0% ≤ 月可用率 < 99.9%)",
        "SLA 二档违约赔付 (95.0% ≤ 月可用率 < 99.0%)",
        "SLA 三档违约赔付 (月可用率 < 95.0%)",
        "JSONL 异步批处理 (24h窗口) 价格折扣",
        "UTC 10:00至01:00 错峰谷段 API 价格折扣",
    ][::-1]
    pct_vals = [10.0, 25.0, 50.0, 50.0, 50.0][::-1]
    val_lbls = [
        "10.0%（按月度服务费抵扣 10%，阿里云国际站 SLA）",
        "25.0%（按月度服务费抵扣 25%，阿里云国际站 SLA）",
        "50.0%（按月度服务费抵扣 50%，阿里云国际站 SLA）",
        "50.0%（单文件 ≤500MB / ≤50,000条请求，实时单价5折）",
        "50.0%（北京时间 18:00至次日09:00 跨时区谷段5折）",
    ][::-1]
    yi = np.arange(len(items))

    ax2.barh(yi, pct_vals, height=0.46, color=[BLUE, AMBER, CRIMSON, TEAL, EMERALD][::-1])
    for y_idx, v, vl in zip(yi, pct_vals, val_lbls):
        ax2.text(v + 1.2, y_idx, vl, va="center", ha="left", fontsize=6.4, color=NAVY, bbox=WHITE_HALO)
    ax2.set_yticks(yi)
    ax2.set_yticklabels(items, fontsize=6.9)
    ax2.set_xlim(0, 92)
    ax2.set_xlabel("费用抵扣比例 / 价格折扣比例 (%)", fontsize=7.2, color=SLATE)
    ax2.set_title("国际模型平台 SLA 分档服务抵扣比例与异步错峰价格折扣标准", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_6_2b")


# ===========================================================================
# 6.5: 24h Carbon-Aware Virtual Capacity & Off-Peak Window
# ===========================================================================
def build_chart_6_5():
    fig = plt.figure(figsize=(8.8, 4.2), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    style_ax(ax, grid_axis="both", hide_top_right=False)
    ax.spines["top"].set_visible(False)

    utc_hrs = np.arange(0, 24)
    grid_carbon = np.array(get_input('figure_inputs.json', 'build_chart_6_5', 'grid_carbon'), dtype=float)
    virtual_cap = np.array(get_input('figure_inputs.json', 'build_chart_6_5', 'virtual_cap'), dtype=float)

    ax.plot(utc_hrs, grid_carbon, color=CRIMSON, lw=2.0, marker="o", markersize=3.5, label="西部电网小时边际碳强度（gCO2/kWh）", zorder=3)
    ax.set_ylabel("边际碳强度 (gCO2/kWh)", fontsize=7.2, color=CRIMSON)
    ax.tick_params(axis="y", colors=CRIMSON)
    ax.set_ylim(80, 740)

    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(TEAL)
    ax2.fill_between(utc_hrs, 0, virtual_cap, color=TEAL, alpha=0.14, zorder=2)
    ax2.plot(utc_hrs, virtual_cap, color=TEAL, lw=2.0, linestyle="--", label="可延期推理负载虚拟容量配额 (%)", zorder=3)
    ax2.set_ylabel("虚拟容量配额 (%)", fontsize=7.2, color=TEAL)
    ax2.tick_params(axis="y", colors=TEAL)
    ax2.set_ylim(0, 122)

    ax.axvspan(3.0, 7.0, color=EMERALD, alpha=0.12)
    ax.axvspan(16.0, 23.5, color=BLUE, alpha=0.10)

    ax.text(5.0, 685, "窗口一：11:00~15:00 BJT（午间光伏谷段）", ha="center", va="center", fontsize=6.4, color=EMERALD, bbox=WHITE_HALO, zorder=6)
    ax.text(19.6, 685, "窗口二：00:00~08:30 BJT（跨时区API半价谷段）", ha="center", va="center", fontsize=6.4, color=BLUE, bbox=WHITE_HALO, zorder=6)

    ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
    ax.set_xticklabels(["00:00 UTC\n(08:00 BJT)", "04:00 UTC\n(12:00 BJT)", "08:00 UTC\n(16:00 BJT)", "12:00 UTC\n(20:00 BJT)", "16:00 UTC\n(00:00 BJT)", "20:00 UTC\n(04:00 BJT)", "23:00 UTC\n(07:00 BJT)"], fontsize=6.7)
    ax.set_title("基于电价信号、小时级边际碳强度与跨时区半价窗口的 24 小时联合调度曲线", loc="left", fontsize=8.8, color=NAVY, pad=22)

    l1, lb1 = ax.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, lb1 + lb2, loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_6_5")


# ===========================================================================
# 7.3 & 7.3B: Cross-Border Data Channels & Review Timelines
# ===========================================================================
def build_chart_7_3():
    fig = plt.figure(figsize=(8.8, 3.7), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    paths = [
        "16号令第4条：来数加工豁免",
        "16号令第5条：小规模豁免",
        "自贸区负面清单外豁免",
        "个人信息出境标准合同备案",
        "国家网信办数据出境安全评估",
    ][::-1]
    burden_idx = [8, 15, 22, 58, 95][::-1]
    cols = [EMERALD, TEAL, BLUE, AMBER, CRIMSON][::-1]
    yp = np.arange(len(paths))

    ax1.barh(yp, burden_idx, height=0.46, color=cols)
    tags = [
        "指数 8（免予评估 / 备案 / 认证）",
        "指数 15（年累计 <10万人一般信息免予申报）",
        "指数 22（负面清单外免予前置申报）",
        "指数 58（10万~100万人一般信息合同备案）",
        "指数 95（CIIO / 重要数据 / >100万人安全评估）",
    ][::-1]
    for yi, bv, tg in zip(yp, burden_idx, tags):
        ax1.text(bv + 2.0, yi, tg, va="center", ha="left", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)

    ax1.set_yticks(yp)
    ax1.set_yticklabels(paths, fontsize=7.0)
    ax1.set_xlim(0, 152)
    ax1.set_xlabel("程序复杂度指数 (0~100)", fontsize=7.2, color=SLATE)
    ax1.set_title("中国数据跨境流动五类制度通道与合规复杂度指数对比", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_7_3")


def build_chart_7_3b():
    fig = plt.figure(figsize=(8.8, 3.7), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    proc = [
        "安全评估：省级网信办完备性查验",
        "安全评估：国家网信办受理决定",
        "上海自贸区：负面清单区级初审",
        "标准合同：生效后提交备案窗口",
        "标准合同：省级网信办材料查验",
        "增值电信业务许可证：法定审查期",
    ][::-1]
    days = [5, 7, 10, 10, 15, 60][::-1]
    yp2 = np.arange(len(proc))

    ax2.barh(yp2, days, height=0.46, color=NAVY)
    for yi, dv in zip(yp2, days):
        unit = "自然日" if dv == 60 else "个工作日"
        ax2.text(dv + 1.2, yi, f"{dv} {unit}", va="center", ha="left", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)
    ax2.set_yticks(yp2)
    ax2.set_yticklabels(proc, fontsize=7.0)
    ax2.set_xlim(0, 74)
    ax2.set_xlabel("法定时限（工作日 / 自然日）", fontsize=7.2, color=SLATE)
    ax2.set_title("电信业务准入与数据出境核心审查环节法定时限对比", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_7_3b")


# ===========================================================================
# 7.5 & 7.5B: Green Power Thresholds & Validity Periods
# ===========================================================================
def build_chart_7_5():
    fig = plt.figure(figsize=(8.8, 3.7), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    metrics = get_input('figure_inputs.json', 'build_chart_7_5', 'metrics')
    vals = get_input('figure_inputs.json', 'build_chart_7_5', 'vals')
    xm = np.arange(len(metrics))

    ax1.bar(xm, vals, width=0.38, color=[TEAL, BLUE, NAVY, EMERALD, SLATE])
    for xi, v in zip(xm, vals):
        ax1.text(xi, v + 2.8, f"≥{v}%", ha="center", va="bottom", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)
    ax1.set_xticks(xm)
    ax1.set_xticklabels(metrics, fontsize=7.0)
    ax1.set_ylim(0, 98)
    ax1.set_ylabel("政策阈值 (%)", fontsize=7.2, color=SLATE)
    ax1.set_title("2025至2030年绿电直连、绿电消费与国家枢纽算力集聚政策指标", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_7_5")


def build_chart_7_5b():
    fig = plt.figure(figsize=(8.8, 3.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    rules = [
        "绿证核销有效期限",
        "数据出境安全评估有效期",
        "个人信息出境认证有效期",
        "安全评估延期申请窗口",
        "评估延期允许增幅上限",
    ][::-1]
    r_vals = [24, 36, 36, 12, 20][::-1]
    r_lbls = [
        "24 个自然月（2年）",
        "36 个月（3年，可顺延3年）",
        "36 个月（3年，届满前6个月续证）",
        "届满前 60 个工作日（约12周）",
        "出境数据规模增幅 ≤20%",
    ][::-1]
    yr = np.arange(len(rules))

    ax2.barh(yr, r_vals, height=0.46, color=TEAL)
    for yi, rv, rl in zip(yr, r_vals, r_lbls):
        ax2.text(rv + 1.0, yi, rl, va="center", ha="left", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)
    ax2.set_yticks(yr)
    ax2.set_yticklabels(rules, fontsize=7.0)
    ax2.set_xlim(0, 56)
    ax2.set_xlabel("周期参数（月 / 周 / 增幅%）", fontsize=7.2, color=SLATE)
    ax2.set_title("中国绿证核销有效期与跨境数据合规资质存续期参数", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_7_5b")


# ===========================================================================
# 8.1: 10 Target Jurisdictions Compliance Heatmap
# ===========================================================================
def build_chart_8_1():
    fig = plt.figure(figsize=(8.8, 4.7), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)

    markets = get_input('figure_inputs.json', 'build_chart_8_1', 'markets')
    dims = get_input('figure_inputs.json', 'build_chart_8_1', 'dims')
    matrix = np.array(get_input('figure_inputs.json', 'build_chart_8_1', 'matrix'))

    cmap = matplotlib.colors.ListedColormap(["#E0F2FE", "#BAE6FD", "#7DD3FC", "#FCD34D", "#B91C1C"])
    ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=1, vmax=5)

    ax.set_xticks(np.arange(len(dims) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(markets) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="#FFFFFF", linestyle="-", linewidth=1.8)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_xticks(np.arange(len(dims)))
    ax.set_xticklabels(dims, fontsize=6.9, color=NAVY)
    ax.set_yticks(np.arange(len(markets)))
    ax.set_yticklabels(markets, fontsize=7.0, color=NAVY)

    level_txt = get_input('figure_inputs.json', 'build_chart_8_1', 'level_txt')
    for i in range(len(markets)):
        for j in range(len(dims)):
            v = matrix[i, j]
            # High contrast rule: only dark crimson (5) uses white text; levels 1-4 use dark NAVY text
            t_col = "#FFFFFF" if v == 5 else NAVY
            ax.text(j, i, level_txt[v], ha="center", va="center", fontsize=6.5, color=t_col)

    ax.set_title("十大海外目标法域跨境推理准入与数据安全治理摩擦等级分布（1级至5级）", loc="left", fontsize=8.8, color=NAVY, pad=14)
    for spine in ax.spines.values():
        spine.set_visible(False)

    save_chart(fig, "chart_8_1")


# ===========================================================================
# 9.2 & 9.2B: LCoT Decomposition & GDS Financial Reality
# ===========================================================================
def build_chart_9_2():
    fig = plt.figure(figsize=(8.8, 4.4), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    modes = get_input('figure_inputs.json', 'build_chart_9_2', 'modes')
    hw_depr = np.array(get_input('figure_inputs.json', 'build_chart_9_2', 'hw_depr'))
    power_pue = np.array(get_input('figure_inputs.json', 'build_chart_9_2', 'power_pue'))
    net_ixp = np.array(get_input('figure_inputs.json', 'build_chart_9_2', 'net_ixp'))
    ops_comp = np.array(get_input('figure_inputs.json', 'build_chart_9_2', 'ops_comp'))
    totals = hw_depr + power_pue + net_ixp + ops_comp
    xm = np.arange(len(modes))
    w = 0.40

    ax1.bar(xm, hw_depr, width=w, color=NAVY, label="硬件折旧摊销")
    ax1.bar(xm, power_pue, bottom=hw_depr, width=w, color=EMERALD, label="电力与PUE冷却")
    ax1.bar(xm, net_ixp, bottom=hw_depr + power_pue, width=w, color=AMBER, label="海陆专线与IXP端口")
    ax1.bar(xm, ops_comp, bottom=hw_depr + power_pue + net_ixp, width=w, color=SLATE, label="运维合规与渠道分成")

    for xi, tot, hd, pp, ni, oc in zip(xm, totals, hw_depr, power_pue, net_ixp, ops_comp):
        diff = tot - 100.0
        diff_str = "基准 100.0" if xi == 0 else (f"总指数 {tot:.1f} (+{diff:.0f}%)" if diff > 0 else f"总指数 {tot:.1f} ({diff:.0f}%)")
        ax1.text(xi, tot + 3.5, diff_str, ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)
        # 1. Hardware depreciation (all >= 34.0)
        ax1.text(xi, hd / 2.0, f"{hd:.1f}", ha="center", va="center", color="#FFFFFF", fontsize=6.2)
        # 2. Power & PUE
        y_pp = hd + pp / 2.0
        if pp >= 8.5:
            ax1.text(xi, y_pp, f"{pp:.1f}", ha="center", va="center", color="#FFFFFF", fontsize=5.9)
        else:
            ax1.plot([xi - w / 2.0 - 0.06, xi - w / 2.0], [y_pp, y_pp], color=EMERALD, lw=0.8)
            ax1.text(xi - w / 2.0 - 0.08, y_pp, f"电力 {pp:.1f}", ha="right", va="center", color=EMERALD, fontsize=5.7, bbox=WHITE_HALO)
        # 3. Network & IXP
        y_ni = hd + pp + ni / 2.0
        if ni >= 8.0:
            ax1.text(xi, y_ni, f"{ni:.1f}", ha="center", va="center", color="#FFFFFF", fontsize=5.9)
        else:
            ax1.plot([xi + w / 2.0, xi + w / 2.0 + 0.06], [y_ni, y_ni], color=AMBER, lw=0.8)
            ax1.text(xi + w / 2.0 + 0.08, y_ni, f"专线 {ni:.1f}", ha="left", va="center", color=AMBER, fontsize=5.7, bbox=WHITE_HALO)
        # 4. Ops & Compliance (all >= 12.3)
        ax1.text(xi, tot - oc / 2.0, f"{oc:.1f}", ha="center", va="center", color="#FFFFFF", fontsize=6.0)

    ax1.set_xticks(xm)
    ax1.set_xticklabels(modes, fontsize=7.0)
    ax1.set_xlim(-0.55, 3.55)
    ax1.set_ylim(0, 148)
    ax1.set_ylabel("成本指数（美东=100）", fontsize=7.2, color=SLATE)
    ax1.set_title("四类跨国推理部署架构百万 Token 生命周期成本 (LCoT) 结构拆解", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=4, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_9_2")


def build_chart_9_2b():
    fig = plt.figure(figsize=(8.8, 3.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    gds_metrics = get_input('figure_inputs.json', 'build_chart_9_2b', 'gds_metrics')
    gds_vals = get_input('figure_inputs.json', 'build_chart_9_2b', 'gds_vals')
    xg = np.arange(len(gds_metrics))

    ax2.bar(xg, gds_vals, width=0.38, color=[SLATE, NAVY, TEAL, TEAL])
    for xi, v in zip(xg, gds_vals):
        lbl = f"{v:.1f}% (+3.7pct)" if xi == 1 else f"{v:.1f}%"
        ax2.text(xi, v + 2.4, lbl, ha="center", va="bottom", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)
    ax2.set_xticks(xg)
    ax2.set_xticklabels(gds_metrics, fontsize=7.0)
    ax2.set_ylim(0, 96)
    ax2.set_ylabel("运营与盈利比率 (%)", fontsize=7.2, color=SLATE)
    ax2.set_title("头部数据中心运营商（万国数据 GDS）计费面积利用率与经调整 EBITDA 利润率变化", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_9_2b")


# ===========================================================================
# 9.3: 2026 Flagship LLM API Price Spectrum
# ===========================================================================
def build_chart_9_3():
    fig = plt.figure(figsize=(8.8, 5.4), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    style_ax(ax, grid_axis="x")

    models = [
        "Qwen3.8-Max (阿里云 新加坡站 ≤32k)",
        "Qwen3.8-Max (阿里云 中国北京站 ≤32k)",
        "DeepSeek-V4-Pro (常规高峰时段)",
        "DeepSeek-V4-Pro (UTC 10:00~01:00 谷段5折)",
        "Claude Haiku 5.5 (>100k 上下文)",
        "DeepSeek-V4.1-Flash (常规高峰时段)",
        "DeepSeek-V4.1-Flash (UTC 10:00~01:00 谷段5折)",
        "Claude Haiku 5.5 (≤100k 上下文)",
        "Qwen3.8-Flash (Together AI)",
    ][::-1]

    p_cache = np.array([0.20, 0.165, 0.044, 0.022, 0.05, 0.006, 0.003, 0.01, 0.03])[::-1]
    p_input = np.array([2.00, 1.65, 1.32, 0.66, 0.50, 0.30, 0.15, 0.10, 0.15])[::-1]
    p_output = np.array([6.00, 4.951, 3.96, 1.98, 2.50, 1.20, 0.60, 0.50, 0.47])[::-1]
    ym = np.arange(len(models))

    ax.barh(ym + 0.25, p_output, height=0.22, color=NAVY, label="输出单价（美元/百万Token）")
    ax.barh(ym, p_input, height=0.22, color=TEAL, label="输入未命中单价（美元/百万Token）")
    ax.barh(ym - 0.25, p_cache, height=0.22, color=AMBER, label="输入缓存命中单价（美元/百万Token）")

    for yi, po, pi, pc in zip(ym, p_output, p_input, p_cache):
        ax.text(po + 0.09, yi + 0.25, f"输出 ${po:g}", va="center", ha="left", fontsize=5.7, color=NAVY)
        ax.text(pi + 0.09, yi, f"输入 ${pi:g}", va="center", ha="left", fontsize=5.7, color=TEAL)
        ax.text(pc + 0.09, yi - 0.25, f"缓存 ${pc:g}", va="center", ha="left", fontsize=5.7, color=AMBER)

    ax.set_yticks(ym)
    ax.set_yticklabels(models, fontsize=6.7)
    ax.set_xlim(0, 7.6)
    ax.set_ylim(-0.65, 8.65)
    ax.set_xlabel("API 挂牌单价（美元 / 百万 Token）", fontsize=7.2, color=SLATE)
    ax.set_title("2026年10月主流大模型 API 输入、缓存命中与输出分档价格对比", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_9_3")


# ===========================================================================
# 9.5 & 9.5B: Tornado Sensitivity & Utilization Break-Even
# ===========================================================================
def build_chart_9_5():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    drivers = [
        "集群有效利用率 (45%~85%)",
        "API平均成交单价 (-25%~+15%)",
        "全口径到户电价 (0.48~0.28元/度)",
        "KV缓存命中率 (20%~75%)",
        "跨境专线带宽单价 (+30%~-30%)",
        "GPU硬件采购成本 (+20%~-15%)",
    ][::-1]
    low_delta = np.array([-16.5, -12.0, -6.2, -5.5, -4.2, -4.8])[::-1]
    high_delta = np.array([+11.2, +7.5, +5.8, +6.4, +4.0, +3.6])[::-1]
    yd = np.arange(len(drivers))

    ax1.barh(yd, low_delta, height=0.46, color=CRIMSON, alpha=0.86, label="不利变动对净利率冲击（百分点）")
    ax1.barh(yd, high_delta, height=0.46, color=TEAL, alpha=0.90, label="有利变动对净利率提升（百分点）")
    ax1.axvline(0, color=NAVY, lw=0.9)
    for yi, ld, hd in zip(yd, low_delta, high_delta):
        ax1.text(ld - 0.6, yi, f"{ld:+.1f}pct", va="center", ha="right", fontsize=6.5, color=CRIMSON, bbox=WHITE_HALO)
        ax1.text(hd + 0.6, yi, f"{hd:+.1f}pct", va="center", ha="left", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)

    ax1.set_yticks(yd)
    ax1.set_yticklabels(drivers, fontsize=7.0)
    ax1.set_xlim(-22, 18)
    ax1.set_ylim(-0.6, 5.6)
    ax1.set_xlabel("净利率敏感度变动（百分点）", fontsize=7.2, color=SLATE)
    ax1.set_title("Token 出海项目经营净利率六维敏感性龙卷风图", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.8)

    save_chart(fig, "chart_9_5")


def build_chart_9_5b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="both")
    util = np.linspace(25, 90, 100)
    margin_west = -38 + 0.92 * util - 0.0018 * (util ** 2)
    margin_overseas = -48 + 0.85 * util - 0.0018 * (util ** 2)

    ax2.plot(util, margin_west, color=NAVY, lw=2.0, label="中国西部绿电直连集群（电价 0.30~0.35元/度）", zorder=3)
    ax2.plot(util, margin_overseas, color=AMBER, lw=1.8, linestyle="--", label="海外高成本租用集群（亚太/欧洲高电价）", zorder=3)
    ax2.axhline(0, color=CRIMSON, linestyle=":", lw=1.0, zorder=2)
    ax2.fill_between(util, margin_overseas, margin_west, color=TEAL, alpha=0.12, label="中国绿电经营安全垫（平衡点低20.2pct）", zorder=1)

    ax2.scatter([46.0, 66.2], [0.0, 0.0], s=42, color=CRIMSON, zorder=5)
    ax2.text(44.0, 6.5, "西部集群平衡点：46.0%", ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO, zorder=6)
    ax2.text(68.5, -8.5, "海外集群平衡点：66.2%", ha="center", va="top", fontsize=6.5, color=AMBER, bbox=WHITE_HALO, zorder=6)

    ax2.set_xlim(25, 90)
    ax2.set_ylim(-26, 36)
    ax2.set_xlabel("年均有效计费利用率 (%)", fontsize=7.2, color=SLATE)
    ax2.set_ylabel("税前经营利润率 (%)", fontsize=7.2, color=SLATE)
    ax2.set_title("重资产算力集群盈亏平衡利用率临界曲线", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3, frameon=False, fontsize=6.6)

    save_chart(fig, "chart_9_5b")


# ===========================================================================
# 10.1 & 10.1B: Hub Construction & Regional Complementarity
# ===========================================================================
def build_chart_10_1():
    fig = plt.figure(figsize=(8.8, 4.0), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    hubs = [
        "宁夏中卫集群 (2026年6月实绩)",
        "甘肃庆阳集群 (2026上半年实绩)",
        "甘肃庆阳集群 (2025年末实绩)",
        "云南全省智算规划 (2027年目标)",
        "广东汕头1号词元工厂 (2026.05首期)",
    ][::-1]
    compute_p = [26.37, 18.55, 11.40, 2.00, 0.20][::-1]
    racks_w = [33.1, 10.2, 10.2, 0.0, 0.0][::-1]
    notes_h = get_input('figure_inputs.json', 'build_chart_10_1', 'notes_h')
    yh = np.arange(len(hubs))

    ax1.barh(yh - 0.16, compute_p, height=0.30, color=NAVY, label="智算规模实绩或规划目标（万PFLOPS，FP16）")
    ax1.barh(yh + 0.16, racks_w, height=0.30, color=TEAL, label="已披露标准机架规模（万架，未单列机架项目留空）")
    for yi, cp, rw, nh in zip(yh, compute_p, racks_w, notes_h):
        max_x = max(cp, rw)
        ax1.text(max_x + 0.8, yi, nh, va="center", ha="left", fontsize=5.9, color=NAVY, bbox=WHITE_HALO)

    ax1.set_yticks(yh)
    ax1.set_yticklabels(hubs, fontsize=6.9)
    ax1.set_xlim(0, 62)
    ax1.set_ylim(-0.6, 4.6)
    ax1.set_xlabel("智算规模（万PFLOPS）与标准机架（万架）", fontsize=7.2, color=SLATE)
    ax1.set_title("典型国家算力枢纽与沿海沿边节点智算规模及标准机架核定实绩", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_10_1")


def build_chart_10_1b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    dims = get_input('figure_inputs.json', 'build_chart_10_1b', 'dims')
    west_v = get_input('figure_inputs.json', 'build_chart_10_1b', 'west_v')
    coast_v = get_input('figure_inputs.json', 'build_chart_10_1b', 'coast_v')
    sw_v = get_input('figure_inputs.json', 'build_chart_10_1b', 'sw_v')
    xd = np.arange(len(dims))

    ax2.bar(xd - 0.22, west_v, width=0.21, color=NAVY, label="西北风光绿电基地（宁夏/甘肃/内蒙）")
    ax2.bar(xd, coast_v, width=0.21, color=TEAL, label="东部沿海国际门户（上海/广东/海南/青岛）")
    ax2.bar(xd + 0.22, sw_v, width=0.21, color=AMBER, label="西南水电与陆缆走廊（云南/贵州/四川）")
    for xi, wv, cv, sv in zip(xd, west_v, coast_v, sw_v):
        ax2.text(xi - 0.22, wv + 2.5, f"{wv}", ha="center", va="bottom", fontsize=6.5, color=NAVY)
        ax2.text(xi, cv + 2.5, f"{cv}", ha="center", va="bottom", fontsize=6.5, color=TEAL)
        ax2.text(xi + 0.22, sv + 2.5, f"{sv}", ha="center", va="bottom", fontsize=6.5, color=AMBER)

    ax2.set_xticks(xd)
    ax2.set_xticklabels(dims, fontsize=7.0)
    ax2.set_ylim(0, 114)
    ax2.set_ylabel("禀赋评分 (0~100)", fontsize=7.2, color=SLATE)
    ax2.set_title("国内三大区域板块在 Token 出海链条中的四维禀赋评估", loc="left", fontsize=8.8, color=NAVY, pad=22)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_10_1b")


# ===========================================================================
# 10.3 & 10.3B: Corporate Financials & Horinger PUE
# ===========================================================================
def build_chart_10_3():
    fig = plt.figure(figsize=(8.8, 4.0), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    cos = [
        "天亿马 (2026H1 合并营收同比)",
        "润泽科技 (2026H1 合并营收同比)",
        "君逸数码 (智算转投年均营收/总预算)",
        "万国数据 GDS (2026Q2 经调EBITDA率)",
        "鸿博股份 (2026H1 合并营收同比)",
    ][::-1]
    pct_metrics = np.array([+98.60, +50.05, +46.86, +45.50, -76.39])[::-1]
    c_notes = [
        "+98.60%（营收 2.13亿元；深圳算力集群营收 3,609万元，参设亿联词元）",
        "+50.05%（营收 37.46亿元；归母净利 12.03亿元 [+36.43%]，经营现金流 29.58亿）",
        "+46.86%（改投智算 2.05亿元；预计年均营收 9,628万元，静态回收期 5.15年）",
        "+45.50%（2026Q2净营收 30.88亿元，计费面积使用率回升至 79.2%）",
        "-76.39%（2026H1营收 1.87亿元 [上年同期7.90亿]，归母净亏损 -5,148万元）",
    ][::-1]
    yc = np.arange(len(cos))
    cols_c = [BLUE, EMERALD, AMBER, TEAL, CRIMSON][::-1]

    ax1.barh(yc, pct_metrics, height=0.46, color=cols_c, alpha=0.90)
    ax1.axvline(0, color=NAVY, lw=0.9)
    for yi, pv, cn in zip(yc, pct_metrics, c_notes):
        if pv >= 0:
            ax1.text(pv + 2.0, yi, cn, va="center", ha="left", fontsize=6.0, color=NAVY, bbox=WHITE_HALO)
        else:
            ax1.text(2.0, yi, cn, va="center", ha="left", fontsize=6.0, color=CRIMSON, bbox=WHITE_HALO)

    ax1.set_yticks(yc)
    ax1.set_yticklabels(cos, fontsize=6.8)
    ax1.set_xlim(-92, 225)
    ax1.set_ylim(-0.6, 4.6)
    ax1.set_xlabel("营收同比增速 / 经调EBITDA率 / 预算年化产出率 (%)", fontsize=7.0, color=SLATE)
    ax1.set_title("算力基础设施及转型样本企业 2026 年披露财务增速与盈利分化实证", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_10_3")


def build_chart_10_3b():
    fig = plt.figure(figsize=(8.8, 3.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="y")
    items = get_input('figure_inputs.json', 'build_chart_10_3b', 'items')
    pue_v = get_input('figure_inputs.json', 'build_chart_10_3b', 'pue_v')
    xi = np.arange(len(items))

    ax2.bar(xi, pue_v, width=0.36, color=[SLATE, AMBER, TEAL, EMERALD, NAVY])
    for x_idx, pv in zip(xi, pue_v):
        if x_idx == 3:
            lbl = f"PUE {pv:.3f} (-0.106)"
        elif x_idx in (2, 4):
            lbl = f"PUE ≤{pv:.3f}"
        else:
            lbl = f"PUE {pv:.3f}"
        ax2.text(x_idx, pv + 0.02, lbl, ha="center", va="bottom", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)
    ax2.set_xticks(xi)
    ax2.set_xticklabels(items, fontsize=6.8)
    ax2.set_ylim(0.9, 1.50)
    ax2.set_ylabel("电能利用效率 (PUE)", fontsize=7.1, color=SLATE)
    ax2.set_title("内蒙古和林格尔新区 B02 机楼节能改造实测 PUE 与国家及枢纽标准对比", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_10_3b")


# ===========================================================================
# 11.2 & 11.2B: 30-Province CO2 Factors & 11-Row LCA Factors
# ===========================================================================
def build_chart_11_2():
    fig = plt.figure(figsize=(8.8, 4.5), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    provs30 = get_input('figure_inputs.json', 'build_chart_11_2', 'provs30')
    p_names = [x[0] for x in provs30]
    p_vals = np.array([x[1] for x in provs30])
    xp = np.arange(len(provs30))
    p_cols = [
        EMERALD if v < 0.25 else (TEAL if v < 0.5306 else (AMBER if v < 0.61 else CRIMSON))
        for v in p_vals
    ]

    ax1.axhline(0.5306, color=NAVY, linestyle="--", lw=1.0, zorder=2, label="2023全国平均因子 (0.5306)")
    ax1.axhline(0.6096, color=AMBER, linestyle="-.", lw=1.0, zorder=2, label="全国剔除市场化非化石电量因子 (0.6096)")
    ax1.axhline(0.8273, color=CRIMSON, linestyle=":", lw=1.1, zorder=2, label="全国化石能源因子 / 2026绿色算力CUE基准 (0.8273)")

    ax1.bar(xp, p_vals, width=0.64, color=p_cols, alpha=0.92, zorder=3)
    for xi, pv in zip(xp, p_vals):
        ax1.text(xi, pv + 0.015, f"{pv:.4f}", ha="center", va="bottom", fontsize=4.8, color=NAVY, rotation=68, bbox=WHITE_HALO, zorder=6)

    ax1.set_xticks(xp)
    ax1.set_xticklabels(p_names, fontsize=6.0, rotation=45, ha="right")
    ax1.set_xlim(-0.8, 29.8)
    ax1.set_ylim(0, 0.92)
    ax1.set_ylabel("排放因子 (kgCO2/kWh)", fontsize=7.0, color=SLATE)
    ax1.set_title("2023年中国分省电力二氧化碳排放因子与国家基准线对比", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, frameon=False, fontsize=6.4)

    save_chart(fig, "chart_11_2")


def build_chart_11_2b():
    fig = plt.figure(figsize=(8.8, 4.2), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    lca11 = [
        ("输配电（不含线损）", 0.0046),
        ("核能发电", 0.0065),
        ("水力发电", 0.0141),
        ("光热发电", 0.0312),
        ("风力发电", 0.0324),
        ("输配电（含线损）", 0.0327),
        ("生物质发电", 0.0404),
        ("光伏发电", 0.0520),
        ("燃气发电", 0.4503),
        ("全国电力平均 (2024 LCA)", 0.5777),
        ("燃煤发电", 0.9240),
    ][::-1]

    lc_names = [x[0] for x in lca11]
    lc_vals = np.array([x[1] for x in lca11])
    ylc = np.arange(len(lca11))
    lc_cols = [CRIMSON if v > 0.6 else (AMBER if v > 0.4 else (EMERALD if v < 0.04 else TEAL)) for v in lc_vals]

    ax2.barh(ylc, lc_vals, height=0.56, color=lc_cols, alpha=0.90)
    for yi, lv in zip(ylc, lc_vals):
        ax2.text(lv + 0.015, yi, f"{lv:.4f} kgCO2e/kWh", va="center", ha="left", fontsize=6.4, color=NAVY, bbox=WHITE_HALO)

    ax2.set_yticks(ylc)
    ax2.set_yticklabels(lc_names, fontsize=6.8)
    ax2.set_xlim(0, 1.15)
    ax2.set_ylim(-0.65, 10.65)
    ax2.set_xlabel("全生命周期碳足迹因子 (kgCO2e/kWh)", fontsize=7.1, color=SLATE)
    ax2.set_title("2024年中国不同电源品种与输配电全生命周期碳足迹因子对比", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_11_2b")


# ===========================================================================
# 11.4 & 11.4B: IEA Global Regions & LBNL US Scenarios
# ===========================================================================
def build_chart_11_4():
    fig = plt.figure(figsize=(8.8, 4.9), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    iea9 = [
        ("全球总计 (World)", 360, 485, 945, 732),
        ("北美 (North America)", 158, 229, 434, 351),
        ("美国 (United States)", 154, 224, 426, 345),
        ("亚太 (Asia Pacific)", 128, 173, 378, 281),
        ("中国 (China)", 84, 117, 277, 205),
        ("欧洲 (Europe)", 66, 72, 114, 88),
        ("中东 (Middle East)", 1.3, 1.7, 3.0, 1.7),
        ("非洲 (Africa)", 1.3, 1.6, 2.9, 1.8),
        ("中南美 (CSA)", 1.2, 1.5, 2.7, 1.8),
    ][::-1]

    r_lbls = [x[0] for x in iea9]
    v23 = np.array([x[1] for x in iea9])
    v25 = np.array([x[2] for x in iea9])
    v30_tot = np.array([x[3] for x in iea9])
    v30_it = np.array([x[4] for x in iea9])
    yi9 = np.arange(len(iea9))

    ax1.barh(yi9 + 0.18, v30_tot, height=0.33, color=NAVY, label="2030年数据中心总用电量 (Total Facility, TWh)")
    ax1.barh(yi9 - 0.18, v25, height=0.33, color=TEAL, label="2025年数据中心总用电量 (Total Facility, TWh)")
    for y_i, v_23, v_25, v_30, v_it in zip(yi9, v23, v25, v30_tot, v30_it):
        ax1.text(
            v_30 + 10, y_i + 0.18,
            f"2030: {v_30:g} TWh（含IT设备 {v_it:g} TWh）",
            va="center", ha="left", fontsize=5.8, color=NAVY,
        )
        ax1.text(
            v_25 + 10, y_i - 0.18,
            f"2025: {v_25:g} TWh（2023: {v_23:g} TWh）",
            va="center", ha="left", fontsize=5.8, color=TEAL,
        )

    ax1.set_yticks(yi9)
    ax1.set_yticklabels(r_lbls, fontsize=6.9)
    ax1.set_xlim(0, 1280)
    ax1.set_ylim(-0.65, 8.65)
    ax1.set_xlabel("年度用电量 (TWh)", fontsize=7.1, color=SLATE)
    ax1.set_title("全球各区域数据中心总用电量与 IT 设备用电量演进（2025至2030年）", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_11_4")


def build_chart_11_4b():
    fig = plt.figure(figsize=(8.8, 3.8), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    lbnl_scens = [
        "双向不确定性上限 (High)",
        "高推理能耗情景 (High Inference)",
        "高专用芯片占比 (High ASIC)",
        "2030 基准情景 (Reference Case)",
        "加速器短折旧周期 (Low Lifetime)",
        "集约化部署情景 (Consolidated)",
        "双向不确定性下限 (Low)",
    ][::-1]
    lbnl_twh = [843, 782, 664, 649, 590, 578, 521][::-1]
    yl = np.arange(len(lbnl_scens))

    ax2.barh(yl, lbnl_twh, height=0.48, color=[SLATE, SLATE, SLATE, NAVY, TEAL, AMBER, CRIMSON][::-1])
    for yi, tv in zip(yl, lbnl_twh):
        mult = tv / 192.0
        ax2.text(tv + 14, yi, f"{tv} TWh（为2024年192 TWh的 {mult:.2f}倍）", va="center", ha="left", fontsize=6.4, color=NAVY, bbox=WHITE_HALO)
    ax2.set_yticks(yl)
    ax2.set_yticklabels(lbnl_scens, fontsize=6.9)
    ax2.set_xlim(0, 1140)
    ax2.set_xlabel("2030年预测用电量 (TWh)", fontsize=7.1, color=SLATE)
    ax2.set_title("美国 2030 年数据中心不同情景下电力需求预测", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_11_4b")


# ===========================================================================
# 12.2 & 12.2B: 17 MIIT Regional Nodes & 12 Local Voucher Policies
# ===========================================================================
def build_chart_12_2():
    fig = plt.figure(figsize=(8.8, 4.9), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    nodes17 = [
        ("1. 北京", 2, "北京互联网交换中心 + 北京移动"),
        ("2. 河北", 1, "中国移动通信集团河北有限公司"),
        ("3. 山西", 3, "山西云时代技术 + 山西联通 + 山西移动"),
        ("4. 内蒙古", 3, "内蒙古大数据集团 + 内蒙古移动 + 内蒙古算网"),
        ("5. 辽宁", 3, "辽宁移动 + 辽宁联通 + 辽宁电信"),
        ("6. 黑龙江", 3, "黑龙江移动 + 黑龙江联通 + 黑龙江电信"),
        ("7. 上海", 3, "上海互联网交换中心 + 上海市新型交换中心 + 上海电信"),
        ("8. 浙江", 2, "浙江省新型互联网交换中心 + 浙江泽悦信息"),
        ("9. 福建", 3, "福建电信 + 福建移动 + 福建省大数据集团"),
        ("10. 湖北", 3, "湖北大数据集团算力 + 湖北省新型交换中心 + 湖北移动"),
        ("11. 广东", 2, "广东省交易控股集团 + 广州互联网交换中心"),
        ("12. 重庆", 3, "重庆两江智慧城投 + 重庆移动 + 重庆电信"),
        ("13. 四川", 3, "成渝（成都）信通院 + 四川电信 + 四川移动"),
        ("14. 贵州", 3, "贵州电信 + 贵州移动 + 贵州联通"),
        ("15. 陕西", 3, "陕西省大数据集团 + 陕西电信 + 陕西时代云"),
        ("16. 甘肃", 3, "甘肃电信 + 甘肃移动 + 甘肃联通"),
        ("17. 宁夏", 3, "宁夏电信 + 宁夏移动 + 宁夏征信有限公司"),
    ][::-1]

    n_names = [x[0] for x in nodes17]
    n_cnts = np.array([x[1] for x in nodes17])
    n_impl = [x[2] for x in nodes17]
    yn = np.arange(len(nodes17))
    n_cols = [NAVY if "交换中心" in im else (TEAL if "大数据" in im or "云时代" in im or "征信" in im else BLUE) for im in n_impl]

    ax2.barh(yn, n_cnts, height=0.58, color=n_cols, alpha=0.90)
    for yi, cnt, im in zip(yn, n_cnts, n_impl):
        ax2.text(cnt + 0.10, yi, f"{cnt}家：{im}", va="center", ha="left", fontsize=6.1, color=NAVY, bbox=WHITE_HALO)

    ax2.set_yticks(yn)
    ax2.set_yticklabels(n_names, fontsize=6.4)
    ax2.set_xlim(0, 8.2)
    ax2.set_ylim(-0.65, 16.65)
    ax2.set_xlabel("联合实施主体数量（家）", fontsize=7.0, color=SLATE)
    ax2.set_title("国家算力互联互通区域节点入选省（区、市）联合实施主体结构", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_12_2")


def build_chart_12_2b():
    fig = plt.figure(figsize=(8.8, 4.3), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="x")
    vouchers12 = [
        ("芜湖：孵化载体中小微(含Token)", 70, "年上限 10 万元"),
        ("黑龙江：省级以上重点课题算力券", 50, "年上限 400 万元"),
        ("芜湖：具身智能等未来产业算力券", 45, "年上限 500 万元"),
        ("湖南：算力/模型/国产适配服务券", 30, "年上限 1,000 万元"),
        ("黑龙江：一般企业算力券", 30, "年上限 400 万元"),
        ("武汉：自主可控算力补贴", 30, "年上限 300 万元"),
        ("上海：模塑申城算力/模型Token/语料券", 30, "按季申报分档核定"),
        ("芜湖：一般企业智算服务算力券", 25, "年上限 500 万元"),
        ("北京：孵化器在孵企业算力创新券", 25, "年上限 50 万元"),
        ("北京：其他科技中小微算力创新券", 25, "年上限 20 万元"),
        ("武汉：非自主可控算力/国产模型Token", 20, "年上限 300 万元"),
        ("宁夏：自治区算力券专项预算", 20, "年度预算 5,000 万元 / 单户上限 200 万元"),
    ][::-1]

    v_names = [x[0] for x in vouchers12]
    v_rates = np.array([x[1] for x in vouchers12])
    v_notes = [x[2] for x in vouchers12]
    yv = np.arange(len(vouchers12))

    ax1.barh(yv, v_rates, height=0.56, color=TEAL, alpha=0.90)
    for yi, rv, vn in zip(yv, v_rates, v_notes):
        ax1.text(rv + 1.2, yi, f"最高 {rv}%（{vn}）", va="center", ha="left", fontsize=6.3, color=NAVY, bbox=WHITE_HALO)

    ax1.set_yticks(yv)
    ax1.set_yticklabels(v_names, fontsize=6.6)
    ax1.set_xlim(0, 106)
    ax1.set_ylim(-0.65, 11.65)
    ax1.set_xlabel("最高补贴比例上限 (%)", fontsize=7.0, color=SLATE)
    ax1.set_title("国内典型省市算力券、模型 Token 券及语料券补贴比例与额度上限对比", loc="left", fontsize=8.8, color=NAVY, pad=12)

    save_chart(fig, "chart_12_2b")


# ===========================================================================
# 12.4 & 12.4B: Policy Evaluation Thresholds & 4-Stage Roadmap
# ===========================================================================
def build_chart_12_4():
    fig = plt.figure(figsize=(8.8, 3.6), facecolor="#FFFFFF")
    ax1 = fig.add_subplot(111)
    style_ax(ax1, grid_axis="y")
    targets = get_input('figure_inputs.json', 'build_chart_12_4', 'targets')
    t_vals = get_input('figure_inputs.json', 'build_chart_12_4', 't_vals')
    xt = np.arange(len(targets))

    ax1.bar(xt, t_vals, width=0.38, color=[SLATE, TEAL, EMERALD, NAVY, BLUE])
    for xi, tv in zip(xt, t_vals):
        ax1.text(xi, tv + 2.6, f"≥{tv}%", ha="center", va="bottom", fontsize=6.6, color=NAVY, bbox=WHITE_HALO)
    ax1.set_xticks(xt)
    ax1.set_xticklabels(targets, fontsize=7.0)
    ax1.set_ylim(0, 98)
    ax1.set_ylabel("目标阈值 (%)", fontsize=7.2, color=SLATE)
    ax1.set_title("国家绿色算力设施评价与数字贸易发展分阶段量化目标对比", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_12_4")


def build_chart_12_4b():
    fig = plt.figure(figsize=(8.8, 3.6), facecolor="#FFFFFF")
    ax2 = fig.add_subplot(111)
    style_ax(ax2, grid_axis="x")
    phases = [
        "第一阶段：验证期 (0~9个月)",
        "第二阶段：试点期 (6~18个月)",
        "第三阶段：放量期 (15~33个月)",
        "第四阶段：升级期 (27~48个月)",
    ][::-1]
    p_start = [0, 6, 15, 27][::-1]
    p_dur = [9, 12, 18, 21][::-1]
    yp = np.arange(len(phases))

    ax2.barh(yp, p_dur, left=p_start, height=0.44, color=[NAVY, TEAL, BLUE, EMERALD][::-1])
    lbls = [
        "0~9个月（来数加工豁免 + 跨时区谷段批量推理）",
        "6~18个月（自贸负面清单 + 前店后厂双节点协同）",
        "15~33个月（17省互联节点 + 650号文绿电直连）",
        "27~48个月（小时级绿电互认 + 百万Token跨境结算）",
    ][::-1]
    for yi, ps, pd, lb in zip(yp, p_start, p_dur, lbls):
        ax2.text(ps + pd + 1.2, yi, lb, va="center", ha="left", fontsize=6.5, color=NAVY, bbox=WHITE_HALO)

    ax2.set_yticks(yp)
    ax2.set_yticklabels(phases, fontsize=7.0)
    ax2.set_xlim(0, 82)
    ax2.set_xlabel("实施推进时间轴（月度里程碑，0至48个月）", fontsize=7.2, color=SLATE)
    ax2.set_title("中国 Token 出海四阶段实施路线图", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_12_4b")


# ===========================================================================
# MOAT METHODOLOGY CHARTS: 6.3_TEA, 9.5C_SOBOL, 11.1B_LMDI
# ===========================================================================
def build_chart_6_3_tea():
    fig = plt.figure(figsize=(8.8, 4.4), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    style_ax(ax, grid_axis="x")

    corridors = [
        "西北绿电基荷 → 东南亚 (S1 中卫/庆阳)",
        "西南水电陆缆 → 东南亚 (S2 贵安/昆明)",
        "北部算力走廊 → 欧洲 (S3 乌兰察布)",
        "东部沿海门户 → 东南亚 (S4 深圳/上海)",
        "新加坡本地部署基准 (L-SG)",
        "法兰克福本地部署基准 (L-EU)",
        "美东弗吉尼亚本地基准 (L-US)",
    ][::-1]
    c_w1 = np.array([0.146, 0.154, 0.150, 0.207, 0.305, 0.291, 0.221])[::-1]
    c_w2 = np.array([0.182, 0.190, 0.191, 0.244, 0.372, 0.355, 0.274])[::-1]
    u_star_w1 = ["临界利用率 26.4%", "临界利用率 27.8%", "临界利用率 28.6%", "临界利用率 36.5%", "本地基准", "本地基准", "本地基准"][::-1]
    u_star_w2 = ["临界利用率 26.8%", "临界利用率 28.1%", "临界利用率 29.8%", "临界利用率 36.2%", "本地基准", "本地基准", "本地基准"][::-1]
    yc = np.arange(len(corridors))

    ax.barh(yc + 0.18, c_w2, height=0.33, color=NAVY, label="W2 在线交互任务（美元/百万合格Token，65%利用率）")
    ax.barh(yc - 0.18, c_w1, height=0.33, color=TEAL, label="W1 异步批处理任务（美元/百万合格Token，65%利用率）")

    for yi, w1, w2, us1, us2 in zip(yc, c_w1, c_w2, u_star_w1, u_star_w2):
        ax.text(w2 + 0.008, yi + 0.18, f"W2: ${w2:.3f}（{us2}）", va="center", ha="left", fontsize=5.9, color=NAVY)
        ax.text(w1 + 0.008, yi - 0.18, f"W1: ${w1:.3f}（{us1}）", va="center", ha="left", fontsize=5.9, color=TEAL)

    ax.set_yticks(yc)
    ax.set_yticklabels(corridors, fontsize=6.9)
    ax.set_xlim(0, 0.50)
    ax.set_ylim(-0.65, 6.65)
    ax.set_xlabel("单位合格 Token 全口径交付成本（USD / 百万 Token）", fontsize=7.1, color=SLATE)
    ax.set_title("境内四大供给节点与海外三大本地基准的单位合格 Token 交付成本及临界利用率对比", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_6_3_tea")


def build_chart_9_5c_sobol():
    fig = plt.figure(figsize=(8.8, 4.1), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    style_ax(ax, grid_axis="x")

    params = [
        "有效业务利用率 u (30%至85%)",
        "年化硬件与机房资本成本 ($4.5万至$7.5万/节点年)",
        "KV缓存命中率与工程效率 η (15%至80%)",
        "综合到户电价 ($0.042至$0.220/kWh)",
        "跨境通信与端口费率 ($0.010至$0.085/1M)",
        "机房电能利用效率 PUE (1.15至1.42)",
    ][::-1]
    s_first = np.array([71.17, 13.72, 8.81, 3.16, 0.69, 0.08])[::-1]
    s_total = np.array([73.36, 15.06, 9.63, 3.24, 0.69, 0.09])[::-1]
    yp = np.arange(len(params))

    ax.barh(yp + 0.18, s_total, height=0.33, color=NAVY, label="全效应敏感性指数 STi（含耦合交互效应，%）")
    ax.barh(yp - 0.18, s_first, height=0.33, color=TEAL, label="一阶主效应指数 Si（独立方差贡献，%）")

    for yi, sf, st in zip(yp, s_first, s_total):
        inter = st - sf
        inter_str = f"（交互 +{inter:.2f}%）"
        ax.text(st + 1.0, yi + 0.18, f"全效应 {st:.2f}%{inter_str}", va="center", ha="left", fontsize=6.0, color=NAVY)
        ax.text(sf + 1.0, yi - 0.18, f"一阶主效应 {sf:.2f}%", va="center", ha="left", fontsize=6.0, color=TEAL)

    ax.set_yticks(yp)
    ax.set_yticklabels(params, fontsize=6.8)
    ax.set_xlim(0, 102)
    ax.set_ylim(-0.65, 5.65)
    ax.set_xlabel("全局方差解释贡献率 (%)", fontsize=7.1, color=SLATE)
    ax.set_title("基于 32,768 组随机样本条件均值与 Jansen 估计的单位 Token 成本全局敏感性指数分布", loc="left", fontsize=8.8, color=NAVY, pad=20)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, frameon=False, fontsize=6.7)

    save_chart(fig, "chart_9_5c_sobol")


def build_chart_11_1b_lmdi():
    fig = plt.figure(figsize=(8.8, 4.0), facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    style_ax(ax, grid_axis="y")

    steps = get_input('figure_inputs.json', 'build_chart_11_1b_lmdi', 'steps')
    vals = get_input('figure_inputs.json', 'build_chart_11_1b_lmdi', 'vals')
    bottoms = get_input('figure_inputs.json', 'build_chart_11_1b_lmdi', 'bottoms')
    cols = [NAVY, CRIMSON, AMBER, EMERALD, TEAL, NAVY]
    shares = get_input('figure_inputs.json', 'build_chart_11_1b_lmdi', 'shares')
    xs = np.arange(len(steps))

    for xi, b, v, c, sh in zip(xs, bottoms, vals, cols, shares):
        ax.bar(xi, abs(v), bottom=b, width=0.42, color=c, alpha=0.92)
        top_y = b + abs(v)
        val_txt = f"{v:+.1f} TWh\n({sh})" if xi not in (0, 5) else f"{v:.1f} TWh\n({sh})"
        ax.text(xi, top_y + 12, val_txt, ha="center", va="bottom", fontsize=6.1, color=NAVY, bbox=WHITE_HALO)

    ax.set_xticks(xs)
    ax.set_xticklabels(steps, fontsize=6.9)
    ax.set_ylim(0, 640)
    ax.set_ylabel("数据中心年度总用电量 (TWh)", fontsize=7.1, color=SLATE)
    ax.set_title("2024至2030年中国数据中心用电量增长 LMDI 对数平均迪氏指数结构分解", loc="left", fontsize=8.8, color=NAVY, pad=14)

    save_chart(fig, "chart_11_1b_lmdi")


def main():
    print("Rendering the frozen report figures from the supplied figure parameters...")
    build_cover_hero()
    build_chart_es_1()
    build_chart_es_2()
    build_chart_1_1()
    build_chart_1_2_v()
    build_chart_1_3()
    build_chart_1_4()
    build_chart_1_5()
    build_chart_2_1_v()
    build_chart_2_2()
    build_chart_2_3_v()
    build_chart_2_4()
    build_chart_3_1()
    build_chart_3_1b()
    build_chart_3_2()
    build_chart_3_2b()
    build_chart_3_3()
    build_chart_3_3b()
    build_chart_3_5()
    build_chart_3_5b()
    build_chart_4_1()
    build_chart_4_1b()
    build_chart_4_3()
    build_chart_4_3b()
    build_chart_5_2()
    build_chart_5_2b()
    build_chart_5_5()
    build_chart_5_5b()
    build_chart_6_2()
    build_chart_6_2b()
    build_chart_6_3_tea()
    build_chart_6_5()
    build_chart_7_3()
    build_chart_7_3b()
    build_chart_7_5()
    build_chart_7_5b()
    build_chart_8_1()
    build_chart_9_2()
    build_chart_9_2b()
    build_chart_9_3()
    build_chart_9_5()
    build_chart_9_5b()
    build_chart_9_5c_sobol()
    build_chart_10_1()
    build_chart_10_1b()
    build_chart_10_3()
    build_chart_10_3b()
    build_chart_11_1b_lmdi()
    build_chart_11_2()
    build_chart_11_2b()
    build_chart_11_4()
    build_chart_11_4b()
    build_chart_12_2()
    build_chart_12_2b()
    build_chart_12_4()
    build_chart_12_4b()
    print("Report figure rendering finished.")


if __name__ == "__main__":
    main()


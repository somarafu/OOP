"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
시도별 주거환경 만족도 광역지표
결론 중심 버전:
"기술이 아니라 배분이 도시의 수준을 결정한다"

실행:
streamlit run dashboard.py

필요 파일:
- dashboard.py
- data/현재_거주_지역의_주거환경_만족도_20260523172214.csv
  또는
- data/현재_거주_지역의_주거환경_만족도_20260523172214(1).csv

requirements.txt:
streamlit
pandas
numpy
plotly
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="시도별 주거환경 만족도 광역지표",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_CANDIDATES = [
    Path("data/현재_거주_지역의_주거환경_만족도_20260523172214.csv"),
    Path("data/현재_거주_지역의_주거환경_만족도_20260523172214(1).csv"),
    Path("현재_거주_지역의_주거환경_만족도_20260523172214.csv"),
    Path("현재_거주_지역의_주거환경_만족도_20260523172214(1).csv"),
]

PALETTE = {
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_blue": "#EFF6FF",
    "surface_mint": "#ECFDF5",
    "surface_purple": "#F5F3FF",
    "text": "#111827",
    "muted": "#64748B",
    "line": "#D9E2EC",
    "blue": "#7EA8E6",
    "blue_dark": "#2563EB",
    "mint": "#7BCFA6",
    "green": "#1A7F37",
    "yellow": "#F2D16B",
    "rose": "#F2A6A6",
    "red": "#CF222E",
    "purple": "#BFA7E8",
    "cyan": "#8FD8D2",
    "navy": "#243B53",
}

INDICATOR_TO_ALLOCATION = {
    "생활 인프라": {
        "area": "일반 인프라",
        "emoji": "🏗️",
        "short": "생활SOC·도시 기반시설",
        "color": PALETTE["blue"],
    },
    "대중교통 이용": {
        "area": "일반 인프라",
        "emoji": "🚌",
        "short": "교통 접근성·환승 체계",
        "color": PALETTE["blue"],
    },
    "치안 및 범죄 등 방범 상태": {
        "area": "안전",
        "emoji": "🛡️",
        "short": "치안·방범·재난 대응",
        "color": PALETTE["rose"],
    },
    "위생 환경": {
        "area": "복지·인프라",
        "emoji": "🧼",
        "short": "공공서비스·환경 관리",
        "color": PALETTE["mint"],
    },
    "녹지 공간": {
        "area": "에너지·환경 인프라",
        "emoji": "🌿",
        "short": "친환경 기반·공원·녹지",
        "color": PALETTE["green"],
    },
    "문화/ 부대시설": {
        "area": "교육·생활SOC",
        "emoji": "🎭",
        "short": "문화시설·활동 기회",
        "color": PALETTE["purple"],
    },
    "교육 환경": {
        "area": "교육",
        "emoji": "🎓",
        "short": "학교·학습·청년 기회",
        "color": PALETTE["purple"],
    },
    "이웃과의 관계": {
        "area": "복지·안전",
        "emoji": "🤝",
        "short": "공동체·생활 안정성",
        "color": PALETTE["yellow"],
    },
}


# ============================================================
# CSS
# ============================================================
st.markdown(
    f"""
<style>
.stApp {{
    background: {PALETTE["bg"]};
    color: {PALETTE["text"]};
}}

.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%);
    border-right: 1px solid {PALETTE["line"]};
}}

section[data-testid="stSidebar"] * {{
    color: {PALETTE["text"]} !important;
}}

h1, h2, h3, h4, p, li, label, span {{
    color: {PALETTE["text"]};
}}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricValue"],
div[data-testid="stMetricDelta"] {{
    color: {PALETTE["text"]} !important;
}}

.hero {{
    background:
        radial-gradient(circle at 8% 14%, rgba(191,167,232,0.25) 0, rgba(191,167,232,0.00) 34%),
        radial-gradient(circle at 92% 18%, rgba(126,168,230,0.23) 0, rgba(126,168,230,0.00) 32%),
        linear-gradient(135deg, #EEF6FF 0%, #F3FBF8 55%, #FAF7FF 100%);
    border: 1px solid #D7E5F4;
    border-radius: 28px;
    padding: 28px 32px;
    box-shadow: 0 14px 30px rgba(36,59,83,0.08);
    margin-bottom: 22px;
}}

.hero-grid {{
    display: grid;
    grid-template-columns: 1.25fr 0.75fr;
    gap: 34px;
    align-items: center;
}}

.hero-eyebrow {{
    display: inline-block;
    background: rgba(126,168,230,0.18);
    color: #2563EB;
    border: 1px solid rgba(126,168,230,0.28);
    border-radius: 999px;
    padding: 7px 13px;
    font-size: 0.78rem;
    font-weight: 900;
    margin-bottom: 12px;
}}

.hero-title {{
    font-size: 2.05rem;
    line-height: 1.26;
    font-weight: 950;
    letter-spacing: -0.04em;
    margin-bottom: 12px;
}}

.hero-subtitle {{
    color: #64748B;
    font-size: 0.96rem;
    line-height: 1.62;
    max-width: 820px;
}}

.hero-panel {{
    background: rgba(255,255,255,0.82);
    border: 1px solid #D8E6F4;
    border-radius: 22px;
    padding: 16px 18px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.90);
}}

.hero-row {{
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: center;
    border-bottom: 1px solid #E1EAF4;
    padding: 9px 0;
    font-weight: 850;
    font-size: 0.94rem;
}}

.hero-row:last-child {{
    border-bottom: none;
}}

.hero-value {{
    font-weight: 950;
    color: #1D4ED8;
    text-align: right;
}}

.metric-card {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
    border: 1px solid #DCE8F5;
    border-radius: 20px;
    padding: 16px 18px;
    min-height: 132px;
    box-shadow: 0 9px 20px rgba(15,23,42,0.045);
}}

.metric-title {{
    font-size: 0.9rem;
    font-weight: 850;
    color: {PALETTE["muted"]};
    margin-bottom: 8px;
}}

.metric-value {{
    font-size: 1.62rem;
    font-weight: 950;
    color: #111827;
    line-height: 1.12;
}}

.metric-desc {{
    font-size: 0.84rem;
    color: #64748B;
    margin-top: 8px;
    line-height: 1.42;
}}

.small-label {{
    display: inline-block;
    padding: 0.28rem 0.7rem;
    border-radius: 999px;
    background: #DBEAFE;
    color: #1D4ED8;
    font-size: 0.75rem;
    font-weight: 900;
    margin-bottom: 0.5rem;
}}

.section-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["line"]};
    border-radius: 24px;
    padding: 22px 24px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.06);
    height: 100%;
}}

.section-title {{
    font-size: 1.25rem;
    font-weight: 950;
    margin-bottom: 10px;
}}

.section-text {{
    color: {PALETTE["muted"]};
    line-height: 1.72;
    font-size: 0.98rem;
}}

.conclusion-box {{
    background: linear-gradient(135deg, #243B53 0%, #2563EB 100%);
    border-radius: 26px;
    padding: 25px 28px;
    margin: 24px 0 18px;
    box-shadow: 0 16px 32px rgba(37,99,235,0.20);
}}

.conclusion-box * {{
    color: white !important;
}}

.conclusion-title {{
    font-size: 1.45rem;
    font-weight: 950;
    margin-bottom: 8px;
}}

.conclusion-text {{
    line-height: 1.7;
    opacity: 0.96;
}}

.flow-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin: 22px 0 12px;
}}

.flow-card {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
    border: 1px solid #DCE8F5;
    border-radius: 22px;
    padding: 18px 20px;
    min-height: 142px;
    box-shadow: 0 9px 20px rgba(15,23,42,0.045);
}}

.flow-num {{
    width: 36px;
    height: 36px;
    border-radius: 14px;
    background: #E3EEFF;
    color: #2563EB !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 950;
    margin-bottom: 10px;
}}

.flow-title {{
    font-size: 1.08rem;
    font-weight: 950;
    margin-bottom: 7px;
}}

.flow-text {{
    color: #64748B;
    font-size: 0.88rem;
    line-height: 1.52;
}}

.policy-map-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["line"]};
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 12px;
}}

.policy-map-head {{
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 7px;
}}

.policy-map-emoji {{
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #EFF6FF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}}

.policy-map-title {{
    font-weight: 950;
    font-size: 1.03rem;
}}

.policy-map-sub {{
    color: {PALETTE["muted"]};
    font-size: 0.9rem;
    line-height: 1.55;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 0.35rem;
    background: #EEF4FB;
    border-radius: 16px;
    padding: 6px;
    margin-top: 10px;
}}

.stTabs [data-baseweb="tab"] {{
    color: {PALETTE["muted"]};
    font-weight: 850;
    border-radius: 12px;
    padding: 10px 15px;
}}

.stTabs [aria-selected="true"] {{
    color: {PALETTE["text"]} !important;
    background: white;
    box-shadow: 0 4px 12px rgba(15,23,42,0.06);
}}

[data-testid="stDataFrame"] * {{
    color: {PALETTE["text"]} !important;
}}

.plot-container text {{
    fill: {PALETTE["text"]} !important;
}}

@media (max-width: 900px) {{
    .hero-grid, .flow-grid {{
        grid-template-columns: 1fr;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 데이터 로드
# ============================================================
def find_data_path():
    for path in DATA_CANDIDATES:
        if path.exists():
            return path
    return None


@st.cache_data
def load_housing_satisfaction(path):
    try:
        raw = pd.read_csv(path, encoding="cp949")
    except UnicodeDecodeError:
        raw = pd.read_csv(path, encoding="utf-8-sig")

    indicator_names = raw.iloc[0, 2:].tolist()
    df = raw[raw["특성별(1)"] == "지역별"].copy()
    df.columns = ["category", "region"] + indicator_names
    df = df.drop(columns=["category"])

    for col in df.columns:
        if col != "region":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    indicator_cols = [col for col in df.columns if col != "region"]
    df["종합 주거환경 만족도"] = df[indicator_cols].mean(axis=1)

    return df, indicator_cols


data_path = find_data_path()
if data_path is None:
    st.error(
        "데이터 파일을 찾을 수 없습니다. CSV 파일을 아래 위치 중 하나에 넣어주세요.\n\n"
        "- data/현재_거주_지역의_주거환경_만족도_20260523172214.csv\n"
        "- data/현재_거주_지역의_주거환경_만족도_20260523172214(1).csv"
    )
    st.stop()

df, indicator_cols = load_housing_satisfaction(data_path)

region_group_map = {
    "서울": "수도권",
    "인천": "수도권",
    "경기": "수도권",
    "대전": "중부권",
    "세종": "중부권",
    "충북": "중부권",
    "충남": "중부권",
    "광주": "호남권",
    "전북": "호남권",
    "전남": "호남권",
    "대구": "대경권",
    "경북": "대경권",
    "부산": "동남권",
    "울산": "동남권",
    "경남": "동남권",
    "강원": "강원권",
    "제주": "제주권",
}

df["권역"] = df["region"].map(region_group_map).fillna("기타")


# ============================================================
# Plotly 스타일 함수
# ============================================================
def style_plotly_chart(fig, height=500):
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=PALETTE["text"], size=13),
        title_font=dict(color=PALETTE["text"], size=19),
        xaxis=dict(
            title_font=dict(color=PALETTE["text"]),
            tickfont=dict(color=PALETTE["text"]),
            gridcolor="#D9E2EC",
            zerolinecolor="#D9E2EC",
            linecolor="#94A3B8",
        ),
        yaxis=dict(
            title_font=dict(color=PALETTE["text"]),
            tickfont=dict(color=PALETTE["text"]),
            gridcolor="#D9E2EC",
            zerolinecolor="#D9E2EC",
            linecolor="#94A3B8",
        ),
        legend=dict(
            title_font=dict(color=PALETTE["text"]),
            font=dict(color=PALETTE["text"]),
        ),
        margin=dict(l=44, r=44, t=72, b=44),
    )
    return fig


def style_heatmap(fig, height=550):
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=PALETTE["text"], size=12),
        title_font=dict(color=PALETTE["text"], size=19),
        xaxis=dict(
            title_font=dict(color=PALETTE["text"]),
            tickfont=dict(color=PALETTE["text"]),
        ),
        yaxis=dict(
            title_font=dict(color=PALETTE["text"]),
            tickfont=dict(color=PALETTE["text"]),
        ),
        coloraxis_colorbar=dict(
            title_font=dict(color=PALETTE["text"]),
            tickfont=dict(color=PALETTE["text"]),
        ),
        margin=dict(l=44, r=44, t=72, b=44),
    )
    return fig


def style_polar_chart(fig, height=520):
    fig.update_polars(
        radialaxis=dict(
            range=[0, 5],
            tickfont=dict(color=PALETTE["text"]),
            gridcolor="#D9E2EC",
            linecolor=PALETTE["text"],
        ),
        angularaxis=dict(
            tickfont=dict(color=PALETTE["text"], size=13),
            linecolor=PALETTE["text"],
            gridcolor="#D9E2EC",
        ),
        bgcolor="white",
    )
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=PALETTE["text"], size=13),
        title_font=dict(color=PALETTE["text"], size=19),
        margin=dict(l=84, r=84, t=82, b=82),
    )
    return fig


# ============================================================
# 분석 보조 함수
# ============================================================
def get_weak_indicators(row, n=3):
    return row[indicator_cols].sort_values(ascending=True).head(n)


def get_strong_indicators(row, n=3):
    return row[indicator_cols].sort_values(ascending=False).head(n)


def get_allocation_count_table():
    rows = []
    for _, row in df.iterrows():
        weak = get_weak_indicators(row, 3)
        for indicator, score in weak.items():
            info = INDICATOR_TO_ALLOCATION.get(indicator)
            if info:
                rows.append(
                    {
                        "region": row["region"],
                        "취약 지표": indicator,
                        "만족도": score,
                        "배분 영역": info["area"],
                    }
                )
    weak_df = pd.DataFrame(rows)

    if weak_df.empty:
        return weak_df, pd.DataFrame(columns=["배분 영역", "빈도"])

    count_df = (
        weak_df.groupby("배분 영역")
        .size()
        .reset_index(name="빈도")
        .sort_values("빈도", ascending=False)
    )

    return weak_df, count_df


def render_metric_card(title, value, desc):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_distribution_flow():
    st.markdown(
        """
        <div class="flow-grid">
            <div class="flow-card">
                <div class="flow-num">1</div>
                <div class="flow-title">지역마다 차이가 있다</div>
                <div class="flow-text">
                    종합 만족도와 세부 지표는 시도마다 다르게 나타납니다.
                </div>
            </div>
            <div class="flow-card">
                <div class="flow-num">2</div>
                <div class="flow-title">부족한 지표도 다르다</div>
                <div class="flow-text">
                    어떤 곳은 교통, 어떤 곳은 교육·녹지·방범이 더 취약합니다.
                </div>
            </div>
            <div class="flow-card">
                <div class="flow-num">3</div>
                <div class="flow-title">결국 배분의 문제다</div>
                <div class="flow-text">
                    도시 수준은 필요한 자원을 어디에 우선 두는지에 따라 달라집니다.
                </div>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 사이드바
# ============================================================
st.sidebar.title("분석 설정")

view_mode = st.sidebar.radio(
    "보기 방식",
    ["차트 중심", "수치표 중심"],
    index=0,
)

selected_groups = st.sidebar.multiselect(
    "권역 선택",
    options=["전체"] + sorted(df["권역"].unique().tolist()),
    default=["전체"],
)

selected_indicator = st.sidebar.selectbox(
    "대표 지표 선택",
    ["종합 주거환경 만족도"] + indicator_cols,
)

sort_order = st.sidebar.radio(
    "정렬 기준",
    ["높은 순", "낮은 순"],
    horizontal=True,
)

top_n = st.sidebar.slider(
    "표시할 지역 수",
    min_value=5,
    max_value=len(df),
    value=len(df),
)

if "전체" in selected_groups:
    filtered_df = df.copy()
else:
    filtered_df = df[df["권역"].isin(selected_groups)].copy()

ascending = True if sort_order == "낮은 순" else False
filtered_df = filtered_df.sort_values(selected_indicator, ascending=ascending).head(top_n)


# ============================================================
# 핵심 지표 계산
# ============================================================
full_avg = df["종합 주거환경 만족도"].mean()
top_region = df.loc[df["종합 주거환경 만족도"].idxmax()]
low_region = df.loc[df["종합 주거환경 만족도"].idxmin()]
gap = top_region["종합 주거환경 만족도"] - low_region["종합 주거환경 만족도"]
indicator_avg = df[indicator_cols].mean().sort_values(ascending=False)
indicator_std = df[indicator_cols].std().sort_values(ascending=False)
most_divided_indicator = indicator_std.index[0]
lowest_avg_indicator = indicator_avg.index[-1]
weak_df, allocation_count_df = get_allocation_count_table()


# ============================================================
# 헤더
# ============================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="hero-eyebrow">Regional Housing Satisfaction Dashboard</div>
                <div class="hero-title">도시 만족도의 차이는<br>배분의 차이를 보여준다.</div>
                <div class="hero-subtitle">
                    생활 인프라, 교통, 방범, 위생, 녹지, 문화, 교육, 이웃 관계를 비교해
                    도시 수준이 단순한 기술 보유가 아니라 <b>자원이 어디에 배분되었는지</b>와 연결됨을 확인합니다.
                </div>
            </div>
            <div class="hero-panel">
                <div class="hero-row"><span>전국 평균</span><span class="hero-value">{full_avg:.2f} / 5</span></div>
                <div class="hero-row"><span>최고 지역</span><span class="hero-value">{top_region["region"]} {top_region["종합 주거환경 만족도"]:.2f}</span></div>
                <div class="hero-row"><span>최저 지역</span><span class="hero-value">{low_region["region"]} {low_region["종합 주거환경 만족도"]:.2f}</span></div>
                <div class="hero-row"><span>격차</span><span class="hero-value">{gap:.2f}점</span></div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    render_metric_card("전국 평균", f"{full_avg:.2f} / 5", "8개 지표 평균")

with c2:
    render_metric_card("지역 간 격차", f"{gap:.2f}점", f"{top_region['region']} - {low_region['region']}")

with c3:
    render_metric_card("가장 낮은 지표", lowest_avg_indicator, f"전국 평균 {indicator_avg[lowest_avg_indicator]:.2f}점")

with c4:
    render_metric_card("차이가 큰 지표", most_divided_indicator, f"표준편차 {indicator_std[most_divided_indicator]:.2f}")

render_distribution_flow()

st.markdown(
    """
    <div class="conclusion-box">
        <div class="conclusion-title">중간 결론</div>
        <div class="conclusion-text">
            도시별 취약 지표가 다르다는 것은 필요한 자원도 다르다는 뜻입니다.
            좋은 도시는 기술을 많이 넣은 도시가 아니라, 필요한 곳에 자원을 정확히 배분한 도시입니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "종합 격차",
        "지표 구조",
        "권역 패턴",
        "도시별 진단",
        "결론 도출",
    ]
)


# ============================================================
# TAB 1. 종합 격차
# ============================================================
with tab1:
    st.markdown('<span class="small-label">Gap Overview</span>', unsafe_allow_html=True)
    st.subheader("시도별 종합 주거환경 만족도")

    if view_mode == "차트 중심":
        fig = px.bar(
            filtered_df,
            x="region",
            y=selected_indicator,
            color=selected_indicator,
            text=selected_indicator,
            color_continuous_scale="Blues",
            title=f"시도별 {selected_indicator}",
            labels={"region": "시도", selected_indicator: "만족도"},
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            marker_line_width=0.7,
            marker_line_color="white",
            textfont=dict(color=PALETTE["text"]),
        )
        fig.add_hline(
            y=full_avg if selected_indicator == "종합 주거환경 만족도" else df[selected_indicator].mean(),
            line_dash="dash",
            line_color=PALETTE["red"],
            annotation_text="전국 평균",
            annotation_position="top left",
            annotation_font_color=PALETTE["text"],
        )
        fig = style_plotly_chart(fig, height=520)
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(
            filtered_df[["권역", "region", selected_indicator]].reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    col_left, col_right = st.columns([1.15, 1])

    with col_left:
        st.subheader("상위·하위 지역 비교")

        rank_df = df.sort_values("종합 주거환경 만족도", ascending=False)
        top5 = rank_df.head(5)[["region", "종합 주거환경 만족도"]].copy()
        low5 = rank_df.tail(5)[["region", "종합 주거환경 만족도"]].copy()
        top5["구분"] = "상위 5개"
        low5["구분"] = "하위 5개"
        compare_df = pd.concat([top5, low5], axis=0)

        fig = px.bar(
            compare_df,
            x="종합 주거환경 만족도",
            y="region",
            color="구분",
            orientation="h",
            text="종합 주거환경 만족도",
            title="종합 만족도 상위·하위 지역",
            color_discrete_map={"상위 5개": PALETTE["blue"], "하위 5개": PALETTE["rose"]},
            labels={"region": "시도", "종합 주거환경 만족도": "만족도"},
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(color=PALETTE["text"]),
        )
        fig = style_plotly_chart(fig, height=430)
        fig.update_xaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("전국 평균 대비 분포")

        fig = go.Figure()
        fig.add_trace(
            go.Box(
                y=df["종합 주거환경 만족도"],
                name="분포",
                boxpoints="all",
                jitter=0.35,
                pointpos=-1.8,
                text=df["region"],
                marker=dict(size=8, color=PALETTE["blue"]),
                line=dict(color=PALETTE["navy"]),
                fillcolor="#EAF4FF",
            )
        )
        fig.add_hline(
            y=full_avg,
            line_dash="dash",
            line_color=PALETTE["red"],
            annotation_text=f"전국 평균 {full_avg:.2f}",
            annotation_position="top left",
            annotation_font_color=PALETTE["text"],
        )
        fig.update_layout(title="시도별 종합 만족도 분포", yaxis_title="만족도")
        fig = style_plotly_chart(fig, height=430)
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2. 지표 구조
# ============================================================
with tab2:
    st.markdown('<span class="small-label">Indicator Structure</span>', unsafe_allow_html=True)
    st.subheader("세부 지표가 보여주는 배분의 흔적")

    col1, col2 = st.columns([1.18, 1])

    with col1:
        heatmap_df = df.set_index("region")[indicator_cols]

        fig = px.imshow(
            heatmap_df,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="YlGnBu",
            title="시도별 세부 주거환경 만족도 히트맵",
            labels={"x": "지표", "y": "시도", "color": "만족도"},
            zmin=3,
            zmax=5,
        )
        fig.update_traces(textfont=dict(color=PALETTE["text"]))
        fig = style_heatmap(fig, height=620)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        indicator_summary = pd.DataFrame(
            {
                "지표": indicator_avg.index,
                "전국 평균": indicator_avg.values,
                "지역 차이": [indicator_std[i] for i in indicator_avg.index],
            }
        ).sort_values("전국 평균", ascending=True)

        fig = px.bar(
            indicator_summary,
            x="전국 평균",
            y="지표",
            orientation="h",
            text="전국 평균",
            title="전국 평균이 낮은 지표",
            color="전국 평균",
            color_continuous_scale="Blues",
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(color=PALETTE["text"]),
        )
        fig = style_plotly_chart(fig, height=620)
        fig.update_xaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("지역별 차이가 큰 지표")
        std_df = indicator_std.reset_index()
        std_df.columns = ["지표", "표준편차"]

        fig = px.bar(
            std_df.sort_values("표준편차"),
            x="표준편차",
            y="지표",
            orientation="h",
            text="표준편차",
            title="지표별 지역 간 편차",
            color="표준편차",
            color_continuous_scale="Purples",
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(color=PALETTE["text"]),
        )
        fig = style_plotly_chart(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("선택 지표 상세 순위")
        selected_detail_indicator = st.selectbox(
            "상세 비교할 지표",
            indicator_cols,
            key="detail_indicator",
        )

        detail_df = df.sort_values(selected_detail_indicator, ascending=False)

        fig = px.line(
            detail_df,
            x="region",
            y=selected_detail_indicator,
            markers=True,
            title=f"{selected_detail_indicator} 시도별 비교",
            labels={"region": "시도", selected_detail_indicator: "만족도"},
        )
        fig.add_hline(
            y=detail_df[selected_detail_indicator].mean(),
            line_dash="dash",
            line_color=PALETTE["red"],
            annotation_text="평균",
            annotation_position="top left",
            annotation_font_color=PALETTE["text"],
        )
        fig.update_traces(
            line=dict(width=3, color=PALETTE["blue_dark"]),
            marker=dict(size=9, color=PALETTE["blue_dark"]),
        )
        fig = style_plotly_chart(fig, height=430)
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 3. 권역 패턴
# ============================================================
with tab3:
    st.markdown('<span class="small-label">Regional Pattern</span>', unsafe_allow_html=True)
    st.subheader("권역별 주거환경 만족도 패턴")

    group_df = df.groupby("권역")[["종합 주거환경 만족도"] + indicator_cols].mean().reset_index()

    col1, col2 = st.columns([1, 1])

    with col1:
        fig = px.bar(
            group_df.sort_values("종합 주거환경 만족도", ascending=False),
            x="권역",
            y="종합 주거환경 만족도",
            color="종합 주거환경 만족도",
            text="종합 주거환경 만족도",
            color_continuous_scale="Blues",
            title="권역별 종합 주거환경 만족도",
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(color=PALETTE["text"]),
        )
        fig = style_plotly_chart(fig, height=450)
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        group_heatmap = group_df.set_index("권역")[indicator_cols]

        fig = px.imshow(
            group_heatmap,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="PuBuGn",
            title="권역별 세부 지표 히트맵",
            zmin=3,
            zmax=5,
        )
        fig.update_traces(textfont=dict(color=PALETTE["text"]))
        fig = style_heatmap(fig, height=450)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("권역별 강점·약점 요약")

    summary_rows = []
    for _, row in group_df.iterrows():
        weak = row[indicator_cols].idxmin()
        strong = row[indicator_cols].idxmax()
        summary_rows.append(
            {
                "권역": row["권역"],
                "강점 지표": strong,
                "강점 점수": round(row[strong], 2),
                "취약 지표": weak,
                "취약 점수": round(row[weak], 2),
            }
        )

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ============================================================
# TAB 4. 도시별 진단
# ============================================================
with tab4:
    st.markdown('<span class="small-label">City Diagnosis</span>', unsafe_allow_html=True)
    st.subheader("도시별 주거환경 프로필")

    selected_city = st.selectbox("도시 선택", df["region"].tolist())
    city_row = df[df["region"] == selected_city].iloc[0]

    city_score = city_row["종합 주거환경 만족도"]
    city_rank = (
        df["종합 주거환경 만족도"]
        .rank(ascending=False, method="min")[df["region"] == selected_city]
        .iloc[0]
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("선택 도시", selected_city)
    col2.metric("종합 만족도", f"{city_score:.2f} / 5")
    col3.metric("전국 순위", f"{int(city_rank)}위 / {len(df)}개")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        radar_df = pd.DataFrame(
            {
                "지표": indicator_cols,
                "만족도": [city_row[col] for col in indicator_cols],
            }
        )

        fig = px.line_polar(
            radar_df,
            r="만족도",
            theta="지표",
            line_close=True,
            title=f"{selected_city} 주거환경 레이더차트",
        )
        fig.update_traces(
            fill="toself",
            line=dict(width=3, color=PALETTE["blue_dark"]),
            fillcolor="rgba(126,168,230,0.22)",
        )
        fig = style_polar_chart(fig, height=520)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        city_indicator_df = pd.DataFrame(
            {
                "지표": indicator_cols,
                "만족도": [city_row[col] for col in indicator_cols],
                "전국 평균": [df[col].mean() for col in indicator_cols],
            }
        )
        city_indicator_df["평균 대비"] = city_indicator_df["만족도"] - city_indicator_df["전국 평균"]

        fig = px.bar(
            city_indicator_df.sort_values("평균 대비"),
            x="평균 대비",
            y="지표",
            orientation="h",
            color="평균 대비",
            color_continuous_scale="RdBu",
            title=f"{selected_city}의 전국 평균 대비 강점·약점",
        )
        fig.add_vline(x=0, line_dash="dash", line_color=PALETTE["text"])
        fig = style_plotly_chart(fig, height=520)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("이 도시의 취약 지표는 어떤 배분 영역을 가리키는가?")

    weak_items = get_weak_indicators(city_row, 3)

    for indicator, score in weak_items.items():
        info = INDICATOR_TO_ALLOCATION.get(indicator)
        if info is None:
            continue

        st.markdown(
            f"""
            <div class="policy-map-card">
                <div class="policy-map-head">
                    <div class="policy-map-emoji">{info["emoji"]}</div>
                    <div>
                        <div class="policy-map-title">{indicator} {score:.2f}점 → {info["area"]}</div>
                        <div class="policy-map-sub">{info["short"]}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 5. 결론 도출
# ============================================================
with tab5:
    st.markdown('<span class="small-label">Conclusion</span>', unsafe_allow_html=True)
    st.subheader("왜 ‘기술’보다 ‘배분’인가?")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">핵심 논리</div>
                <div class="section-text">
                    주거환경 만족도는 하나의 기술 점수가 아닙니다.
                    교통, 교육, 방범, 녹지, 문화처럼 서로 다른 생활 조건의 조합입니다.
                    따라서 낮은 만족도는 ‘기술 부족’보다 ‘필요한 영역에 자원이 충분히 배분되지 않은 상태’로 해석할 수 있습니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">시각화가 보여준 것</div>
                <div class="section-text">
                    지역별 순위는 다르고, 지표별 취약점도 다릅니다.
                    어떤 도시는 교통이, 어떤 도시는 교육이나 녹지가 더 낮습니다.
                    결국 좋은 도시는 같은 기술을 똑같이 넣은 도시가 아니라
                    필요한 곳에 필요한 자원을 배치한 도시입니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    col_a, col_b = st.columns([1.1, 1])

    with col_a:
        st.subheader("취약 지표가 모이는 배분 영역")

        if not allocation_count_df.empty:
            fig = px.bar(
                allocation_count_df.sort_values("빈도"),
                x="빈도",
                y="배분 영역",
                orientation="h",
                text="빈도",
                title="지역별 하위 3개 지표를 배분 영역으로 변환",
                color="빈도",
                color_continuous_scale="Blues",
            )
            fig.update_traces(
                textposition="outside",
                textfont=dict(color=PALETTE["text"]),
            )
            fig = style_plotly_chart(fig, height=430)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("배분 영역으로 변환할 취약 지표가 없습니다.")

    with col_b:
        st.subheader("지표 → 배분 영역 연결표")

        map_rows = []
        for indicator in indicator_cols:
            info = INDICATOR_TO_ALLOCATION.get(indicator)
            if info:
                map_rows.append(
                    {
                        "주거환경 지표": indicator,
                        "배분 영역": info["area"],
                        "해석": info["short"],
                    }
                )

        st.dataframe(pd.DataFrame(map_rows), use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="conclusion-box">
            <div class="conclusion-title">최종 결론</div>
            <div class="conclusion-text">
                도시의 수준은 기술의 양만으로 결정되지 않습니다.
                시민이 체감하는 주거환경은 생활 인프라, 교통, 교육, 안전, 녹지처럼
                서로 다른 자원이 어떻게 배분되었는지에 따라 달라집니다.
                <br><br>
                <b>기술이 아니라 배분이 도시의 수준을 결정한다.</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 하단 데이터 표
# ============================================================
with st.expander("전처리 데이터 보기"):
    st.dataframe(
        df.sort_values("종합 주거환경 만족도", ascending=False),
        use_container_width=True,
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="전처리 데이터 CSV 다운로드",
        data=csv,
        file_name="housing_satisfaction_processed.csv",
        mime="text/csv",
    )

"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
시도별 주거환경 만족도 광역지표
→ 예산 및 에너지 배분 시뮬레이션으로 이어지는 전환형 대시보드

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

SIMULATION_URL = "https://gdp-dashboard-djcuxtlb7y.streamlit.app/"

DATA_CANDIDATES = [
    Path("data/현재_거주_지역의_주거환경_만족도_20260523172214.csv"),
    Path("data/현재_거주_지역의_주거환경_만족도_20260523172214(1).csv"),
    Path("현재_거주_지역의_주거환경_만족도_20260523172214.csv"),
    Path("현재_거주_지역의_주거환경_만족도_20260523172214(1).csv"),
]

PALETTE = {
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_2": "#EEF6FF",
    "surface_3": "#F4F7FB",
    "text": "#111827",
    "muted": "#64748B",
    "line": "#D9E2EC",
    "navy": "#243B53",
    "blue": "#7EA8E6",
    "blue_dark": "#2563EB",
    "mint": "#7BCFA6",
    "green": "#1A7F37",
    "yellow": "#F2D16B",
    "rose": "#F2A6A6",
    "red": "#CF222E",
    "purple": "#BFA7E8",
    "cyan": "#8FD8D2",
}

INDICATOR_TO_POLICY = {
    "생활 인프라": {
        "budget": "일반 인프라",
        "energy": "ESS·외부전력망 안정화",
        "reason": "생활 편의 시설과 도시 기반시설 확충이 직접적으로 연결됩니다.",
        "emoji": "🏗️",
    },
    "대중교통 이용": {
        "budget": "일반 인프라",
        "energy": "ESS·전기 교통 인프라",
        "reason": "교통 접근성은 도로, 대중교통, 환승 거점 등 인프라 투입과 관련됩니다.",
        "emoji": "🚌",
    },
    "치안 및 범죄 등 방범 상태": {
        "budget": "안전",
        "energy": "외부전력망·ESS 백업",
        "reason": "치안, 방범, CCTV, 재난 대응 체계가 안전 예산과 연결됩니다.",
        "emoji": "🛡️",
    },
    "위생 환경": {
        "budget": "복지 + 일반 인프라",
        "energy": "에너지 인프라",
        "reason": "위생·환경 관리는 공공서비스와 기반시설 유지 관리가 함께 필요합니다.",
        "emoji": "🧼",
    },
    "녹지 공간": {
        "budget": "에너지 인프라 + 일반 인프라",
        "energy": "태양광·ESS",
        "reason": "녹지와 친환경 인프라는 에너지 자립과 도시 환경 개선을 동시에 보여줍니다.",
        "emoji": "🌿",
    },
    "문화/ 부대시설": {
        "budget": "교육 + 일반 인프라",
        "energy": "ESS",
        "reason": "문화·부대시설은 활동 기회와 생활SOC 투자로 확장됩니다.",
        "emoji": "🎭",
    },
    "교육 환경": {
        "budget": "교육",
        "energy": "ESS·스마트 캠퍼스 인프라",
        "reason": "학교, 평생학습, 직업훈련, 청년 기회와 직접적으로 연결됩니다.",
        "emoji": "🎓",
    },
    "이웃과의 관계": {
        "budget": "복지 + 안전",
        "energy": "지역 커뮤니티 에너지",
        "reason": "공동체 관계는 복지, 안전, 생활권 안정성과 함께 개선됩니다.",
        "emoji": "🤝",
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
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #EAF4FF 0%, #FFFFFF 100%);
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
        radial-gradient(circle at 6% 18%, rgba(191,167,232,0.35) 0, rgba(191,167,232,0.00) 32%),
        linear-gradient(135deg, #D9ECFF 0%, #E8F7F3 52%, #F7F3FF 100%);
    border: 1px solid #CFE0F2;
    border-radius: 28px;
    padding: 30px 34px;
    box-shadow: 0 16px 34px rgba(36,59,83,0.10);
    margin-bottom: 18px;
}}

.hero-grid {{
    display: grid;
    grid-template-columns: 1.35fr 0.85fr;
    gap: 26px;
    align-items: center;
}}

.hero-eyebrow {{
    display: inline-block;
    background: rgba(37,99,235,0.10);
    color: #1D4ED8;
    border: 1px solid rgba(37,99,235,0.18);
    border-radius: 999px;
    padding: 7px 13px;
    font-size: 0.82rem;
    font-weight: 900;
    margin-bottom: 12px;
}}

.hero-title {{
    font-size: 2.35rem;
    line-height: 1.25;
    font-weight: 950;
    letter-spacing: -0.04em;
    margin-bottom: 10px;
}}

.hero-subtitle {{
    color: {PALETTE["muted"]};
    font-size: 1.02rem;
    line-height: 1.75;
    max-width: 920px;
}}

.hero-panel {{
    background: rgba(255,255,255,0.76);
    border: 1px solid #D5E3F3;
    border-radius: 22px;
    padding: 18px 20px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
}}

.hero-row {{
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: center;
    border-bottom: 1px solid #D9E2EC;
    padding: 10px 0;
    font-weight: 800;
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
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["line"]};
    border-radius: 20px;
    padding: 18px 20px;
    height: 150px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.06);
}}

.metric-title {{
    font-size: 0.92rem;
    font-weight: 850;
    color: {PALETTE["muted"]};
    margin-bottom: 8px;
}}

.metric-value {{
    font-size: 2rem;
    font-weight: 950;
    color: {PALETTE["text"]};
    line-height: 1.1;
}}

.metric-desc {{
    font-size: 0.9rem;
    color: {PALETTE["muted"]};
    margin-top: 8px;
    line-height: 1.45;
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

.story-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["line"]};
    border-radius: 24px;
    padding: 22px 24px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.06);
    height: 100%;
}}

.story-title {{
    font-size: 1.25rem;
    font-weight: 950;
    margin-bottom: 10px;
}}

.story-text {{
    color: {PALETTE["muted"]};
    line-height: 1.75;
    font-size: 0.98rem;
}}

.conclusion-box {{
    background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
    border-radius: 24px;
    padding: 26px 28px;
    margin: 24px 0;
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
    line-height: 1.75;
    opacity: 0.95;
}}

.cta-card {{
    background: linear-gradient(135deg, #F0F7FF 0%, #F7F3FF 100%);
    border: 1px solid #C7D7FE;
    border-radius: 24px;
    padding: 24px 26px;
    box-shadow: 0 12px 28px rgba(37,99,235,0.11);
}}

.cta-title {{
    font-size: 1.35rem;
    font-weight: 950;
    margin-bottom: 10px;
}}

.cta-text {{
    color: {PALETTE["muted"]};
    line-height: 1.75;
    margin-bottom: 16px;
}}

.cta-button {{
    display: inline-block;
    background: #2563EB;
    color: white !important;
    text-decoration: none !important;
    padding: 12px 18px;
    border-radius: 14px;
    font-weight: 900;
    box-shadow: 0 8px 18px rgba(37,99,235,0.22);
}}

.cta-button:hover {{
    background: #1D4ED8;
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
    margin-bottom: 8px;
}}

.policy-map-emoji {{
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #EEF6FF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}}

.policy-map-title {{
    font-weight: 950;
    font-size: 1.05rem;
}}

.policy-map-sub {{
    color: {PALETTE["muted"]};
    font-size: 0.9rem;
    line-height: 1.55;
}}

.bridge-step {{
    display: grid;
    grid-template-columns: 42px 1fr;
    gap: 14px;
    align-items: start;
    margin-bottom: 16px;
}}

.bridge-num {{
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #DBEAFE;
    color: #1D4ED8 !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 950;
}}

.bridge-step-title {{
    font-weight: 950;
    margin-bottom: 4px;
}}

.bridge-step-text {{
    color: {PALETTE["muted"]};
    line-height: 1.6;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 0.35rem;
    background: #EEF4FB;
    border-radius: 16px;
    padding: 6px;
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
    .hero-grid {{
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
        "데이터 파일을 찾을 수 없습니다. 아래 둘 중 하나의 위치에 CSV 파일을 넣어주세요.\n\n"
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
        margin=dict(l=40, r=40, t=70, b=40),
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
        margin=dict(l=40, r=40, t=70, b=40),
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
        margin=dict(l=80, r=80, t=80, b=80),
    )
    return fig


# ============================================================
# 분석 보조 함수
# ============================================================
def get_weak_indicators(row, n=3):
    values = row[indicator_cols].sort_values(ascending=True)
    return values.head(n)


def get_strong_indicators(row, n=3):
    values = row[indicator_cols].sort_values(ascending=False)
    return values.head(n)


def policy_recommendation_from_city(row):
    weak = get_weak_indicators(row, 3)
    mapped = []
    for indicator, score in weak.items():
        info = INDICATOR_TO_POLICY.get(
            indicator,
            {
                "budget": "일반 인프라",
                "energy": "ESS",
                "reason": "도시 기반 서비스 개선으로 연결할 수 있습니다.",
                "emoji": "🏙️",
            },
        )
        mapped.append(
            {
                "indicator": indicator,
                "score": score,
                "budget": info["budget"],
                "energy": info["energy"],
                "reason": info["reason"],
                "emoji": info["emoji"],
            }
        )
    return mapped


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


def render_simulation_cta():
    st.markdown(
        f"""
        <div class="cta-card">
            <div class="cta-title">다음 단계: 예산 및 에너지 배분 시뮬레이션으로 이동</div>
            <div class="cta-text">
                광역지표 대시보드는 도시별 만족도 차이를 보여줍니다.
                하지만 차이를 확인하는 것만으로는 정책 판단이 끝나지 않습니다.
                이제 <b>복지, 교육, 에너지 인프라, 일반 인프라, 안전</b> 예산을 어떻게 배분할지,
                그리고 <b>태양광, 수소연료전지, ESS, 외부전력망</b>을 어떻게 조합할지 실험해야 합니다.
            </div>
            <a class="cta-button" href="{SIMULATION_URL}" target="_blank">
                예산 및 에너지 배분 시뮬레이션 열기 →
            </a>
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 대시보드 흐름")
st.sidebar.markdown(
    """
1. 지역별 만족도 격차 확인  
2. 취약 지표 확인  
3. 취약 지표를 예산·에너지 변수로 번역  
4. 시뮬레이션에서 배분 전략 실험  
"""
)
st.sidebar.markdown(
    f"""
<a class="cta-button" href="{SIMULATION_URL}" target="_blank" style="display:block;text-align:center;margin-top:10px;">
시뮬레이션으로 이동
</a>
""",
    unsafe_allow_html=True,
)

if "전체" in selected_groups:
    filtered_df = df.copy()
else:
    filtered_df = df[df["권역"].isin(selected_groups)].copy()

ascending = True if sort_order == "낮은 순" else False
filtered_df = filtered_df.sort_values(selected_indicator, ascending=ascending).head(top_n)


# ============================================================
# 헤더
# ============================================================
full_avg = df["종합 주거환경 만족도"].mean()
top_region = df.loc[df["종합 주거환경 만족도"].idxmax()]
low_region = df.loc[df["종합 주거환경 만족도"].idxmin()]
gap = top_region["종합 주거환경 만족도"] - low_region["종합 주거환경 만족도"]

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="hero-eyebrow">Regional Housing Satisfaction → Policy Allocation Simulator</div>
                <div class="hero-title">시도별 주거환경 만족도는<br>도시의 차이를 보여주고, 배분 시뮬레이션은 그 차이를 바꾸는 방법을 실험합니다.</div>
                <div class="hero-subtitle">
                    이 대시보드는 생활 인프라, 대중교통, 치안, 위생, 녹지, 문화, 교육, 이웃 관계의 만족도를 비교합니다.
                    여기서 확인한 지역 간 격차와 취약 지표를 바탕으로
                    <b>“기술이 아니라 배분이 도시의 수준을 결정한다”</b>는 결론으로 이어지고,
                    다음 단계에서 예산 및 에너지 배분 시뮬레이션을 실행합니다.
                </div>
            </div>
            <div class="hero-panel">
                <div class="hero-row"><span>전국 평균</span><span class="hero-value">{full_avg:.2f} / 5</span></div>
                <div class="hero-row"><span>최고 지역</span><span class="hero-value">{top_region["region"]} {top_region["종합 주거환경 만족도"]:.2f}</span></div>
                <div class="hero-row"><span>최저 지역</span><span class="hero-value">{low_region["region"]} {low_region["종합 주거환경 만족도"]:.2f}</span></div>
                <div class="hero-row"><span>지역 간 격차</span><span class="hero-value">{gap:.2f}점</span></div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 핵심 카드
# ============================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    render_metric_card("전국 평균", f"{full_avg:.2f} / 5", "8개 주거환경 지표 평균")

with c2:
    render_metric_card("만족도 최고 지역", top_region["region"], f"{top_region['종합 주거환경 만족도']:.2f}점")

with c3:
    render_metric_card("만족도 최저 지역", low_region["region"], f"{low_region['종합 주거환경 만족도']:.2f}점")

with c4:
    render_metric_card("지역 간 격차", f"{gap:.2f}점", "최고 지역 - 최저 지역")


st.markdown(
    """
    <div class="conclusion-box">
        <div class="conclusion-title">핵심 결론</div>
        <div class="conclusion-text">
            지역별 만족도 차이는 단순히 도시가 크거나 기술이 많아서 생기는 차이가 아닙니다.
            생활 인프라, 교통, 치안, 녹지, 교육처럼 시민이 체감하는 자원이
            어디에 얼마나 배분되었는지가 도시 만족도의 차이를 만듭니다.
            따라서 다음 질문은 <b>“어떤 기술을 넣을 것인가?”</b>가 아니라
            <b>“한정된 예산과 에너지를 어디에 배분할 것인가?”</b>입니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "종합 현황",
        "지표별 비교",
        "권역 분석",
        "도시 프로필",
        "정책 전환",
        "데이터 표",
    ]
)


# ============================================================
# TAB 1. 종합 현황
# ============================================================
with tab1:
    st.markdown('<span class="small-label">Overview</span>', unsafe_allow_html=True)
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
        fig = style_plotly_chart(fig, height=520)
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(
            filtered_df[["권역", "region", selected_indicator]].reset_index(drop=True),
            use_container_width=True,
        )

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

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

    render_simulation_cta()


# ============================================================
# TAB 2. 지표별 비교
# ============================================================
with tab2:
    st.markdown('<span class="small-label">Indicator Comparison</span>', unsafe_allow_html=True)
    st.subheader("세부 지표별 도시 비교")

    col1, col2 = st.columns([1.2, 1])

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
        indicator_avg = df[indicator_cols].mean().sort_values(ascending=False).reset_index()
        indicator_avg.columns = ["지표", "전국 평균"]

        fig = px.bar(
            indicator_avg,
            x="전국 평균",
            y="지표",
            orientation="h",
            text="전국 평균",
            title="지표별 전국 평균",
            color="전국 평균",
            color_continuous_scale="Teal",
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

    st.info(
        "지표별 비교는 어떤 도시가 낮은지만 보여주는 것이 아니라, "
        "다음 시뮬레이션에서 어떤 예산 항목을 조정해야 하는지 알려주는 출발점입니다."
    )


# ============================================================
# TAB 3. 권역 분석
# ============================================================
with tab3:
    st.markdown('<span class="small-label">Region Group</span>', unsafe_allow_html=True)
    st.subheader("권역별 주거환경 만족도")

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
    st.subheader("권역 구성 비중")

    count_df = df.groupby("권역").size().reset_index(name="지역 수")

    fig = px.treemap(
        count_df,
        path=["권역"],
        values="지역 수",
        title="권역별 포함 시도 수",
        color="지역 수",
        color_continuous_scale="Blues",
    )
    fig.update_traces(textfont=dict(color=PALETTE["text"], size=16))
    fig.update_layout(
        height=430,
        font=dict(color=PALETTE["text"]),
        title_font=dict(color=PALETTE["text"], size=19),
        paper_bgcolor="white",
        margin=dict(l=30, r=30, t=70, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 4. 도시 프로필
# ============================================================
with tab4:
    st.markdown('<span class="small-label">City Profile</span>', unsafe_allow_html=True)
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

    weak_items = city_indicator_df.sort_values("만족도").head(3)
    strong_items = city_indicator_df.sort_values("만족도", ascending=False).head(3)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.warning(f"{selected_city}의 상대적 취약 지표")
        st.dataframe(
            weak_items[["지표", "만족도", "전국 평균", "평균 대비"]],
            use_container_width=True,
        )

    with col_b:
        st.success(f"{selected_city}의 상대적 강점 지표")
        st.dataframe(
            strong_items[["지표", "만족도", "전국 평균", "평균 대비"]],
            use_container_width=True,
        )

    st.markdown("### 취약 지표 → 시뮬레이션 변수로 번역")
    recommendations = policy_recommendation_from_city(city_row)

    for rec in recommendations:
        st.markdown(
            f"""
            <div class="policy-map-card">
                <div class="policy-map-head">
                    <div class="policy-map-emoji">{rec["emoji"]}</div>
                    <div>
                        <div class="policy-map-title">{rec["indicator"]} {rec["score"]:.2f}점 → {rec["budget"]} 예산 조정</div>
                        <div class="policy-map-sub">에너지 방향: {rec["energy"]}</div>
                    </div>
                </div>
                <div class="policy-map-sub">{rec["reason"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_simulation_cta()


# ============================================================
# TAB 5. 정책 전환
# ============================================================
with tab5:
    st.markdown('<span class="small-label">Bridge to Simulation</span>', unsafe_allow_html=True)
    st.subheader("광역지표에서 예산·에너지 배분 시뮬레이션으로")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(
            """
            <div class="story-card">
                <div class="story-title">왜 두 번째 대시보드가 필요한가?</div>
                <div class="story-text">
                    첫 번째 대시보드는 지역별 주거환경 만족도의 차이를 보여줍니다.
                    하지만 “어느 지역이 높고 낮은가”만으로는 정책 대안을 만들기 어렵습니다.
                    그래서 두 번째 대시보드는 만족도 차이를 만든 원인을
                    예산과 에너지 배분이라는 조작 가능한 변수로 바꾸어 실험합니다.
                    <br><br>
                    즉, 이 대시보드의 결론은 다음과 같습니다.
                    <br><b>기술이 아니라 배분이 도시의 수준을 결정한다.</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div class="story-card">
                <div class="story-title">대시보드 연결 흐름</div>
                <div class="bridge-step">
                    <div class="bridge-num">1</div>
                    <div>
                        <div class="bridge-step-title">시도별 만족도 격차 확인</div>
                        <div class="bridge-step-text">생활 인프라, 교통, 치안, 녹지, 교육 등 지표별 차이를 확인합니다.</div>
                    </div>
                </div>
                <div class="bridge-step">
                    <div class="bridge-num">2</div>
                    <div>
                        <div class="bridge-step-title">취약 지표를 정책 변수로 번역</div>
                        <div class="bridge-step-text">낮은 지표를 복지, 교육, 에너지 인프라, 일반 인프라, 안전 예산으로 연결합니다.</div>
                    </div>
                </div>
                <div class="bridge-step">
                    <div class="bridge-num">3</div>
                    <div>
                        <div class="bridge-step-title">배분 시뮬레이션 실행</div>
                        <div class="bridge-step-text">예산과 에너지 비율을 바꿔 시민 만족도와 에너지 자립률 변화를 실험합니다.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("지표와 시뮬레이션 변수 연결표")

    map_rows = []
    for indicator in indicator_cols:
        info = INDICATOR_TO_POLICY.get(indicator)
        if info:
            map_rows.append(
                {
                    "주거환경 지표": indicator,
                    "연결되는 예산 변수": info["budget"],
                    "연결되는 에너지 방향": info["energy"],
                    "해석": info["reason"],
                }
            )

    st.dataframe(pd.DataFrame(map_rows), use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="conclusion-box">
            <div class="conclusion-title">최종 연결 문장</div>
            <div class="conclusion-text">
                광역지표는 도시의 현재 상태를 보여주고,
                예산 및 에너지 배분 시뮬레이션은 그 상태를 바꾸기 위한 정책 실험 공간입니다.
                따라서 첫 번째 대시보드에서 확인한 취약 지표는
                두 번째 대시보드의 예산·에너지 슬라이더를 조정하는 근거가 됩니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_simulation_cta()


# ============================================================
# TAB 6. 데이터 표
# ============================================================
with tab6:
    st.markdown('<span class="small-label">Data Table</span>', unsafe_allow_html=True)
    st.subheader("전처리 데이터")

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


# ============================================================
# 하단 설명
# ============================================================
st.markdown("---")
st.markdown(
    f"""
### 분석 해석 방향

이 대시보드는 시도별 주거환경 만족도를 스마트시티 시민 체감 만족도의 기초 지표로 사용합니다.  
분석의 핵심은 단순한 순위 비교가 아니라, 지역별 취약 지표를 찾아
다음 단계의 예산·에너지 배분 변수로 연결하는 것입니다.

**결론: 기술이 아니라 배분이 도시의 수준을 결정한다.**

<a href="{SIMULATION_URL}" target="_blank">예산 및 에너지 배분 시뮬레이션으로 이동하기 →</a>
""",
    unsafe_allow_html=True,
)

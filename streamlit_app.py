import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="시도별 주거환경 만족도 광역지표",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = Path("data/현재_거주_지역의_주거환경_만족도_20260523172214.csv")

# =========================
# CSS 꾸미기
# =========================
st.markdown(
    """
    <style>
    .main {
        background-color: #f6f8fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #102a43;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        font-size: 1rem;
        color: #52606d;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        border: 1px solid #e5eaf0;
        height: 150px;
    }

    .metric-title {
        color: #627d98;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        color: #102a43;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .metric-desc {
        color: #829ab1;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }

    .section-card {
        background: white;
        padding: 1.2rem;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        border: 1px solid #e5eaf0;
        margin-bottom: 1rem;
    }

    .small-label {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        background-color: #e6f0ff;
        color: #1d4ed8;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# 데이터 로드
# =========================
@st.cache_data
def load_housing_satisfaction(path):
    # KOSIS CSV는 보통 cp949 인코딩인 경우가 많음
    try:
        raw = pd.read_csv(path, encoding="cp949")
    except UnicodeDecodeError:
        raw = pd.read_csv(path, encoding="utf-8-sig")

    # 첫 번째 행에 실제 지표명이 들어 있다고 가정
    indicator_names = raw.iloc[0, 2:].tolist()

    # 지역별 행만 추출
    df = raw[raw["특성별(1)"] == "지역별"].copy()

    # 컬럼명 정리
    new_columns = ["category", "region"] + indicator_names
    df.columns = new_columns
    df = df.drop(columns=["category"])

    # 숫자형 변환
    for col in df.columns:
        if col != "region":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    indicator_cols = [col for col in df.columns if col != "region"]

    # 종합지수 생성
    df["종합 주거환경 만족도"] = df[indicator_cols].mean(axis=1)

    return df, indicator_cols


if not DATA_PATH.exists():
    st.error(f"파일을 찾을 수 없습니다: {DATA_PATH}")
    st.stop()

df, indicator_cols = load_housing_satisfaction(DATA_PATH)

# =========================
# 권역 분류
# =========================
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

# =========================
# 사이드바
# =========================
st.sidebar.title("지표 설정")

view_mode = st.sidebar.radio(
    "보기 방식",
    ["차트 중심", "수치표 중심"],
    index=0
)

selected_groups = st.sidebar.multiselect(
    "권역 선택",
    options=["전체"] + sorted(df["권역"].unique().tolist()),
    default=["전체"]
)

selected_indicator = st.sidebar.selectbox(
    "대표 지표 선택",
    ["종합 주거환경 만족도"] + indicator_cols
)

sort_order = st.sidebar.radio(
    "정렬 기준",
    ["높은 순", "낮은 순"],
    horizontal=True
)

top_n = st.sidebar.slider(
    "표시할 지역 수",
    min_value=5,
    max_value=len(df),
    value=len(df)
)

if "전체" in selected_groups:
    filtered_df = df.copy()
else:
    filtered_df = df[df["권역"].isin(selected_groups)].copy()

ascending = True if sort_order == "낮은 순" else False
filtered_df = filtered_df.sort_values(selected_indicator, ascending=ascending).head(top_n)

# =========================
# 헤더
# =========================
st.markdown(
    """
    <div class="dashboard-title">시도별 주거환경 만족도 광역지표</div>
    <div class="dashboard-subtitle">
    현재 거주 지역의 주거환경 만족도를 바탕으로 도시별 생활 인프라, 교통, 의료, 녹지, 교육 환경 등을 비교합니다.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# 핵심 카드
# =========================
full_avg = df["종합 주거환경 만족도"].mean()
top_region = df.loc[df["종합 주거환경 만족도"].idxmax()]
low_region = df.loc[df["종합 주거환경 만족도"].idxmin()]
gap = top_region["종합 주거환경 만족도"] - low_region["종합 주거환경 만족도"]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">전국 평균</div>
            <div class="metric-value">{full_avg:.2f} / 5</div>
            <div class="metric-desc">8개 주거환경 지표 평균</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">만족도 최고 지역</div>
            <div class="metric-value">{top_region["region"]}</div>
            <div class="metric-desc">{top_region["종합 주거환경 만족도"]:.2f}점</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">만족도 최저 지역</div>
            <div class="metric-value">{low_region["region"]}</div>
            <div class="metric-desc">{low_region["종합 주거환경 만족도"]:.2f}점</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">지역 간 격차</div>
            <div class="metric-value">{gap:.2f}점</div>
            <div class="metric-desc">최고 지역 - 최저 지역</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# =========================
# 탭 구성
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "종합 현황",
        "지표별 비교",
        "권역 분석",
        "도시 프로필",
        "데이터 표"
    ]
)

# =========================
# TAB 1. 종합 현황
# =========================
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
            labels={
                "region": "시도",
                selected_indicator: "만족도"
            }
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            marker_line_width=0.7,
            marker_line_color="white"
        )
        fig.update_layout(
            height=520,
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=20,
            font=dict(size=13),
            margin=dict(l=30, r=30, t=70, b=30)
        )
        fig.update_yaxes(range=[0, 5], gridcolor="#e5eaf0")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(
            filtered_df[["권역", "region", selected_indicator]].reset_index(drop=True),
            use_container_width=True
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
            labels={
                "region": "시도",
                "종합 주거환경 만족도": "만족도"
            }
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(
            height=430,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        fig.update_xaxes(range=[0, 5], gridcolor="#e5eaf0")
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
                marker=dict(size=8)
            )
        )

        fig.add_hline(
            y=full_avg,
            line_dash="dash",
            annotation_text=f"전국 평균 {full_avg:.2f}",
            annotation_position="top left"
        )

        fig.update_layout(
            height=430,
            title="시도별 종합 만족도 분포",
            yaxis_title="만족도",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        fig.update_yaxes(range=[0, 5], gridcolor="#e5eaf0")
        st.plotly_chart(fig, use_container_width=True)


# =========================
# TAB 2. 지표별 비교
# =========================
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
            labels={
                "x": "지표",
                "y": "시도",
                "color": "만족도"
            },
            zmin=3,
            zmax=5
        )
        fig.update_layout(
            height=620,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        indicator_avg = (
            df[indicator_cols]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        indicator_avg.columns = ["지표", "전국 평균"]

        fig = px.bar(
            indicator_avg,
            x="전국 평균",
            y="지표",
            orientation="h",
            text="전국 평균",
            title="지표별 전국 평균",
            color="전국 평균",
            color_continuous_scale="Teal"
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(
            height=620,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        fig.update_xaxes(range=[0, 5], gridcolor="#e5eaf0")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("선택 지표 상세 순위")

    selected_detail_indicator = st.selectbox(
        "상세 비교할 지표",
        indicator_cols,
        key="detail_indicator"
    )

    detail_df = df.sort_values(selected_detail_indicator, ascending=False)

    fig = px.line(
        detail_df,
        x="region",
        y=selected_detail_indicator,
        markers=True,
        title=f"{selected_detail_indicator} 시도별 비교",
        labels={
            "region": "시도",
            selected_detail_indicator: "만족도"
        }
    )
    fig.add_hline(
        y=detail_df[selected_detail_indicator].mean(),
        line_dash="dash",
        annotation_text="평균",
        annotation_position="top left"
    )
    fig.update_layout(
        height=430,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_yaxes(range=[0, 5], gridcolor="#e5eaf0")
    st.plotly_chart(fig, use_container_width=True)


# =========================
# TAB 3. 권역 분석
# =========================
with tab3:
    st.markdown('<span class="small-label">Region Group</span>', unsafe_allow_html=True)
    st.subheader("권역별 주거환경 만족도")

    group_df = (
        df.groupby("권역")[["종합 주거환경 만족도"] + indicator_cols]
        .mean()
        .reset_index()
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        fig = px.bar(
            group_df.sort_values("종합 주거환경 만족도", ascending=False),
            x="권역",
            y="종합 주거환경 만족도",
            color="종합 주거환경 만족도",
            text="종합 주거환경 만족도",
            color_continuous_scale="Blues",
            title="권역별 종합 주거환경 만족도"
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_yaxes(range=[0, 5], gridcolor="#e5eaf0")
        fig.update_layout(
            height=450,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
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
            zmax=5
        )
        fig.update_layout(
            height=450,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("권역 구성 비중")

    count_df = df.groupby("권역").size().reset_index(name="지역 수")

    fig = px.treemap(
        count_df,
        path=["권역"],
        values="지역 수",
        title="권역별 포함 시도 수"
    )
    fig.update_layout(height=430)
    st.plotly_chart(fig, use_container_width=True)


# =========================
# TAB 4. 도시 프로필
# =========================
with tab4:
    st.markdown('<span class="small-label">City Profile</span>', unsafe_allow_html=True)
    st.subheader("도시별 주거환경 프로필")

    selected_city = st.selectbox(
        "도시 선택",
        df["region"].tolist()
    )

    city_row = df[df["region"] == selected_city].iloc[0]

    city_score = city_row["종합 주거환경 만족도"]
    city_rank = (
        df["종합 주거환경 만족도"]
        .rank(ascending=False, method="min")
        [df["region"] == selected_city]
        .iloc[0]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("선택 도시", selected_city)
    col2.metric("종합 만족도", f"{city_score:.2f} / 5")
    col3.metric("전국 순위", f"{int(city_rank)}위 / {len(df)}개")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        radar_df = pd.DataFrame({
            "지표": indicator_cols,
            "만족도": [city_row[col] for col in indicator_cols]
        })

        fig = px.line_polar(
            radar_df,
            r="만족도",
            theta="지표",
            line_close=True,
            title=f"{selected_city} 주거환경 레이더차트"
        )
        fig.update_traces(fill="toself")
        fig.update_polars(radialaxis=dict(range=[0, 5]))
        fig.update_layout(
            height=520,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        city_indicator_df = pd.DataFrame({
            "지표": indicator_cols,
            "만족도": [city_row[col] for col in indicator_cols],
            "전국 평균": [df[col].mean() for col in indicator_cols]
        })

        city_indicator_df["평균 대비"] = (
            city_indicator_df["만족도"] - city_indicator_df["전국 평균"]
        )

        fig = px.bar(
            city_indicator_df.sort_values("평균 대비"),
            x="평균 대비",
            y="지표",
            orientation="h",
            color="평균 대비",
            color_continuous_scale="RdBu",
            title=f"{selected_city}의 전국 평균 대비 강점·약점"
        )
        fig.add_vline(x=0, line_dash="dash")
        fig.update_layout(
            height=520,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

    weak_items = (
        city_indicator_df
        .sort_values("만족도")
        .head(3)
    )

    strong_items = (
        city_indicator_df
        .sort_values("만족도", ascending=False)
        .head(3)
    )

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.warning(f"{selected_city}의 상대적 취약 지표")
        st.dataframe(
            weak_items[["지표", "만족도", "전국 평균", "평균 대비"]],
            use_container_width=True
        )

    with col_b:
        st.success(f"{selected_city}의 상대적 강점 지표")
        st.dataframe(
            strong_items[["지표", "만족도", "전국 평균", "평균 대비"]],
            use_container_width=True
        )

    st.info(
        "취약 지표는 이후 예산 배분 시뮬레이션에서 우선 투자 영역으로 연결할 수 있습니다. "
        "예를 들어 대중교통 만족도가 낮은 도시는 교통·인프라 예산, 녹지 공간 만족도가 낮은 도시는 환경·에너지 투자를 높이는 방식으로 확장할 수 있습니다."
    )


# =========================
# TAB 5. 데이터 표
# =========================
with tab5:
    st.markdown('<span class="small-label">Data Table</span>', unsafe_allow_html=True)
    st.subheader("전처리 데이터")

    st.dataframe(
        df.sort_values("종합 주거환경 만족도", ascending=False),
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="전처리 데이터 CSV 다운로드",
        data=csv,
        file_name="housing_satisfaction_processed.csv",
        mime="text/csv"
    )

# =========================
# 하단 설명
# =========================
st.markdown("---")
st.markdown(
    """
    ### 분석 해석 방향

    이 대시보드는 시도별 주거환경 만족도를 스마트시티 시민 체감 만족도의 기초 지표로 사용합니다.  
    이후 단계에서는 이 데이터에 시도별 예산 배분 데이터와 에너지 효용 데이터를 결합하여  
    **“도시 만족도는 생활 인프라, 교통, 의료, 녹지, 교육 등 자원이 어디에 배분되는가와 연결된다”**는 흐름으로 확장할 수 있습니다.
    """
)

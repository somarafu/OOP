import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="시도별 주거환경 만족도 대시보드",
    layout="wide"
)

DATA_PATH = Path("data/현재_거주_지역의_주거환경_만족도_20260523172214.csv")

st.title("시도별 주거환경 만족도 대시보드")

st.markdown("""
이 대시보드는 시도별 주거환경 만족도를 바탕으로  
도시별 시민 체감 생활환경의 차이를 시각화합니다.
""")


@st.cache_data
def load_housing_satisfaction(path):
    raw = pd.read_csv(path, encoding="cp949")

    # 첫 번째 행에 실제 지표명이 들어 있으므로 따로 저장
    indicator_names = raw.iloc[0, 2:].tolist()

    # 지역별 행만 추출
    df = raw[raw["특성별(1)"] == "지역별"].copy()

    # 컬럼명 정리
    new_columns = ["category", "region"] + indicator_names
    df.columns = new_columns

    # 필요한 컬럼만 남기기
    df = df.drop(columns=["category"])

    # 숫자형 변환
    for col in df.columns:
        if col != "region":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 종합 만족도 생성
    indicator_cols = [col for col in df.columns if col != "region"]
    df["종합 주거환경 만족도"] = df[indicator_cols].mean(axis=1)

    return df, indicator_cols


if not DATA_PATH.exists():
    st.error(f"파일을 찾을 수 없습니다: {DATA_PATH}")
    st.stop()

df, indicator_cols = load_housing_satisfaction(DATA_PATH)

# =========================
# 1. 핵심 지표
# =========================
st.header("1. 전체 요약")

top_region = df.loc[df["종합 주거환경 만족도"].idxmax()]
low_region = df.loc[df["종합 주거환경 만족도"].idxmin()]
avg_score = df["종합 주거환경 만족도"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전국 평균", f"{avg_score:.2f} / 5")

with col2:
    st.metric(
        "만족도 최고 지역",
        top_region["region"],
        f"{top_region['종합 주거환경 만족도']:.2f}"
    )

with col3:
    st.metric(
        "만족도 최저 지역",
        low_region["region"],
        f"{low_region['종합 주거환경 만족도']:.2f}"
    )

# =========================
# 2. 시도별 종합 만족도
# =========================
st.header("2. 시도별 종합 주거환경 만족도")

fig = px.bar(
    df.sort_values("종합 주거환경 만족도", ascending=False),
    x="region",
    y="종합 주거환경 만족도",
    text="종합 주거환경 만족도",
    title="시도별 종합 주거환경 만족도",
    labels={
        "region": "시도",
        "종합 주거환경 만족도": "만족도 평균"
    }
)

fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig.update_yaxes(range=[0, 5])

st.plotly_chart(fig, use_container_width=True)

# =========================
# 3. 시도별 세부 지표 히트맵
# =========================
st.header("3. 시도별 세부 주거환경 만족도 히트맵")

heatmap_df = df.set_index("region")[indicator_cols]

fig = px.imshow(
    heatmap_df,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="YlGnBu",
    title="시도별 주거환경 세부 지표",
    labels={
        "x": "주거환경 지표",
        "y": "시도",
        "color": "만족도"
    },
    zmin=3,
    zmax=5
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 4. 지표별 도시 순위
# =========================
st.header("4. 지표별 도시 순위")

selected_indicator = st.selectbox(
    "확인할 주거환경 지표를 선택하세요",
    indicator_cols
)

rank_df = df[["region", selected_indicator]].sort_values(
    selected_indicator,
    ascending=False
)

fig = px.bar(
    rank_df,
    x="region",
    y=selected_indicator,
    text=selected_indicator,
    title=f"{selected_indicator} 만족도 시도별 순위",
    labels={
        "region": "시도",
        selected_indicator: "만족도"
    }
)

fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig.update_yaxes(range=[0, 5])

st.plotly_chart(fig, use_container_width=True)

# =========================
# 5. 도시별 레이더차트
# =========================
st.header("5. 도시별 주거환경 프로필")

selected_region = st.selectbox(
    "도시를 선택하세요",
    df["region"].tolist()
)

region_row = df[df["region"] == selected_region].iloc[0]

radar_df = pd.DataFrame({
    "indicator": indicator_cols,
    "score": [region_row[col] for col in indicator_cols]
})

fig = px.line_polar(
    radar_df,
    r="score",
    theta="indicator",
    line_close=True,
    title=f"{selected_region} 주거환경 만족도 프로필"
)

fig.update_traces(fill="toself")
fig.update_polars(radialaxis=dict(range=[0, 5]))

st.plotly_chart(fig, use_container_width=True)

# =========================
# 6. 취약 지표 자동 분석
# =========================
st.header("6. 도시별 취약 지표 분석")

selected_row = df[df["region"] == selected_region].iloc[0]

weak_items = (
    selected_row[indicator_cols]
    .sort_values(ascending=True)
    .head(3)
)

st.write(f"**{selected_region}에서 상대적으로 낮은 만족도 지표 TOP 3**")

weak_df = weak_items.reset_index()
weak_df.columns = ["지표", "만족도"]

st.dataframe(weak_df, use_container_width=True)

st.info(
    f"{selected_region}의 낮은 지표는 이후 시뮬레이션에서 "
    "예산 배분 또는 에너지·환경 정책 우선순위로 연결할 수 있습니다."
)

# =========================
# 7. 원본 데이터
# =========================
with st.expander("전처리된 데이터 보기"):
    st.dataframe(df, use_container_width=True)

pd.read_excel("data/2025년 서울서베이 시민조사_통계표.xlsx")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="서울 스마트시티 시민 만족도 대시보드",
    layout="wide"
)

DATA_DIR = Path("data")

SURVEY_FILE = DATA_DIR / "2025년 서울서베이 시민조사_통계표.xlsx"
BUDGET_FILE = DATA_DIR / "seoul_budget_by_district.csv"
ENERGY_FILE = DATA_DIR / "seoul_energy_by_district.csv"
SURVEY_DISTRICT_FILE = DATA_DIR / "survey_by_district.csv"


# =========================
# 공통 함수
# =========================
@st.cache_data
def load_excel_table():
    """
    서울서베이 통계표 엑셀의 Sheet1을 원본 형태로 불러온다.
    """
    return pd.read_excel(SURVEY_FILE, sheet_name="Sheet1", header=None)


def find_table_start(raw_df, keyword):
    """
    Sheet1에서 특정 표 제목이 있는 행 번호를 찾는다.
    예: '<표29A> 서울의 매력_10점 평균'
    """
    for idx, value in raw_df[0].items():
        if isinstance(value, str) and keyword in value:
            return idx
    return None


def extract_overall_row_table(raw_df, keyword, selected_columns=None):
    """
    서울서베이 통계표에서 '▩전체▩' 행의 10점 평균 지표들을 추출한다.

    구조 예시:
    표 제목 행
    BASE:전체 / 사례수 / 지표명들...
    ▩전체▩ / (5000) / 점수들...
    """
    start_idx = find_table_start(raw_df, keyword)

    if start_idx is None:
        return pd.DataFrame(columns=["indicator", "score"])

    header_row = raw_df.iloc[start_idx + 1]
    value_row = raw_df.iloc[start_idx + 2]

    records = []

    for col_idx in range(3, raw_df.shape[1]):
        indicator = header_row[col_idx]
        score = value_row[col_idx]

        if pd.isna(indicator) or pd.isna(score):
            continue

        indicator = str(indicator).strip()

        try:
            score = float(score)
        except:
            continue

        if selected_columns is not None and indicator not in selected_columns:
            continue

        records.append({
            "indicator": indicator,
            "score": score
        })

    return pd.DataFrame(records)


@st.cache_data
def load_optional_csv(path):
    """
    선택 데이터 CSV를 불러온다.
    파일이 없으면 None 반환.
    """
    if path.exists():
        return pd.read_csv(path)
    return None


def normalize_district_column(df):
    """
    자치구 컬럼명을 district로 통일한다.
    """
    if df is None:
        return None

    df = df.copy()

    possible_cols = ["district", "자치구", "구", "지역", "gu", "GU"]

    for col in possible_cols:
        if col in df.columns:
            df = df.rename(columns={col: "district"})
            break

    return df


def to_numeric_columns(df, exclude_cols=None):
    """
    숫자로 변환 가능한 컬럼을 숫자형으로 변환한다.
    """
    if exclude_cols is None:
        exclude_cols = []

    df = df.copy()

    for col in df.columns:
        if col not in exclude_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# =========================
# 제목
# =========================
st.title("서울 스마트시티 시민 만족도와 결정 요인 대시보드")

st.markdown("""
이 대시보드는 서울서베이 시민조사 통계표를 바탕으로  
서울 시민의 스마트시티 체감 지표를 시각화하고,  
추가로 구별 예산 데이터와 에너지 데이터를 연결해  
시민 만족도의 결정 요인을 탐색하는 구조입니다.
""")


# =========================
# 파일 확인
# =========================
if not SURVEY_FILE.exists():
    st.error(f"서울서베이 파일을 찾을 수 없습니다: {SURVEY_FILE}")
    st.stop()

raw_survey = load_excel_table()


# =========================
# 1. 서울서베이: 스마트시티 체감 지표
# =========================
st.header("1. 서울 시민 스마트시티 체감 지표")

smartcity_columns = [
    "시내 활동의 안전성",
    "깨끗한 주변환경",
    "교통의 편리함",
    "도로 및 주차시설의 편리성",
    "다양한 편의시설",
    "타 지역과의 접근 용이성",
    "적절한 안내 표시",
]

smartcity_df = extract_overall_row_table(
    raw_survey,
    "<표29A> 서울의 매력_10점 평균",
    selected_columns=smartcity_columns
)

if smartcity_df.empty:
    st.warning("서울의 매력 관련 지표를 찾지 못했습니다.")
else:
    col1, col2 = st.columns([1, 2])

    with col1:
        avg_score = smartcity_df["score"].mean()
        st.metric("스마트시티 체감 평균", f"{avg_score:.2f} / 10")

        top_row = smartcity_df.loc[smartcity_df["score"].idxmax()]
        low_row = smartcity_df.loc[smartcity_df["score"].idxmin()]

        st.metric("가장 높은 지표", f"{top_row['indicator']}", f"{top_row['score']:.2f}")
        st.metric("가장 낮은 지표", f"{low_row['indicator']}", f"{low_row['score']:.2f}")

    with col2:
        fig = px.bar(
            smartcity_df.sort_values("score", ascending=True),
            x="score",
            y="indicator",
            orientation="h",
            text="score",
            title="서울 시민 스마트시티 체감 지표",
            labels={
                "score": "10점 평균",
                "indicator": "지표"
            }
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_xaxes(range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)


# =========================
# 2. AI 공공서비스 필요성
# =========================
st.header("2. AI 기반 공공서비스 필요성")

ai_columns = [
    "개인의 역량을 고려한 맞춤형 교육·학습 서비스",
    "행정데이터를 활용해 복지 사각지대에 있는 시민을 찾아내고 필요한 복지지원을 연결하는 서비스",
    "교통사고를 예방하고 안전성을 높이기 위한 교통서비스",
    "운동, 의료기록, 질병 관리 등을 위한 헬스케어 서비스",
    "서울시민 욕구에 맞는 정책을 안내하고 맞춤형 정책을 연결하는 AI기반 정책플랫폼 서비스",
]

ai_df = extract_overall_row_table(
    raw_survey,
    "<표7A> AI 기반 공공서비스 필요성_10점 평균",
    selected_columns=ai_columns
)

if ai_df.empty:
    st.warning("AI 공공서비스 필요성 지표를 찾지 못했습니다.")
else:
    short_names = {
        "개인의 역량을 고려한 맞춤형 교육·학습 서비스": "교육·학습",
        "행정데이터를 활용해 복지 사각지대에 있는 시민을 찾아내고 필요한 복지지원을 연결하는 서비스": "복지 연결",
        "교통사고를 예방하고 안전성을 높이기 위한 교통서비스": "교통 안전",
        "운동, 의료기록, 질병 관리 등을 위한 헬스케어 서비스": "헬스케어",
        "서울시민 욕구에 맞는 정책을 안내하고 맞춤형 정책을 연결하는 AI기반 정책플랫폼 서비스": "정책 플랫폼",
    }

    ai_df["service"] = ai_df["indicator"].map(short_names)

    fig = px.bar(
        ai_df.sort_values("score", ascending=False),
        x="service",
        y="score",
        text="score",
        title="AI 기반 공공서비스 필요성",
        labels={
            "service": "서비스 분야",
            "score": "10점 평균"
        }
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_yaxes(range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "이 그래프는 시민들이 어떤 스마트 공공서비스를 더 필요로 하는지 보여줍니다. "
        "이후 시뮬레이션에서 복지·교통·헬스케어·정책 플랫폼 예산 배분으로 연결할 수 있습니다."
    )


# =========================
# 3. 시민이 원하는 정책 투자 방향
# =========================
st.header("3. 시민이 원하는 정책 투자 방향")

tax_df = extract_overall_row_table(
    raw_survey,
    "<표22A> 세금을 더 낼 의향_10점 평균",
    selected_columns=[
        "영유아·아동 정책",
        "청소년 정책",
        "청년 정책",
        "중장년 정책",
        "노년 전기 정책",
        "노년 후기 정책",
        "종합"
    ]
)

if tax_df.empty:
    st.warning("세금을 더 낼 의향 지표를 찾지 못했습니다.")
else:
    fig = px.bar(
        tax_df[tax_df["indicator"] != "종합"].sort_values("score", ascending=False),
        x="indicator",
        y="score",
        text="score",
        title="정책 분야별 세금 부담 의향",
        labels={
            "indicator": "정책 분야",
            "score": "10점 평균"
        }
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_yaxes(range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "이 지표는 실제 예산 데이터는 아니지만, 시민이 어느 정책 분야에 더 많은 자원 투입을 원하고 있는지 보여주는 자료로 활용할 수 있습니다."
    )


# =========================
# 4. 구별 만족도 데이터
# =========================
st.header("4. 구별 시민 만족도")

survey_district_df = load_optional_csv(SURVEY_DISTRICT_FILE)
survey_district_df = normalize_district_column(survey_district_df)

if survey_district_df is None:
    st.warning("""
현재 `data/survey_by_district.csv` 파일이 없습니다.

서울서베이 통계표만으로는 구별 만족도를 바로 추출하기 어렵습니다.  
구별 만족도를 시각화하려면 아래 형식의 CSV를 추가로 만들어야 합니다.

필요 파일명: `data/survey_by_district.csv`

예시 컬럼:
`district, satisfaction, mobility, safety, environment, public_service`
""")
else:
    survey_district_df = to_numeric_columns(survey_district_df, exclude_cols=["district"])

    fig = px.bar(
        survey_district_df.sort_values("satisfaction", ascending=False),
        x="district",
        y="satisfaction",
        text="satisfaction",
        title="서울 구별 시민 만족도",
        labels={
            "district": "자치구",
            "satisfaction": "만족도"
        }
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    factor_cols = [
        col for col in ["mobility", "safety", "environment", "public_service"]
        if col in survey_district_df.columns
    ]

    if factor_cols:
        heatmap_df = survey_district_df.set_index("district")[factor_cols]

        fig = px.imshow(
            heatmap_df,
            text_auto=True,
            aspect="auto",
            title="구별 시민 체감 요인 히트맵",
            labels={
                "x": "요인",
                "y": "자치구",
                "color": "점수"
            }
        )
        st.plotly_chart(fig, use_container_width=True)


# =========================
# 5. 구별 예산 데이터
# =========================
st.header("5. 서울시 구별 예산 배분")

budget_df = load_optional_csv(BUDGET_FILE)
budget_df = normalize_district_column(budget_df)

if budget_df is None:
    st.warning("""
현재 `data/seoul_budget_by_district.csv` 파일이 없습니다.

구별 예산 시각화를 하려면 아래 형식의 CSV를 추가하세요.

예시 컬럼:
`district, total_budget, welfare, education, transport, safety, environment, smartcity, energy`
""")
else:
    budget_df = to_numeric_columns(budget_df, exclude_cols=["district"])

    budget_cols = [
        col for col in [
            "welfare",
            "education",
            "transport",
            "safety",
            "environment",
            "smartcity",
            "energy"
        ]
        if col in budget_df.columns
    ]

    if "total_budget" in budget_df.columns:
        fig = px.bar(
            budget_df.sort_values("total_budget", ascending=False),
            x="district",
            y="total_budget",
            text="total_budget",
            title="구별 총 예산",
            labels={
                "district": "자치구",
                "total_budget": "총 예산"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    if budget_cols:
        selected_district = st.selectbox(
            "예산 배분을 확인할 자치구 선택",
            budget_df["district"].unique(),
            key="budget_select"
        )

        selected_budget = budget_df[budget_df["district"] == selected_district].iloc[0]

        pie_df = pd.DataFrame({
            "category": budget_cols,
            "amount": [selected_budget[col] for col in budget_cols]
        })

        fig = px.pie(
            pie_df,
            names="category",
            values="amount",
            title=f"{selected_district} 예산 배분"
        )
        st.plotly_chart(fig, use_container_width=True)

        stacked_df = budget_df[["district"] + budget_cols].melt(
            id_vars="district",
            var_name="category",
            value_name="amount"
        )

        fig = px.bar(
            stacked_df,
            x="district",
            y="amount",
            color="category",
            title="구별 분야별 예산 배분",
            labels={
                "district": "자치구",
                "amount": "예산",
                "category": "분야"
            }
        )
        st.plotly_chart(fig, use_container_width=True)


# =========================
# 6. 구별 에너지 데이터
# =========================
st.header("6. 서울시 구별 에너지 효용")

energy_df = load_optional_csv(ENERGY_FILE)
energy_df = normalize_district_column(energy_df)

if energy_df is None:
    st.warning("""
현재 `data/seoul_energy_by_district.csv` 파일이 없습니다.

구별 에너지 시각화를 하려면 아래 형식의 CSV를 추가하세요.

예시 컬럼:
`district, electricity_usage_mwh, renewable_generation_mwh, solar_generation_mwh, energy_budget, greenhouse_gas_tco2`
""")
else:
    energy_df = to_numeric_columns(energy_df, exclude_cols=["district"])

    if {
        "electricity_usage_mwh",
        "renewable_generation_mwh"
    }.issubset(energy_df.columns):
        energy_df["renewable_self_sufficiency"] = (
            energy_df["renewable_generation_mwh"]
            / energy_df["electricity_usage_mwh"]
            * 100
        )

    if {
        "electricity_usage_mwh",
        "solar_generation_mwh"
    }.issubset(energy_df.columns):
        energy_df["solar_ratio"] = (
            energy_df["solar_generation_mwh"]
            / energy_df["electricity_usage_mwh"]
            * 100
        )

    energy_chart_cols = [
        col for col in [
            "electricity_usage_mwh",
            "renewable_generation_mwh",
            "solar_generation_mwh",
            "energy_budget",
            "greenhouse_gas_tco2",
            "renewable_self_sufficiency",
            "solar_ratio"
        ]
        if col in energy_df.columns
    ]

    selected_energy_metric = st.selectbox(
        "에너지 지표 선택",
        energy_chart_cols,
        key="energy_metric"
    )

    fig = px.bar(
        energy_df.sort_values(selected_energy_metric, ascending=False),
        x="district",
        y=selected_energy_metric,
        text=selected_energy_metric,
        title=f"구별 {selected_energy_metric}",
        labels={
            "district": "자치구",
            selected_energy_metric: "값"
        }
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# =========================
# 7. 만족도와 예산·에너지 관계 분석
# =========================
st.header("7. 만족도와 예산·에너지 관계")

if survey_district_df is None:
    st.warning("구별 만족도 파일이 없어 상관관계 분석을 수행할 수 없습니다.")
else:
    merged_df = survey_district_df.copy()

    if budget_df is not None:
        merged_df = merged_df.merge(budget_df, on="district", how="left")

    if energy_df is not None:
        merged_df = merged_df.merge(energy_df, on="district", how="left")

    numeric_cols = merged_df.select_dtypes(include=[np.number]).columns.tolist()

    if "satisfaction" not in numeric_cols:
        st.warning("`survey_by_district.csv`에 satisfaction 컬럼이 필요합니다.")
    elif len(numeric_cols) < 2:
        st.warning("상관관계를 계산할 숫자형 컬럼이 부족합니다.")
    else:
        corr_df = merged_df[numeric_cols].corr()

        fig = px.imshow(
            corr_df,
            text_auto=".2f",
            aspect="auto",
            title="구별 만족도·예산·에너지 지표 상관관계",
            labels={
                "color": "상관계수"
            },
            zmin=-1,
            zmax=1
        )
        st.plotly_chart(fig, use_container_width=True)

        relation_cols = [
            col for col in numeric_cols
            if col != "satisfaction"
        ]

        selected_x = st.selectbox(
            "만족도와 비교할 지표 선택",
            relation_cols
        )

        fig = px.scatter(
            merged_df,
            x=selected_x,
            y="satisfaction",
            text="district",
            trendline="ols",
            title=f"만족도와 {selected_x}의 관계",
            labels={
                selected_x: selected_x,
                "satisfaction": "시민 만족도"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "이 분석은 인과관계를 증명하는 것이 아니라, "
            "구별 만족도와 예산·에너지 지표가 함께 움직이는지 탐색하는 단계입니다."
        )


# =========================
# 8. 마무리 메시지
# =========================
st.header("8. 분석 흐름 요약")

st.markdown("""
이 대시보드의 논리 구조는 다음과 같습니다.

1. 서울서베이로 시민이 체감하는 스마트시티 요소를 확인한다.  
2. 구별 예산 데이터로 도시 자원이 어디에 배분되는지 확인한다.  
3. 구별 에너지 데이터로 에너지 효용을 확인한다.  
4. 구별 만족도와 예산·에너지 지표를 연결해 스마트시티 만족도의 결정 요인을 탐색한다.  
5. 이후 단계에서는 예산 배분과 에너지 배분을 조정하는 시뮬레이션으로 확장한다.
""")

import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정
st.set_page_config(
    page_title="MBTI 유형별 국가 분석 대시보드",
    layout="wide"
)

# 제목
st.title("🌍 MBTI 유형별 국가 TOP 10 분석 대시보드")
st.markdown("""
이 대시보드는 국가별 MBTI 분포 데이터를 기반으로 특정 MBTI 유형이 높은 국가 TOP 10을 시각적으로 보여줍니다.<br>
**📊 그래프는 Altair로 구현되며, 직관적인 색상과 인터랙티브 기능을 제공합니다.**
""", unsafe_allow_html=True)

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# MBTI 유형 목록 (Country 열 제외 나머지 열)
mbti_types = [col for col in df.columns if col != "Country"]

# 사이드바 선택
st.sidebar.header("🔎 분석 옵션")
selected_type = st.sidebar.selectbox("MBTI 유형을 선택하세요:", mbti_types)

# 선택한 유형 기준으로 TOP 10 추출
top10_df = df.nlargest(10, selected_type)[["Country", selected_type]].reset_index(drop=True)

# 제목 출력
st.subheader(f"🏆 {selected_type} 유형 비율이 높은 국가 TOP 10")

# Altair 차트 생성
chart = (
    alt.Chart(top10_df)
    .mark_bar()
    .encode(
        x=alt.X(selected_type, title=f"{selected_type} 비율"),
        y=alt.Y("Country", sort='-x', title="국가"),
        tooltip=["Country", selected_type],
        color=alt.Color(selected_type, scale=alt.Scale(scheme='blues'), legend=None)
    )
    .properties(width=700, height=400)
    .interactive()
)

# 그래프 표시
st.altair_chart(chart, use_container_width=True)

# 데이터 테이블 표시
with st.expander("📄 데이터 상세 보기"):
    st.dataframe(top10_df.style.format({selected_type: "{:.2f}"}))

# 인사이트 생성
max_country = top10_df.iloc[0]["Country"]
max_value = top10_df.iloc[0][selected_type]
st.markdown(f"""
### 🧠 분석 인사이트
- **{selected_type} 유형이 가장 높은 국가는 `{max_country}`이며, 비율은 {max_value:.2f}% 입니다.**
- 상위 10개 국가는 전반적으로 `{selected_type}` 유형의 성향이 강하게 나타나는 국가로 해석될 수 있습니다.
""")

# Footer
st.markdown("---")
st.caption("🔧 Powered by Streamlit + Altair | 데이터 기반 MBTI 국가 분석")

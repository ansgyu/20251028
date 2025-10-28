import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정
st.set_page_config(
    page_title="MBTI 유형별 국가 분석 대시보드",
    layout="wide"
)

st.title("🌍 MBTI 유형별 국가 TOP 10 분석 대시보드 (URL 기반 데이터 로드)")
st.markdown("""
MBTI 데이터를 CSV URL에서 직접 불러옵니다.<br>
**GitHub Raw 링크 또는 공개된 CSV URL을 입력하세요.**
""", unsafe_allow_html=True)

# URL 입력 받기
default_url = "https://raw.githubusercontent.com/ansgyu/20251028/main/countriesMBTI_16types.csv"
csv_url = st.sidebar.text_input("CSV 파일 URL을 입력하세요:", default_url)

# 데이터 불러오기 함수
@st.cache_data
def load_data_from_url(url):
    try:
        df = pd.read_csv(url)
        return df, None
    except Exception as e:
        return None, str(e)

df, error = load_data_from_url(csv_url)

# 오류 처리
if error:
    st.error(f"❌ 데이터를 불러오는 중 오류 발생: {error}")
    st.info("💡 URL이 Raw CSV 형식인지 확인하세요. (예: https://raw.githubusercontent.com/...)")
    st.stop()
else:
    st.success("✅ 데이터 불러오기 성공!")

# MBTI 유형 선택 옵션 생성
mbti_types = [col for col in df.columns if col != "Country"]

if not mbti_types:
    st.error("CSV에 MBTI 유형 데이터가 포함되어 있지 않습니다. 'Country' 외에 다른 열이 필요합니다.")
    st.stop()

# 사이드바 선택
selected_type = st.sidebar.selectbox("MBTI 유형을 선택하세요:", mbti_types)

# TOP 10 추출
top10_df = df.nlargest(10, selected_type)[["Country", selected_type]].reset_index(drop=True)

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

# 차트 표시
st.altair_chart(chart, use_container_width=True)

# 테이블 표시
with st.expander("📄 데이터 상세 보기"):
    st.dataframe(top10_df.style.format({selected_type: "{:.2f}"}))

# 인사이트
max_country = top10_df.iloc[0]["Country"]
max_value = top10_df.iloc[0][selected_type]
st.markdown(f"""
### 🧠 분석 인사이트
- **{selected_type} 유형이 가장 높은 국가는 `{max_country}`이며, 비율은 {max_value:.2f}% 입니다.**
- 상위 10개 국가들은 `{selected_type}` 성향이 두드러지게 나타나는 국가입니다.
""")

st.markdown("---")
st.caption("🔧 Powered by Streamlit + Altair | URL 기반 데이터 분석")

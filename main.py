import streamlit as st
import pandas as pd
from collections import Counter
import re

# Streamlit 애플리케이션 제목 설정
st.title("🏥 국립나주병원 치료식 식단 빈도 분석")
st.markdown("---")

# 1. 데이터 불러오기
# (참고: Streamlit 환경에서는 파일을 직접 업로드하거나 경로를 지정해야 합니다.
# 이 코드는 현재 Jupyter/Colab 환경을 가정하고 파일을 읽습니다.
# 실제 Streamlit 배포 시에는 파일을 프로젝트 폴더에 넣어주세요.)
FILE_NAME = "보건복지부 국립나주병원_치료식 식단 정보_20250331.csv"
try:
    df = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    st.error(f"⚠️ 파일을 찾을 수 없습니다: {FILE_NAME}")
    st.stop()

# 2. 데이터 전처리 및 메뉴 추출 함수
def analyze_menu_frequency(df, diet_type):
    """특정 식이구분의 모든 메뉴 항목의 빈도수를 계산합니다."""
    # 해당 식이구분 데이터 필터링
    diet_df = df[df['식이구분'] == diet_type]

    all_menus = []
    # 조식, 중식, 석식 컬럼 순회
    for col in ['조식', '중식', '석식']:
        # 각 식단 셀의 문자열을 '+' 기준으로 분리하여 모든 메뉴 리스트에 추가
        for menu_str in diet_df[col].dropna():
            # 메뉴명에 포함될 수 있는 괄호/숫자 등 특수문자 제거 후 리스트에 추가
            items = [re.sub(r'\(.*?\)|\[.*?\]|\d+/\d+', '', item).strip() for item in menu_str.split('+')]
            all_menus.extend(items)

    # 빈도수 계산
    menu_counts = Counter(all_menus)

    # 밥 종류 (쌀밥, 잡곡밥, 보리밥, 죽 등)는 주식으로 간주하여 제외하거나 통합 처리 가능
    # 여기서는 '밥'과 '죽'을 제외하여 반찬/국에 집중합니다.
    # 제외 목록
    exclude_list = ['쌀밥', '잡곡밥', '보리밥', '쌀밥1/2', '흑미밥', '흰죽', '쌀죽', '야채죽', '새우살죽', '흑임자죽']
    for item in exclude_list:
        menu_counts.pop(item, None) # 딕셔너리에 없으면 무시하고 삭제

    # 메뉴 이름이 너무 짧은 경우(예: '소스')는 분석에서 제외
    menu_counts = {k: v for k, v in menu_counts.items() if len(k) > 1}

    # DataFrame으로 변환 및 정렬
    freq_df = pd.DataFrame(menu_counts.items(), columns=['메뉴', '빈도'])
    freq_df = freq_df.sort_values(by='빈도', ascending=False).reset_index(drop=True)

    return freq_df

# 3. Streamlit 대시보드 구성
st.header("📋 메뉴별 빈도수 (주식 제외)")
st.caption("조식, 중식, 석식에 등장한 모든 메뉴를 통합 분석했습니다. (밥, 죽 종류 제외)")

# 분석할 식이 구분 목록
diet_types = df['식이구분'].unique().tolist()
# 드롭다운 메뉴로 식이 구분 선택
selected_diet = st.selectbox("분석할 식이 구분을 선택하세요:", diet_types)

if selected_diet:
    # 4. 선택된 식이 구분 분석 실행
    freq_df_result = analyze_menu_frequency(df, selected_diet)
    top_n = st.slider("상위 몇 개의 메뉴를 볼까요?", 5, 30, 15)

    if not freq_df_result.empty:
        top_menus = freq_df_result.head(top_n)

        # 5. 시각화 (막대 차트)
        st.subheader(f"🥇 {selected_diet} 메뉴 빈도 Top {top_n} (차트)")
        st.bar_chart(top_menus.set_index('메뉴'))

        # 6. 결과 테이블 표시
        st.subheader(f"📊 {selected_diet} 메뉴 빈도 Top {top_n} (표)")
        st.dataframe(top_menus, hide_index=True)

        st.markdown(f"---")
        st.info("💡 **분석 인사이트:**")
        if selected_diet == '일반식':
            st.write("일반식에서는 **포기김치, 백김치, 깍두기**와 같은 김치류와 **메추리알장조림** 같은 기본 밑반찬이 자주 제공됨을 알 수 있습니다.")
        elif selected_diet == '당뇨식':
            st.write("당뇨식에서도 기본 김치류와 함께 **멸치볶음, 오이생채** 등 저염/채소 위주의 밑반찬이 높은 빈도를 보입니다.")
        elif selected_diet == '연식':
            st.write("연식에서는 **백김치**가 가장 압도적이며, **들깨나물, 애호박나물** 등 부드러운 나물류와 소화가 쉬운 메뉴들이 주를 이룹니다.")
    else:
        st.warning(f"{selected_diet}에 대한 메뉴 데이터를 찾을 수 없거나 분석할 항목이 부족합니다.")

# 7. 전체 데이터 정보 요약 (선택 사항)
with st.expander("원본 데이터 및 분석 기간 확인"):
    st.dataframe(df.head())
    df['날짜'] = pd.to_datetime(df['날짜'])
    start_date = df['날짜'].min().strftime('%Y-%m-%d')
    end_date = df['날짜'].max().strftime('%Y-%m-%d')
    st.write(f"**전체 데이터 기간:** {start_date} 부터 {end_date} 까지")

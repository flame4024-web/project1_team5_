import streamlit as st
import os

# 페이지 기본 설정
st.set_page_config(
    page_title="신혼부부 서울 주거지 분석 보고서",
    page_icon="🏠",
    layout="wide"
)

# 현재 스크립트 위치를 기반으로 report.md 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
markdown_path = os.path.join(current_dir, "report.md")

# 사이드바 제목
st.sidebar.title("보고서 목차")
st.sidebar.markdown("""
- [1. 프로젝트 개요](#1)
- [2. 타겟 페르소나 및 입력 조건](#2)
- [3. 대중교통 통근권 매핑 (EDA)](#3-eda)
- [4. 통근 최적 지역(교집합) 도출](#4)
- [5. 스코어링 및 인사이트 도출](#5-top-5)
""")

# 마크다운 파일 읽기 및 화면 출력
try:
    with open(markdown_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Streamlit에서 마크다운 렌더링
    # 참고: 마크다운 내부의 이미지 경로(./images/...)는 Streamlit이 직접 서빙할 수 있도록 구성되어야 합니다.
    # 만약 웹 배포 후 이미지가 보이지 않는다면 st.image()를 사용하도록 코드를 수정해야 할 수 있습니다.
    st.markdown(content, unsafe_allow_html=True)
    
except FileNotFoundError:
    st.error(f"⚠️ 데이터를 불러올 수 없습니다. 경로를 확인해주세요: `{markdown_path}`")
    st.info("실행 위치(경로)에 'report.md' 파일이 존재하는지 확인해 주세요.")

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
        
    # Streamlit Cloud 환경에서 로컬 경로(./images/...)의 이미지가 
    # st.markdown()으로는 렌더링되지 않으므로, 정규식을 사용하여 
    # 텍스트와 이미지를 분리하여 st.image()로 렌더링합니다.
    import re
    
    # 마크다운 이미지 패턴: ![alt 텍스트](경로)
    pattern = r"!\[(.*?)\]\((.*?)\)"
    
    # 패턴으로 split 하면 [텍스트, alt, 경로, 텍스트, alt, 경로, ...] 형태로 나옴
    parts = re.split(pattern, content)
    
    for i in range(0, len(parts), 3):
        # 1. 일반 마크다운 텍스트 렌더링
        st.markdown(parts[i], unsafe_allow_html=True)
        
        # 2. 다음 이미지가 있다면 렌더링
        if i + 2 < len(parts):
            alt_text = parts[i+1]
            img_path = parts[i+2]
            
            # 절대 경로로 변환 (app.py 기준)
            abs_img_path = os.path.join(current_dir, img_path.replace('./', ''))
            
            if os.path.exists(abs_img_path):
                st.image(abs_img_path, caption=alt_text, use_container_width=True)
            else:
                st.warning(f"⚠️ 이미지를 찾을 수 없습니다: {img_path}")
    
except FileNotFoundError:
    st.error(f"⚠️ 데이터를 불러올 수 없습니다. 경로를 확인해주세요: `{markdown_path}`")
    st.info("실행 위치(경로)에 'report.md' 파일이 존재하는지 확인해 주세요.")

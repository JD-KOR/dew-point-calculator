import streamlit as st
import math

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. CSS 주입: 전체 폰트 크기를 기존 대비 70% 수준으로 조정
st.markdown("""
    <style>
        /* JD Calculator 문구 (26px -> 18px) */
        .jd-header {
            text-align: right;
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700;
            color: black;
            font-size: 18px;
            margin-bottom: -10px;
            padding-right: 5px;
        }
        
        /* 입력창 레이블 (1.8rem -> 1.26rem) */
        .stNumberInput label p {
            font-size: 1.26rem !important;
            font-weight: 600 !important;
            color: #31333F;
        }
        
        /* 숫자 입력칸 내부 숫자 (2rem -> 1.4rem, 높이 60px -> 42px) */
        .stNumberInput input {
            font-size: 1.4rem !important;
            height: 42px !important;
        }
        
        /* 결과 값 Metric Value (4.5rem -> 3.15rem) */
        [data-testid="stMetricValue"] {
            font-size: 3.15rem !important;
            font-weight: 700 !important;
        }
        
        /* 결과 레이블 (1.6rem -> 1.12rem) */
        [data-testid="stMetricLabel"] p {
            font-size: 1.12rem !important;
        }

        /* 탭 텍스트 (1.3rem -> 0.91rem) */
        .stTabs [data-baseweb="tab"] p {
            font-size: 0.91rem !important;
        }
    </style>
    <div class="jd-header">JD Calculator</div>
    """, unsafe_allow_html=True)

st.title("🌡️ 공기 라인 습도/노점 계산기")
st.markdown("---")

# 상단 탭 구성
tab1, tab2 = st.tabs(["💧 노점 계산 (Temp/RH → DP)", "☁️ 상대습도 계산 (Temp/DP → RH)"])

# Magnus 상수
b = 17.625
c = 243.04

# --- Tab 1: 노점 계산 ---
with tab1:
    st.header("📌 입력 (Input)")
    t1 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t1")
    rh1 = st.number_input("상대습도 (%)", value=50.0, min_value=0.1, max_value=100.0, step=0.1, key="rh1")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        gamma1 = math.log(rh1 / 100.0) + (

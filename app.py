import streamlit as st
import math

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. CSS 주입: 폰트 크기 대폭 증대 및 레이아웃 조정
st.markdown("""
    <style>
        /* JD Calculator 문구 위치 조정 (화면 안쪽으로 이동) */
        .jd-header {
            text-align: right;
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700;
            color: black;
            font-size: 26px;
            margin-bottom: -10px;
            padding-right: 5px;
        }
        
        /* 입력창 레이블(현재온도 등) 폰트 크기 */
        .stNumberInput label p {
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            color: #31333F;
        }
        
        /* [추가] 숫자 입력칸 내부의 숫자 폰트 크기 2배 */
        .stNumberInput input {
            font-size: 2rem !important;
            height: 60px !important;
        }
        
        /* 결과 값(Metric Value) 폰트 크기 */
        [data-testid="stMetricValue"] {
            font-size: 4.5rem !important;
            font-weight: 700 !important;
        }
        
        /* 결과 레이블 폰트 크기 */
        [data-testid="stMetricLabel"] p {
            font-size: 1.6rem !important;
        }

        /* 탭 텍스트 크기 조절 */
        .stTabs [data-baseweb="tab"] p {
            font-size: 1.3rem !important;
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
        gamma1 = math.log(rh1 / 100.0) + (b * t1) / (c + t1)
        dp1 = (c * gamma1) / (b - gamma1)

        st.markdown("---")
        st.header("📊 결과 (Result)")
        st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")

# --- Tab 2: 상대습도 계산 (역산) ---
with tab2:
    st.header("📌 입력 (Input)")
    t

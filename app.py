import streamlit as st
import math

# 1. 페이지 설정 및 디자인 커스텀
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# CSS 주입: 폰트 크기 증대 및 우측 상단 문구 삽입
st.markdown("""
    <style>
        /* 우측 상단 JD Calculator 문구 */
        .jd-header {
            position: absolute;
            top: -60px;
            right: 0px;
            font-family: 'Noto Sans KR', sans-serif; /* 윤고딕 유사 폰트 */
            font-weight: 700;
            color: black;
            font-size: 24px;
        }
        
        /* 입력창 레이블(현재온도, 상대습도 등) 폰트 크기 2배 */
        .stNumberInput label p {
            font-size: 1.8rem !important;
            font-weight: 600 !important;
        }
        
        /* 결과 값(Metric Value) 폰트 크기 2배 */
        [data-testid="stMetricValue"] {
            font-size: 4rem !important;
        }
        
        /* 결과 레이블 폰트 크기 증대 */
        [data-testid="stMetricLabel"] p {
            font-size: 1.5rem !important;
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
    
    st.markdown("<br>", unsafe_allow_html=True) # 간격 조절
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        gamma1 = math.log(rh1 / 100.0) + (b * t1) / (c + t1)
        dp1 = (c * gamma1) / (b - gamma1)

        st.markdown("---")
        st.header("📊 결과 (Result)")
        st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")

# --- Tab 2: 상대습도 계산 (역산) ---
with tab2:
    st.header("📌 입력 (Input)")
    t2 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=13.9, step=0.1, key="dp2")

    st.markdown("<br>", unsafe_allow_html=True) # 간격 조절
    if st.button("상대습도 계산하기", key="btn2", use_container_width=True):
        # 역산 로직
        gamma_dp = (b * dp2) / (c + dp2)
        rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))

        st.markdown("---")
        st.header("📊 결과 (Result)")
        
        if rh2 > 100.1:
            st.error(f"오류: 노점({dp2}°C)이 현재 온도({t2}°C)보다 높을 수 없습니다.")
        else:
            st.metric(label="계산된 상대습도 (Relative Humidity)", value=f"{min(rh2, 100.0):.1f} %")

st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Professional Engineering Tool")

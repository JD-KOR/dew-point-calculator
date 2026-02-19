%%writefile app.py
import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="엔지니어링 습공기 계산기", layout="centered")

st.title("🌡️ 공기 라인 습도/노점 계산기")
st.markdown("---")

# 상단 탭으로 기능 분리 (직관적인 UI)
tab1, tab2 = st.tabs(["💧 노점 계산 (Temp/RH → DP)", "☁️ 상대습도 계산 (Temp/DP → RH)"])

# Magnus 상수
b = 17.625
c = 243.04

# --- Tab 1: 노점 계산 ---
with tab1:
    st.header("📌 입력 (Input)")
    c1, c2 = st.columns(2)
    with c1:
        t1 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t1")
    with c2:
        rh1 = st.number_input("상대습도 (%)", value=50.0, min_value=0.1, max_value=100.0, step=0.1, key="rh1")

    # 계산
    gamma1 = math.log(rh1 / 100.0) + (b * t1) / (c + t1)
    dp1 = (c * gamma1) / (b - gamma1)

    st.markdown("---")
    st.header("📊 결과 (Result)")
    st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")

# --- Tab 2: 상대습도 계산 (역산) ---
with tab2:
    st.header("📌 입력 (Input)")
    c3, c4 = st.columns(2)
    with c3:
        t2 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t2")
    with c4:
        dp2 = st.number_input("이슬점(노점) (°C)", value=13.9, step=0.1, key="dp2")

    # 역산 로직
    # 1. 노점 기준 gamma 계산
    gamma_dp = (b * dp2) / (c + dp2)
    # 2. 상대습도 계산
    rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))

    st.markdown("---")
    st.header("📊 결과 (Result)")
    
    if rh2 > 100.1:
        st.error(f"계산된 습도가 {rh2:.1f}% 입니다. 노점이 현재 온도보다 높을 수 없습니다.")
    else:
        st.metric(label="계산된 상대습도 (Relative Humidity)", value=f"{min(rh2, 100.0):.1f} %")

# 하단 정보
st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Professional Engineering Tool")

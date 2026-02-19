import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="엔지니어링 습공기 계산기", layout="centered")

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
    c1, c2 = st.columns(2)
    with c1:
        t1 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t1")
    with c2:
        rh1 = st.number_input("상대습도 (%)", value=50.0, min_value=0.1, max_value=100.0, step=0.1, key="rh1")
    
    # [변경사항] 계산 버튼 추가
    if st.button("노점 계산하기", key="btn1"):
        gamma1 = math.log(rh1 / 100.0) + (b * t1) / (c + t1)
        dp1 = (c * gamma1) / (b - gamma1)

        st.markdown("---")
        st.header("📊 결과 (Result)")
        st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")
        
        if dp1 > t1:
            st.warning("⚠️ 경고: 결로 발생 가능성이 높습니다.")
        else:
            st.success(f"현재 온도 대비 약 {t1 - dp1:.1f}°C의 여유가 있습니다.")

# --- Tab 2: 상대습도 계산 (역산) ---
with tab2:
    st.header("📌 입력 (Input)")
    c3, c4 = st.columns(2)
    with c3:
        t2 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t2")
    with c4:
        dp2 = st.number_input("이슬점(노점) (°C)", value=13.9, step=0.1, key="dp2")

    # [변경사항] 계산 버튼 추가
    if st.button("상대습도 계산하기", key="btn2"):
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

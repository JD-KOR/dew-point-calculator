import streamlit as st
import math
import matplotlib.pyplot as plt
import io

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. 세션 상태 초기화 (데이터 기록용)
if 'dp_history' not in st.session_state:
    st.session_state.dp_history = []
if 'rh_history' not in st.session_state:
    st.session_state.rh_history = []

# 3. CSS 주입 (기존 디자인 유지)
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
        .jd-header {
            text-align: right; font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700; color: #444444; font-size: 18px;
            margin-top: -40px; margin-bottom: -5px; padding-right: 5px;
        }
        h1 { font-size: 1.9rem !important; margin-bottom: -10px !important; color: #1E1E1E; }
        hr { margin-top: 0px !important; margin-bottom: 25px !important; }
        .stTabs { margin-top: -15px !important; }
        [data-baseweb="tab"] { 
            margin-right: 40px !important; padding-top: 2px !important;     
            padding-bottom: 8px !important; height: auto !important;
        }
        .stTabs [data-baseweb="tab"] p {
            font-size: 0.95rem !important; white-space: pre !important; 
            text-align: left !important; line-height: 1.5 !important;
            font-weight: 500 !important; color: #31333F; margin: 0 !important;
        }
        .stTabs [data-baseweb="tab"] p::first-line { font-size: 1.3rem !important; font-weight: 700 !important; }
        .stNumberInput, [data-testid="stMetric"], .stButton {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #f0f0f0;
        }
        [data-testid="stMetricValue"] { font-size: 3.15rem !important; font-weight: 700 !important; color: #1f77b4; }
    </style>
    <div class="jd-header">JD Calculator</div>
    """, unsafe_allow_html=True)

st.title("🌡️ 노점/상대습도 계산기")
st.markdown("---") 

tab1, tab2 = st.tabs(["💧 노점 계산\n    (Temp/RH → DP)", "☁️ 상대습도 계산\n    (Temp/DP → RH)"])

b, c = 17.625, 243.04

# --- Tab 1: 노점 계산 ---
with tab1:
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.header("📌 입력 (Input)")
    t1 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t1")
    rh1 = st.number_input("상대습도 (%)", value=None, min_value=0.1, max_value=100.0, step=0.1, format="%g", key="rh1")
    
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        if t1 is not None and rh1 is not None:
            gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
            dp1 = (c * gamma1) / (b - gamma1)
            st.session_state.dp_history.append(round(dp1, 2))
            if len(st.session_state.dp_history) > 10: st.session_state.dp_history.pop(0)
            st.markdown("---")
            st.header("📊 결과 (Result)")
            st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")
        else: st.warning("값을 입력해주세요.")

# --- Tab 2: 상대습도 계산 ---
with tab2:
    st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.header("📌 입력 (Input)")
    t2 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=None, step=0.1, format="%g", key="dp2")
    
    if st.button("상대습도 계산하기", key="btn2", use_container_width=True):
        if t2 is not None and dp2 is not None:
            gamma_dp = (b * dp2) / (c + dp2)
            rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))
            rh_val = round(min(rh2, 100.0), 1)
            st.session_state.rh_history.append(rh_val)
            if len(st.session_state.rh_history) > 10: st.session_state.rh_history.pop(0)
            st.markdown("---")
            st.header("📊 결과 (Result)")
            if rh2 > 100.1: st.error("노점이 온도보다 높을 수 없습니다.")
            else: st.metric(label="계산된 상대습도", value=f"{rh_val} %")
        else: st.warning("값을 입력해주세요.")

# --- 데이터 시각화 섹션 (하단 공통) ---
st.markdown("---")
st.header("📈 데이터 경향 분석 (Trend Analysis)")

col_target, col_name = st.columns(2)
with col_target:
    target_val = st.number_input("목표값(Target) 설정", value=0.0, step=0.1, format="%g")
with col_name:
    graph_name = st.text_input("그래프 이름 입력", value="JD_Trend_Analysis")

# 그래프 그리기 로직
history = st.session_state.dp_history if st.session_state.dp_history else st.session_state.rh_history
y_label = "Dew Point (°C)" if st.session_state.dp_history else "Relative Humidity (%)"

if history:
    fig, ax = plt.subplots(figsize=(8, 4))
    x_axis = list(range(1, len(history) + 1))
    
    # 꺾은선 그래프 (파란색, 표식 포함)
    ax.plot(x_axis, history, marker='o', linestyle='-', color='#1f77b4', linewidth=2, label='Measured')
    
    # 목표선 (빨간색)
    if target_val != 0:
        ax.axhline(y=target_val, color='red', linestyle='--', linewidth=1.5, label=f'Target ({target_val})')
    
    ax.set_xticks(range(1, 11))
    ax.set_xlabel("Input Sequence (1-10)")
    ax.set_ylabel(y_label)
    ax.set_title(graph_name)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # 캡처 및 저장 기능
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button(
        label="📸 그래프 캡처 및 저장",
        data=buf.getvalue(),
        file_name=f"{graph_name}.png",
        mime="image/png",
        use_container_width=True
    )
    
    if st.button("🧹 데이터 초기화 (Reset History)", use_container_width=True):
        st.session_state.dp_history = []
        st.session_state.rh_history = []
        st.rerun()
else:
    st.info("데이터를 입력하고 계산하면 여기에 그래프가 생성됩니다.")

st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Professional Engineering Tool")

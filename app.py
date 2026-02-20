import streamlit as st
import math
import matplotlib.pyplot as plt
import io
import pandas as pd
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. 세션 상태 초기화
if 'dp_history' not in st.session_state:
    st.session_state.dp_history = []
if 'rh_history' not in st.session_state:
    st.session_state.rh_history = []
if 'target_val' not in st.session_state:
    st.session_state.target_val = 0.0

# 3. CSS 주입 (표 글자 크기 강제 조정 포함)
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
        .jd-header {
            text-align: right; font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700; color: #444444; font-size: 15px;
            margin-top: -45px; margin-bottom: -5px; padding-right: 5px;
        }
        
        /* --- [강력 수정] 웹 화면 하단 st.table 글자 크기 및 여백 최소화 --- */
        [data-testid="stTable"] table td, 
        [data-testid="stTable"] table th,
        [data-testid="stTable"] table p,
        [data-testid="stTable"] table div {
            font-size: 0.8rem !important;  /* 여기에 원하는 크기를 입력하세요 (0.5rem 등) */
            line-height: 1.1 !important;
            padding: 4px 8px !important;
        }
        /* ------------------------------------------------------------- */

        h1 { font-size: 1.9rem !important; margin-top: -48px !important; margin-bottom: 23px !important; color: #1E1E1E; }
        hr { margin-top: 0px !important; margin-bottom: 20px !important; }
        .stTabs { margin-top: 15px !important; overflow: visible !important; }
        [data-baseweb="tab"] p::first-line { font-size: 1.3rem !important; font-weight: 700 !important; }
        .stNumberInput, [data-testid="stMetric"], .stButton {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #f0f0f0;
            margin-bottom: 10px;
        }
        [data-testid="stMetricValue"] { font-size: 3.15rem !important; font-weight: 700 !important; color: #1f77b4; }
    </style>
    <div class="jd-header">JD Calculator</div>
    """, unsafe_allow_html=True)

st.title("🌡️ 노점/상대습도 계산기")
st.markdown("---") 

tab1, tab2 = st.tabs(["💧 노점 계산\n    (Temp/RH → DP)", "☁️ 상대습도 계산\n    (Temp/DP → RH)"])
b, c = 17.625, 243.04

# --- 계산 로직 생략 (기존과 동일) ---
with tab1:
    t1 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t1")
    rh1 = st.number_input("상대습도 (%)", value=None, min_value=0.1, max_value=100.0, step=0.1, format="%g", key="rh1")
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        if t1 is not None and rh1 is not None:
            gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
            dp1 = (c * gamma1) / (b - gamma1)
            st.session_state.dp_history.append(dp1)
            if len(st.session_state.dp_history) > 10: st.session_state.dp_history.pop(0)
            st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")

with tab2:
    t2 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=None, step=0.1, format="%g", key="dp2")
    if st.button("상대습도 계산하기", key="btn2", use_container_width=True):
        if t2 is not None and dp2 is not None:
            gamma_dp = (b * dp2) / (c + dp2)
            rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))
            rh_val = min(rh2, 100.0)
            st.session_state.rh_history.append(rh_val)
            if len(st.session_state.rh_history) > 10: st.session_state.rh_history.pop(0)
            st.metric(label="계산된 상대습도", value=f"{rh_val:.1f} %")

# --- 데이터 분석 섹션 ---
st.markdown("---")
st.header("📈 데이터 경향 및 수렴성 분석")

col_target_input, _, col_graph_name = st.columns([2, 1, 2])
with col_target_input:
    st.session_state.target_val = st.number_input("목표값(Target) 입력", value=st.session_state.target_val, step=0.1, format="%g")
with col_graph_name:
    graph_name = st.text_input("그래프 이름", value="JD_Performance_Trend")

current_history = st.session_state.dp_history if st.session_state.dp_history else st.session_state.rh_history
unit = "°C" if st.session_state.dp_history else "%"

if current_history:
    # 1. 통합 리포트 생성 (이미지용)
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1.5, 1]})
    
    # 그래프 스케일 설정 (30% 여유)
    all_data = current_history + ([st.session_state.target_val] if st.session_state.target_val != 0 else [])
    ymin, ymax = min(all_data), max(all_data)
    y_range = ymax - ymin if ymax != ymin else 1.0
    ax1.plot(range(1, len(current_history)+1), current_history, marker='o', color='#1f77b4', label='Measured')
    ax1.axhline(y=st.session_state.target_val, color='#d62728', linestyle='--', label='Target')
    ax1.set_ylim(ymin - y_range * 0.3, ymax + y_range * 0.3)
    ax1.legend()
    ax1.set_title(graph_name)

    # 데이터프레임 생성
    df_analysis = pd.DataFrame({
        "No.": list(range(1, len(current_history) + 1)),
        f"Measured({unit})": [f"{v:.1f}" for v in current_history],
        f"Target({unit})": [f"{st.session_state.target_val:.1f}"] * len(current_history),
        "Gap": [f"{abs(st.session_state.target_val - v):.1f}" for v in current_history],
        "Error(%)": [f"{(abs(st.session_state.target_val - v)/st.session_state.target_val*100):.1f}%" if st.session_state.target_val != 0 else "0.0%" for v in current_history]
    })

    # 이미지용 표 (글자 크기 10 고정)
    ax2.axis('off')
    ax2.table(cellText=df_analysis.values, colLabels=df_analysis.columns, loc='center', cellLoc='center').set_fontsize(10)
    
    st.pyplot(fig)

    # 2. 웹 화면용 표 (폰트 조절됨)
    st.subheader("📋 수렴성 오차 분석")
    st.table(df_analysis) 

    # 3. 유틸리티 버튼
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    st.download_button("📸 통합 리포트 저장", buf.getvalue(), f"{graph_name}.png", "image/png", use_container_width=True)
    
    if st.button("🧹 데이터 초기화", use_container_width=True):
        st.session_state.dp_history, st.session_state.rh_history, st.session_state.target_val = [], [], 0.0
        st.rerun()
else:
    st.info("데이터를 입력해 주세요.")

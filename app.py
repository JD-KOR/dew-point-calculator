import streamlit as st
import math
import matplotlib.pyplot as plt
import io
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. 데이터 보존을 위한 세션 상태 초기화
if 'dp_history' not in st.session_state:
    st.session_state.dp_history = []
if 'rh_history' not in st.session_state:
    st.session_state.rh_history = []
if 'target_val' not in st.session_state:
    st.session_state.target_val = 0.0

# 3. CSS 주입: 디자인 정체성 유지
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
        .jd-header {
            text-align: right; font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700; color: #444444; font-size: 18px;
            margin-top: -50px; margin-bottom: -5px; padding-right: 5px;
        }
        h1 { 
            font-size: 1.9rem !important; margin-top: -48px !important;   
            margin-bottom: 23px !important; color: #1E1E1E; 
        }
        hr { margin-top: 0px !important; margin-bottom: 20px !important; }
        .stTabs { margin-top: 15px !important; overflow: visible !important; }
        [data-baseweb="tab"] { 
            margin-right: 40px !important; padding-top: 2px !important;     
            padding-bottom: 8px !important; height: auto !important;
        }
        .stTabs [data-baseweb="tab"] p {
            font-size: 0.95rem !important; white-space: pre !important; 
            text-align: left !important; line-height: 1.4 !important;
            font-weight: 500 !important; color: #31333F; margin: 0 !important;
        }
        .stTabs [data-baseweb="tab"] p::first-line { font-size: 1.3rem !important; font-weight: 700 !important; }
        .stNumberInput, [data-testid="stMetric"], .stButton, .stTable {
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

# --- Tab 1: 노점 계산 ---
with tab1:
    st.markdown('<div style="margin-top: 0px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.header("📌 입력 (Input)")
    t1 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t1")
    rh1 = st.number_input("상대습도 (%)", value=None, min_value=0.1, max_value=100.0, step=0.1, format="%g", key="rh1")
    
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        if t1 is not None and rh1 is not None:
            gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
            dp1 = (c * gamma1) / (b - gamma1)
            st.session_state.dp_history.append(dp1)
            if len(st.session_state.dp_history) > 10: st.session_state.dp_history.pop(0)
            st.markdown("---")
            st.header("📊 결과 (Result)")
            st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")
        else: st.warning("값을 입력해주세요.")

# --- Tab 2: 상대습도 계산 ---
with tab2:
    st.markdown('<div style="margin-top: 0px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.header("📌 입력 (Input)")
    t2 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=None, step=0.1, format="%g", key="dp2")
    
    if st.button("상대습도 계산하기", key="btn2", use_container_width=True):
        if t2 is not None and dp2 is not None:
            gamma_dp = (b * dp2) / (c + dp2)
            rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))
            rh_val = min(rh2, 100.0)
            st.session_state.rh_history.append(rh_val)
            if len(st.session_state.rh_history) > 10: st.session_state.rh_history.pop(0)
            st.markdown("---")
            st.header("📊 결과 (Result)")
            if rh2 > 100.1: st.error("노점이 온도보다 높을 수 없습니다.")
            else: st.metric(label="계산된 상대습도", value=f"{rh_val:.1f} %")
        else: st.warning("값을 입력해주세요.")

# --- 데이터 시각화 및 수렴성 분석 섹션 ---
st.markdown("---")
st.header("📈 데이터 경향 및 수렴성 분석")

col_target_input, col_target_btn, col_graph_name = st.columns([2, 1, 2])
with col_target_input:
    new_target = st.number_input("목표값(Target) 입력", value=st.session_state.target_val, step=0.1, format="%g")
with col_target_btn:
    st.write("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    if st.button("목표값 적용"):
        st.session_state.target_val = new_target
        st.success(f"목표가 {new_target:.1f}로 설정되었습니다.")
with col_graph_name:
    graph_name = st.text_input("그래프 이름", value="JD_Performance_Trend")

current_history = st

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

# 3. CSS 주입 (정밀 조정된 디자인 유지)
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
        .jd-header {
            text-align: right; font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700; color: #444444; font-size: 18px;
            margin-top: -50px; margin-bottom: -5px; padding-right: 5px;
        }
        h1 { 
            font-size: 1.9rem !important; 
            margin-top: -40px !important;   
            margin-bottom: 23px !important; 
            color: #1E1E1E; 
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

# --- Tab 1 & 2 로직 (기존 유지) ---
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
            st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")
        else: st.warning("값을 입력해주세요.")

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

current_history = st.session_state.dp_history if st.session_state.dp_history else st.session_state.rh_history
unit = "°C" if st.session_state.dp_history else "%"

if current_history:
    # 1. 통합 리포트 생성 (그래프 + 표)
    # 이미지 저장 시 표가 잘리지 않도록 figsize 조절 및 subplot 분할
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1.5, 1]})
    
    # [상단: 그래프 영역]
    x_axis = np.arange(1, len(current_history) + 1)
    ax1.plot(x_axis, current_history, marker='o', markersize=8, color='#1f77b4', linewidth=2.5, label='Measured Data')
    
    if st.session_state.target_val != 0:
        ax1.axhline(y=st.session_state.target_val, color='#d62728', linestyle='--', linewidth=2, label='Target')

    # --- 수정 사항 2: 스케일 여유 공간 확보 (상하 30% 마진) ---
    all_data = current_history + ([st.session_state.target_val] if st.session_state.target_val != 0 else [])
    y_min, y_max = min(all_data), max(all_data)
    y_range = y_max - y_min
    if y_range == 0: y_range = 1.0 # 모든 값이 같을 경우 대비
    ax1.set_ylim(y_min - y_range * 0.3, y_max + y_range * 0.3)
    
    ax1.set_xticks(x_axis)
    ax1.set_xlabel("Test Sequence")
    ax1.set_ylabel(f"Value ({unit})")
    ax1.set_title(f"Trend Analysis: {graph_name}", fontsize=14, pad=20)
    ax1.grid(True, linestyle=':', alpha=0.7)
    ax1.legend()

    # [하단: 표 영역 생성 (수정 사항 1)]
    ax2.axis('off')
    analysis_df = pd.DataFrame({
        "No.": list(range(1, len(current_history) + 1)),
        f"Measured({unit})": [f"{v:.1f}" for v in current_history],
        f"Target({unit})": [f"{st.session_state.target_val:.1f}"] * len(current_history),
        "Gap": [f"{abs(st.session_state.target_val - v):.1f}" for v in current_history],
        "Error(%)": [f"{(abs(st.session_state.target_val - v)/st.session_state.target_val*100):.1f}%" if st.session_state.target_val != 0 else "0.0%" for v in current_history]
    })
    
    # Matplotlib Table 생성 (한글 깨짐을 고려하여 영문 헤더 권장하거나 별도 폰트 설정 필요)
    # 여기서는 범용성을 위해 영문 키워드와 함께 구성
    the_table = ax2.table(cellText=analysis_df.values, colLabels=analysis_df.columns, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(5)
    the_table.scale(1.1, 1.8) # 표의 셀 높이 조절
    
    st.pyplot(fig)

    # 2. 웹 화면용 표 (기존 스타일 유지)
    st.subheader("📋 수렴성 오차 분석")
    st.table(analysis_df)

    # 3. 유틸리티 버튼
    col_save, col_reset = st.columns(2)
    with col_save:
        buf = io.BytesIO()
        # 이미지 저장 시 bbox_inches='tight'를 사용하여 표가 잘리지 않게 함
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        st.download_button(
            label="📸 그래프 및 데이터 통합 저장",
            data=buf.getvalue(),
            file_name=f"{graph_name}.png",
            mime="image/png",
            use_container_width=True
        )
    with col_reset:
        if st.button("🧹 모든 데이터 초기화", use_container_width=True):
            st.session_state.dp_history = []
            st.session_state.rh_history = []
            st.session_state.target_val = 0.0
            st.rerun()
else:
    st.info("데이터를 입력하면 실시간 트래킹 그래프와 오차 분석표가 나타납니다.")

st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Precision Engineering Analytics")

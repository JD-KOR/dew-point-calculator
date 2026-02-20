import streamlit as st
import math
import matplotlib.pyplot as plt
import io
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. 세션 상태 초기화
if 'dp_history' not in st.session_state:
    st.session_state.dp_history = []
if 'rh_history' not in st.session_state:
    st.session_state.rh_history = []
if 'target_val' not in st.session_state:
    st.session_state.target_val = 0.0

# 3. CSS 주입 (디자인 유지)
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); }
        .jd-header {
            text-align: right; font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700; color: #444444; font-size: 18px;
            margin-top: -50px; margin-bottom: -5px; padding-right: 5px;
        }
        h1 { font-size: 1.9rem !important; margin-top: -48px !important; margin-bottom: 23px !important; color: #1E1E1E; }
        hr { margin-top: 0px !important; margin-bottom: 20px !important; }
        .stTabs { margin-top: 15px !important; }
        [data-baseweb="tab"] { margin-right: 40px !important; padding-bottom: 8px !important; }
        .stNumberInput, [data-testid="stMetric"], .stButton {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #f0f0f0; margin-bottom: 10px;
        }
        [data-testid="stMetricValue"] { font-size: 3.15rem !important; font-weight: 700 !important; color: #1f77b4; }
    </style>
    <div class="jd-header">JD Calculator</div>
    """, unsafe_allow_html=True)

st.title("🌡️ 노점/상대습도 계산기")
st.markdown("---") 

tab1, tab2 = st.tabs(["💧 노점 계산\n    (Temp/RH → DP)", "☁️ 상대습도 계산\n    (Temp/DP → RH)"])

b, c = 17.625, 243.04

with tab1:
    st.markdown('<div style="margin-top: 0px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
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

# --- 데이터 분석 섹션 ---
st.markdown("---")
st.header("📈 데이터 경향 및 수렴성 분석")

c1, c2, c3 = st.columns([2, 1, 2])
with c1:
    new_target = st.number_input("목표값 입력", value=st.session_state.target_val, step=0.1, format="%g")
with c2:
    st.write("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    if st.button("목표 적용"): st.session_state.target_val = new_target
with c3:
    graph_name = st.text_input("그래프 이름", value="JD_Trend_Report")

# 데이터 선택 (노점 혹은 상대습도 중 값이 있는 것)
current_data = st.session_state.dp_history if st.session_state.dp_history else st.session_state.rh_history
unit = "°C" if st.session_state.dp_history else "%"

if current_data:
    # 1. 표 데이터 미리 생성
    rows = []
    for i, v in enumerate(current_data):
        target = st.session_state.target_val
        gap = abs(target - v)
        err = (gap / target * 100) if target != 0 else 0
        rows.append([i+1, f"{v:.1f}", f"{target:.1f}", f"{gap:.1f}", f"{err:.1f}%"])
    
    df = pd.DataFrame(rows, columns=["No.", f"측정({unit})", f"목표({unit})", "오차", "오차율"])

    # 2. 통합 그래프 생성
    # plt.close()를 사용하여 이전 그림 메모리 해제 (먹통 방지)
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1.8, 1]})
    
    # 상단 그래프
    x = list(range(1, len(current_data) + 1))
    ax1.plot(x, current_data, marker='o', markersize=8, color='#1f77b4', linewidth=2, label='Measured')
    if st.session_state.target_val != 0:
        ax1.axhline(y=st.session_state.target_val, color='#d62728', linestyle='--', label='Target')
    
    # Y축 범위 자동 조정 (15% 여백)
    all_vals = current_data + ([st.session_state.target_val] if st.session_state.target_val != 0 else [])
    ymin, ymax = min(all_vals), max(all_vals)
    margin = (ymax - ymin) * 0.15 if ymax != ymin else 2.0
    ax1.set_ylim(ymin - margin, ymax + margin)
    
    ax1.set_xticks(x)
    ax1.set_title(f"Performance Analysis: {graph_name}", fontsize=14, pad=20)
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.6)

    # 하단 표
    ax2.axis('off')
    the_table = ax2.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(11)
    the_table.scale(1, 1.8)

    plt.tight_layout()
    st.pyplot(fig)

    # 3. 저장 및 리셋 버튼
    b1, b2 = st.columns(2)
    with b1:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        st.download_button("📸 통합 리포트 저장", data=buf.getvalue(), file_name=f"{graph_name}.png", mime="image/png", use_container_width=True)
    with b2:
        if st.button("🧹 데이터 초기화", use_container_width=True):
            st.session_state.dp_history, st.session_state.rh_history, st.session_state.target_val = [], [], 0.0
            st.rerun()
else:
    st.info("데이터를 입력하고 계산 버튼을 누르면 분석 리포트가 생성됩니다.")

st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Precision Engineering Analytics")

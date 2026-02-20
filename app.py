import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import pandas as pd
import numpy as np

# --- 1. 한글 폰트 설정 (이미지 저장 시 깨짐 방지) ---
@st.cache_data
def get_font_family():
    font_names = [f.name for f in fm.fontManager.ttflist]
    for candidate in ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'Noto Sans CJK JP', 'sans-serif']:
        if candidate in font_names:
            return candidate
    return 'sans-serif'

font_family = get_font_family()
plt.rcParams['font.family'] = font_family
plt.rcParams['axes.unicode_minus'] = False 

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. 세션 상태 초기화
if 'dp_history' not in st.session_state:
    st.session_state.dp_history = []
if 'rh_history' not in st.session_state:
    st.session_state.rh_history = []
if 'target_val' not in st.session_state:
    st.session_state.target_val = 0.0

# 3. CSS 주입
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
        .stTabs [data-baseweb="tab"] p::first-line { font-size: 1.3rem !important; font-weight: 700 !important; }
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

# --- Tab 1 & 2 로직 (기존 유지) ---
with tab1:
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

with tab2:
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

# --- 데이터 시각화 및 수렴성 분석 섹션 ---
st.markdown("---")
st.header("📈 데이터 경향 및 수렴성 분석")

col_t_in, col_t_bt, col_g_nm = st.columns([2, 1, 2])
with col_t_in:
    new_target = st.number_input("목표값(Target) 입력", value=st.session_state.target_val, step=0.1, format="%g")
with col_t_bt:
    st.write("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    if st.button("목표값 적용"): st.session_state.target_val = new_target
with col_g_nm:
    graph_name = st.text_input("그래프 이름", value="JD_Performance_Trend")

current_history = st.session_state.dp_history if st.session_state.dp_history else st.session_state.rh_history
unit = "°C" if st.session_state.dp_history else "%"

if current_history:
    # 1. 통합 리포트 이미지 생성 (그래프 + 표)
    # 이미지 저장 시 표까지 포함하기 위해 subplots 구조 변경
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [1.2, 1]})
    
    # [상단 그래프 영역]
    x_axis = np.arange(1, len(current_history) + 1)
    ax1.plot(x_axis, current_history, marker='o', markersize=10, color='#1f77b4', lw=3, label='측정값 (Measured)')
    if st.session_state.target_val != 0:
        ax1.axhline(y=st.session_state.target_val, color='#d62728', ls='--', lw=2, label=f'목표값 ({st.session_state.target_val}{unit})')
    
    # --- 수정 사항 2: 그래프 스케일 여유 공간 확보 (상하 30% 마진) ---
    all_vals = current_history + [st.session_state.target_val]
    ymin, ymax = min(all_vals), max(all_vals)
    y_range = ymax - ymin if ymax != ymin else 1.0
    ax1.set_ylim(ymin - y_range * 0.3, ymax + y_range * 0.3)
    
    ax1.set_xticks(x_axis)
    ax1.set_xlabel("측정 순번 (Sequence)", fontsize=12, fontweight='bold')
    ax1.set_ylabel(f"측정값 ({unit})", fontsize=12, fontweight='bold')
    ax1.set_title(f"Trend Analysis: {graph_name}", fontsize=16, pad=20, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right')

    # [하단 표 영역 생성]
    ax2.axis('off')
    analysis_rows = []
    for i, val in enumerate(current_history):
        target = st.session_state.target_val
        gap = abs(target - val)
        err_pct = (gap / target * 100) if target != 0 else 0
        analysis_rows.append([i + 1, f"{val:.1f}", f"{target:.1f}", f"{gap:.1f}", f"{err_pct:.1f}%"])
    
    col_labels = ["No.", f"측정값({unit})", f"목표값({unit})", "오차(Gap)", "오차율(%)"]
    
    # --- 수정 사항 1: 표 한글 깨짐 방지 및 글자 크기 확대 ---
    the_table = ax2.table(cellText=analysis_rows, colLabels=col_labels, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(18) # 텍스트 크기 확대
    the_table.scale(1, 3.0)    # 셀 높이 확대
    
    # 표 헤더 디자인
    for (row, col), cell in the_table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2c3e50')

    # Streamlit 화면에 그래프 표시
    st.pyplot(fig)

    # 2. 웹 화면용 표 (사용자 편의)
    st.subheader("📋 실시간 데이터 리스트")
    st.table(pd.DataFrame(analysis_rows, columns=col_labels))

    # 3. 유틸리티 버튼
    col_save, col_reset = st.columns(2)
    with col_save:
        buf = io.BytesIO()
        # bbox_inches='tight'를 사용하여 표가 잘리지 않게 저장
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        st.download_button(
            label="📸 그래프+표 통합 리포트 저장",
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
    st.info("데이터를 입력하면 실시간 트래킹 그래프와 통합 분석 리포트가 생성됩니다.")

st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Precision Engineering Analytics")

import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import pandas as pd
import numpy as np

# --- 1. 한글 폰트 설정 (더욱 안정적인 방식) ---
@st.cache_data
def get_font_family():
    # 시스템 폰트 목록에서 한글 지원 폰트 확인
    font_names = [f.name for f in fm.fontManager.ttflist]
    for candidate in ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'Noto Sans CJK JP', 'Batang']:
        if candidate in font_names:
            return candidate
    return 'sans-serif'

font_family = get_font_family()
plt.rcParams['font.family'] = font_family
plt.rcParams['axes.unicode_minus'] = False 

# 2. 페이지 설정
st.set_page_config(page_title="JD Calculator", layout="centered")

# 3. 세션 상태 초기화
if 'dp_history' not in st.session_state:
    st.session_state.dp_history = []
if 'rh_history' not in st.session_state:
    st.session_state.rh_history = []
if 'target_val' not in st.session_state:
    st.session_state.target_val = 0.0

# 4. 디자인 CSS
st.markdown("""
    <style>
        .stApp { background-color: #f8f9fa; }
        .stMetric { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🌡️ 노점/상대습도 분석 계산기")

# --- 계산 로직 ---
tab1, tab2 = st.tabs(["💧 노점 계산", "☁️ 상대습도 계산"])
b, c = 17.625, 243.04

with tab1:
    t1 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t1")
    rh1 = st.number_input("상대습도 (%)", value=50.0, min_value=0.1, max_value=100.0, step=0.1, key="rh1")
    if st.button("노점 계산하기", use_container_width=True):
        gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
        dp1 = (c * gamma1) / (b - gamma1)
        st.session_state.dp_history.append(dp1)
        st.metric("계산된 노점", f"{dp1:.2f} °C")

with tab2:
    t2 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=13.0, step=0.1, key="dp2")
    if st.button("상대습도 계산하기", use_container_width=True):
        gamma_dp = (b * dp2) / (c + dp2)
        rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))
        rh_val = min(rh2, 100.0)
        st.session_state.rh_history.append(rh_val)
        st.metric("계산된 상대습도", f"{rh_val:.1f} %")

# --- 데이터 분석 섹션 ---
st.markdown("---")
st.header("📈 데이터 분석 리포트")

# 데이터 선택 (없으면 안내 메시지)
current_data = st.session_state.dp_history if st.session_state.dp_history else st.session_state.rh_history
unit = "°C" if st.session_state.dp_history else "%"

if not current_data:
    st.info("💡 위 계산 버튼을 눌러 데이터를 먼저 생성해주세요. 그래프가 여기에 나타납니다.")
else:
    # 1. 목표값 설정 및 그래프 이름
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.session_state.target_val = st.number_input("목표값 입력", value=st.session_state.target_val)
    with col_t2:
        graph_name = st.text_input("그래프 제목", value="측정 데이터 분석")

    # 2. 표 데이터 생성
    rows = []
    target = st.session_state.target_val
    for i, v in enumerate(current_data):
        gap = abs(target - v)
        err = (gap / target * 100) if target != 0 else 0
        rows.append([i+1, f"{v:.2f}", f"{target:.2f}", f"{gap:.2f}", f"{err:.1f}%"])
    
    df = pd.DataFrame(rows, columns=["번호", f"측정({unit})", f"목표({unit})", "오차", "오차율"])

    # 3. 그래프 및 표 시각화
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [1.2, 1]})
    
    # [그래프]
    x = np.arange(1, len(current_data) + 1)
    ax1.plot(x, current_data, marker='o', color='#1f77b4', lw=2, ms=8, label='측정 데이터')
    ax1.axhline(y=target, color='#d62728', ls='--', label='목표 라인')
    
    # 축 범례 추가 (수정사항 2)
    ax1.set_xlabel("측정 순번 (Count)", fontsize=12, fontweight='bold')
    ax1.set_ylabel(f"측정값 ({unit})", fontsize=12, fontweight='bold')
    ax1.set_title(graph_name, fontsize=16, pad=15)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(x)

    # 스케일 자동 조정 (수정사항 3)
    all_vals = current_data + [target]
    v_min, v_max = min(all_vals), max(all_vals)
    v_range = v_max - v_min
    if v_range == 0: v_range = 1.0 # 동일 값일 때 대비
    ax1.set_ylim(v_min - v_range * 0.3, v_max + v_range * 0.3)

    # [표] (수정사항 1: 한글 깨짐 방지 및 폰트 2배)
    ax2.axis('off')
    table = ax2.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(22) # 텍스트 크기 대폭 확대
    table.scale(1.2, 4)     # 표 높이 비율 확대

    # 표 헤더 색상 입히기
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2c3e50')

    st.pyplot(fig)

    # 리포트 저장 버튼
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button("📸 리포트 이미지 저장", buf.getvalue(), file_name="report.png", mime="image/png", use_container_width=True)

    if st.button("🧹 모든 데이터 초기화"):
        st.session_state.dp_history = []
        st.session_state.rh_history = []
        st.rerun()

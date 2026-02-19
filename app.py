import streamlit as st
import math

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. CSS 주입: 배경 눈금선 추가 및 기존 스타일 유지
st.markdown("""
    <style>
        /* [배경 설정] 모눈종이 형태의 눈금선 추가 */
        .stApp {
            background-color: #ffffff;
            background-image: 
                linear-gradient(rgba(200, 200, 200, 0.2) 1px, transparent 1px),
                linear-gradient(90deg, rgba(200, 200, 200, 0.2) 1px, transparent 1px);
            background-size: 30px 30px; /* 눈금 한 칸의 크기 */
        }

        /* [제목 폰트 크기] 70% 수준으로 축소 */
        h1 {
            font-size: 1.5rem !important; 
            margin-bottom: 1rem !important;
            color: #1E1E1E;
        }

        /* JD Calculator 문구 스타일 */
        .jd-header {
            text-align: right;
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700;
            color: black;
            font-size: 18px;
            margin-bottom: -10px;
            padding-right: 5px;
        }
        
        /* 탭 사이 간격 및 텍스트 정렬 */
        [data-baseweb="tab"] {
            margin-right: 30px !important;
            padding-left: 0px !important;
            padding-right: 10px !important;
        }

        .stTabs [data-baseweb="tab"] p {
            font-size: 0.95rem !important;
            white-space: pre-wrap !important;
            text-align: left !important;
            line-height: 1.4 !important;
            font-weight: 500 !important;
        }

        /* 입력창 및 결과값 폰트 스타일 유지 */
        .stNumberInput label p { font-size: 1.26rem !important; font-weight: 600 !important; }
        .stNumberInput input { font-size: 1.4rem !important; height: 42px !important; }
        [data-testid="stMetricValue"] { font-size: 3.15rem !important; font-weight: 700 !important; }
        
        /* 메트릭 카드 배경 살짝 투명하게 (눈금선이 보이도록) */
        [data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    <div class="jd-header">JD Calculator</div>
    """, unsafe_allow_html=True)

# 메인 제목
st.title("🌡️ 노점/상대습도 계산기")
st.markdown("---")

# 탭 구성: 정밀 정렬 유지
tab1, tab2 = st.tabs([
    "💧 노점 계산\n   (Temp/RH → DP)", 
    "☁️ 상대습도 계산\n   (Temp/DP → RH)"
])

# Magnus 상수
b = 17.625
c = 243.04

# --- Tab 1: 노점 계산 ---
with tab1:
    st.header("📌 입력 (Input)")
    t1 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t1")
    rh1 = st.number_input("상대습도 (%)", value=50.0, min_value=0.1, max_value=100.0, step=0.1, key="rh1")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
        dp1 = (c * gamma1) / (b - gamma1)
        st.markdown("---")
        st.header("📊 결과 (Result)")
        st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")

# --- Tab 2: 상대습도 계산 ---
with tab2:
    st.header("📌 입력 (Input)")
    t2 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=13.9, step=0.1, key="dp2")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("상대습도 계산하기", key="btn2", use_container_width=True):
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

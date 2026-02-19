import streamlit as st
import math

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. CSS 주입: 탭과 콘텐츠 사이의 유격을 최소화
st.markdown("""
    <style>
        /* 배경 설정 */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        }

        /* [JD Calculator 위치] */
        .jd-header {
            text-align: right;
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 700;
            color: #444444;
            font-size: 18px;
            margin-top: -40px; 
            margin-bottom: -5px;
            padding-right: 5px;
        }

        /* [제목 설정] */
        h1 {
            font-size: 1.9rem !important; 
            margin-bottom: -15px !important;
            color: #1E1E1E;
        }
        
        /* 상단 메인 구분선 스타일 */
        hr {
            margin-top: 0px !important;
            margin-bottom: 20px !important;
        }

        /* [탭 전체 위치 조절] */
        .stTabs { 
            margin-top: -15px !important; 
            overflow: visible !important; 
        }

        /* [핵심 수정: 탭 버튼] 글자와 빨간 라인 사이 간격을 8px로 축소 */
        [data-baseweb="tab"] { 
            margin-right: 40px !important; 
            padding-top: 2px !important;     
            padding-bottom: 8px !important;  /* 기존 25px -> 8px로 축소 */
            height: auto !important;
            overflow: visible !important;
        }

        /* [핵심 수정: 탭 패널] 빨간 라인 바로 밑의 여백을 제거 */
        [data-testid="stTabPanel"] {
            padding-top: 0px !important;
        }

        /* 탭 텍스트 설정 */
        .stTabs [data-baseweb="tab"] p {
            font-size: 0.95rem !important; 
            white-space: pre !important; 
            text-align: left !important;
            line-height: 1.4 !important;
            font-weight: 500 !important;
            color: #31333F;
            margin: 0 !important;
        }

        /* 탭 첫 줄 강조 */
        .stTabs [data-baseweb="tab"] p::first-line {
            font-size: 1.3rem !important; 
            font-weight: 700 !important;
        }

        /* 카드 디자인 스타일 */
        .stNumberInput, [data-testid="stMetric"], .stButton {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
            margin-bottom: 10px;
        }
        .stNumberInput label p { font-size: 1.26rem !important; font-weight: 600 !important; }
        .stNumberInput input { font-size: 1.4rem !important; height: 42px !important; }
        [data-testid="stMetricValue"] { font-size: 3.15rem !important; font-weight: 700 !important; color: #1f77b4; }
    </style>
    <div class="jd-header">JD Calculator</div>
    """, unsafe_allow_html=True)

st.title("🌡️ 노점/상대습도 계산기")
st.markdown("---") 

# 3. 탭 구성
tab1, tab2 = st.tabs([
    "💧 노점 계산\n    (Temp/RH → DP)", 
    "☁️ 상대습도 계산\n    (Temp/DP → RH)"
])

# 계산 로직 (Magnus Formula)
b = 17.625
c = 243.04

with tab1:
    # [수정] 빨간 라인과 구분선 사이의 간격을 0으로 조정
    st.markdown('<div style="margin-top: 0px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("📌 입력 (Input)")
    t1 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t1")
    rh1 = st.number_input("상대습도 (%)", value=50.0, min_value=0.1, max_value=100.0, step=0.1, key="rh1")
    
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
        dp1 = (c * gamma1) / (b - gamma1)
        st.markdown("---")
        st.header("📊 결과 (Result)")
        st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")

with tab2:
    # [수정] 빨간 라인과 구분선 사이의 간격을 0으로 조정
    st.markdown('<div style="margin-top: 0px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("📌 입력 (Input)")
    t2 = st.number_input("현재 온도 (°C)", value=25.0, step=0.1, key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=13.9, step=0.1, key="dp2")
    
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

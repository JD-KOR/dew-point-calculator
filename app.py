import streamlit as st
import math

# 1. 페이지 설정
st.set_page_config(page_title="JD Calculator - Dew Point", layout="centered")

# 2. CSS 주입: 디자인 및 레이아웃 최적화
st.markdown("""
    <style>
        /* 배경 설정: 은은한 그라데이션 */
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
            margin-bottom: -10px !important;
            color: #1E1E1E;
        }
        
        /* 상단 메인 구분선 스타일 */
        hr {
            margin-top: 0px !important;
            margin-bottom: 25px !important;
        }

        /* [탭 전체 위치 조절] */
        .stTabs { 
            margin-top: -15px !important; 
            overflow: visible !important; 
        }

        /* [탭 버튼 설정] 하단 간격 축소 */
        [data-baseweb="tab"] { 
            margin-right: 40px !important; 
            padding-top: 2px !important;     
            padding-bottom: 8px !important;  
            height: auto !important;
            overflow: visible !important;
        }

        /* 탭 텍스트 설정 (괄호 포함) */
        .stTabs [data-baseweb="tab"] p {
            font-size: 0.95rem !important; 
            white-space: pre !important; 
            text-align: left !important;
            line-height: 1.5 !important;
            font-weight: 500 !important;
            color: #31333F;
            margin: 0 !important;
        }

        /* 탭 첫 줄 강조 및 크기 확대 */
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

# Magnus 상수
b = 17.625
c = 243.04

with tab1:
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("📌 입력 (Input)")
    # [수정] value=None으로 초기화, format="%g"로 불필요한 0 제거
    t1 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t1")
    rh1 = st.number_input("상대습도 (%)", value=None, min_value=0.1, max_value=100.0, step=0.1, format="%g", key="rh1")
    
    if st.button("노점 계산하기", key="btn1", use_container_width=True):
        if t1 is not None and rh1 is not None:
            gamma1 = math.log(rh1 / 100.0) + (b * t1 / (c + t1))
            dp1 = (c * gamma1) / (b - gamma1)
            st.markdown("---")
            st.header("📊 결과 (Result)")
            st.metric(label="계산된 이슬점 (Dew Point)", value=f"{dp1:.2f} °C")
        else:
            st.warning("온도와 상대습도를 모두 입력해주세요.")

with tab2:
    st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("📌 입력 (Input)")
    # [수정] value=None으로 초기화, format="%g"로 불필요한 0 제거
    t2 = st.number_input("현재 온도 (°C)", value=None, step=0.1, format="%g", key="t2")
    dp2 = st.number_input("이슬점(노점) (°C)", value=None, step=0.1, format="%g", key="dp2")
    
    if st.button("상대습도 계산하기", key="btn2", use_container_width=True):
        if t2 is not None and dp2 is not None:
            gamma_dp = (b * dp2) / (c + dp2)
            rh2 = 100 * math.exp(gamma_dp - (b * t2) / (c + t2))
            st.markdown("---")
            st.header("📊 결과 (Result)")
            if rh2 > 100.1:
                st.error(f"오류: 노점({dp2}°C)이 현재 온도({t2}°C)보다 높을 수 없습니다.")
            else:
                st.metric(label="계산된 상대습도 (Relative Humidity)", value=f"{min(rh2, 100.0):.1f} %")
        else:
            st.warning("온도와 이슬점을 모두 입력해주세요.")

st.markdown("---")
st.caption("Calculation based on Magnus-Tetens Formula | Professional Engineering Tool")

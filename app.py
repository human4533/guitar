import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import time
import datetime
from datetime import timedelta

# 화면을 넓게 쓰기 위한 설정 (원치 않으시면 지워도 됩니다)
st.set_page_config(layout="wide")

st.title("📈 내 기타 성장 일기 (목표 달성 버전)")
st.write("목표를 설정하고 경험치 바를 채워보세요!")

# 1. 데이터 저장할 파일 준비
DATA_FILE = "practice_data.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["날짜", "연습 종류", "곡 명", "최고 BPM", "연습 분", "연습 초"])

# 2. 세션 상태 관리
if "status" not in st.session_state:
    st.session_state.status = "ready"
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed_min" not in st.session_state:
    st.session_state.elapsed_min = 0
if "elapsed_sec" not in st.session_state:
    st.session_state.elapsed_sec = 0

# ==========================================
# 🎯 [신규 기능] 사이드바: 주간 목표 설정
# ==========================================
st.sidebar.header("🎯 나의 주간 연습 목표")
weekly_goal = st.sidebar.number_input("이번 주 목표 시간 (분)", min_value=10, max_value=2000, value=120, step=10)
st.sidebar.write(f"하루 평균 **{round(weekly_goal/7, 1)}분**씩 연습하면 달성할 수 있어요!")

# ==========================================
# 🔥 [신규 기능] 메인 화면: 목표 달성률 프로그레스 바
# ==========================================
st.write("---")
st.subheader("🔥 이번 주 목표 달성률")

if not df.empty:
    # '날짜' 데이터를 진짜 날짜 형식으로 변환하여 최근 7일(이번 주) 데이터만 걸러내기
    df_calc = df.copy()
    df_calc["날짜"] = pd.to_datetime(df_calc["날짜"]).dt.date
    df_calc["총 연습 시간(분)"] = df_calc["연습 분"] + (df_calc["연습 초"] / 60)
    
    today = datetime.date.today()
    seven_days_ago = today - timedelta(days=7)
    recent_df = df_calc[df_calc["날짜"] > seven_days_ago]
    
    # 최근 7일 연습 시간 합산
    recent_total = recent_df["총 연습 시간(분)"].sum()
    
    # 달성률(%) 계산 (최대 1.0 = 100%)
    progress_pct = min(recent_total / weekly_goal, 1.0)
    
    # 프로그레스 바 그리기
    st.progress(progress_pct)
    st.write(f"**현재 {recent_total:.1f}분** / 목표 {weekly_goal}분 (달성률: {progress_pct*100:.1f}%)")
    
    # 100% 달성 시 축하 이벤트
    if progress_pct >= 1.0:
        st.success("🎉 이번 주 목표 달성!! 훌륭한 기타리스트가 되어가고 있습니다!")
        st.balloons() # 풍선 애니메이션 날리기
else:
    st.info("아직 이번 주 기록이 없습니다. 타이머를 켜고 첫 경험치를 획득하세요!")

st.write("---")

# ==========================================
# 기존 기능: 타이머 및 기록 저장
# ==========================================
st.subheader("✍️ 오늘 연습 기록하기")

col1, col2 = st.columns(2)
with col1:
    practice_type = st.selectbox("연습 종류", ["크로매틱", "스케일 연습", "곡 카피", "이론 공부"])
    song_title = st.text_input("곡 명 (선택 사항)", placeholder="예: AC/DC - Back in Black")
with col2:
    bpm_input = st.number_input("최고 BPM (해당 없으면 0)", min_value=0, max_value=300, step=5)
    
    time_col1, time_col2 = st.columns(2)
    with time_col1:
        min_input = st.number_input("연습 분", min_value=0, max_value=600, value=int(st.session_state.elapsed_min), step=1)
    with time_col2:
        sec_input = st.number_input("연습 초", min_value=0, max_value=59, value=int(st.session_state.elapsed_sec), step=1)

st.write(" ")

if st.session_state.status == "ready":
    st.info("💡 아래 버튼을 눌러 스톱워치를 켜고 연습을 시작하세요.")
    if st.button("▶️ 연습 시작하기", type="primary", use_container_width=True):
        st.session_state.status = "running"
        st.session_state.start_time = time.time()
        st.rerun()

elif st.session_state.status == "running":
    st.warning("🎸 집중! 기타 연습 스톱워치가 돌아가고 있습니다... 🔥")
    elapsed_seconds = int(time.time() - st.session_state.start_time)
    timer_html = f"""
    <div style="font-family: sans-serif; font-size: 3rem; font-weight: bold; color: #FF4B4B; text-align: center; padding: 10px;">
        ⏱️ <span id="timer">00:00</span>
    </div>
    <script>
        let totalSeconds = {elapsed_seconds};
        function updateTime() {{
            let m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
            let s = (totalSeconds % 60).toString().padStart(2, '0');
            document.getElementById("timer").innerText = m + ":" + s;
            totalSeconds++;
        }}
        updateTime();
        setInterval(updateTime, 1000);
    </script>
    """
    components.html(timer_html, height=100)

    if st.button("⏹️ 연습 종료하기", use_container_width=True):
        final_elapsed_seconds = int(time.time() - st.session_state.start_time)
        st.session_state.elapsed_min = final_elapsed_seconds // 60
        st.session_state.elapsed_sec = final_elapsed_seconds % 60
        st.session_state.status = "stopped"
        st.rerun()

elif st.session_state.status == "stopped":
    st.success(f"⏱️ 수고하셨습니다! 연습 시간({st.session_state.elapsed_min}분 {st.session_state.elapsed_sec}초)이 우측 칸에 자동 입력되었습니다.")
    if st.button("💾 최종 기록 저장하기", type="primary", use_container_width=True):
        new_data = pd.DataFrame({
            "날짜": [str(datetime.date.today())],
            "연습 종류": [practice_type],
            "곡 명": [song_title if song_title else "-"],
            "최고 BPM": [bpm_input],
            "연습 분": [min_input],
            "연습 초": [sec_input]
        })
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.session_state.status = "ready"
        st.session_state.elapsed_min = 0
        st.session_state.elapsed_sec = 0
        st.rerun()

st.write("---")
st.subheader("📊 나의 성장 그래프")

if not df.empty:
    tab1, tab2 = st.tabs(["🔥 크로매틱 속도 변화", "⏱️ 일일 연습 시간 추이"])
    with tab1:
        bpm_data = df[df["연습 종류"] == "크로매틱"].set_index("날짜")["최고 BPM"]
        if not bpm_data.empty:
            st.line_chart(bpm_data)
        else:
            st.info("아직 크로매틱 연습 기록이 없습니다.")
    with tab2:
        # df_calc는 위에서 만들어두었으므로 그대로 사용
        time_data = df_calc.groupby("날짜")["총 연습 시간(분)"].sum()
        st.line_chart(time_data)
        
    st.write("### 📝 전체 기록 표")
    st.dataframe(df, use_container_width=True)
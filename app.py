import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import time
import datetime
from datetime import timedelta
import hashlib

st.set_page_config(layout="wide")

# 비밀번호 암호화 함수
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

st.title("📈 내 기타 성장 일기 (보안 강화 버전)")
st.write("나만의 닉네임과 비밀번호로 안전하게 일기를 관리하세요!")

# 데이터 파일 정의
DATA_FILE = "practice_data.csv"
columns_list = ["아이디", "비밀번호", "날짜", "연습 종류", "곡 명", "최고 BPM", "연습 분", "연습 초"]

# 최신 파일 데이터를 안전하게 불러오는 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df_loaded = pd.read_csv(DATA_FILE)
            if df_loaded.empty or len(df_loaded.columns) == 0:
                return pd.DataFrame(columns=columns_list)
            return df_loaded
        except Exception:
            return pd.DataFrame(columns=columns_list)
    return pd.DataFrame(columns=columns_list)

# 세션 상태 관리 (로그인 및 기록 데이터 유지)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "status" not in st.session_state:
    st.session_state.status = "ready"
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed_min" not in st.session_state:
    st.session_state.elapsed_min = 0
if "elapsed_sec" not in st.session_state:
    st.session_state.elapsed_sec = 0

# 항상 파일에서 최신 데이터를 불러옵니다.
df = load_data()

# ==========================================
# 🔑 사이드바: 로그인 / 회원가입 창 구현
# ==========================================
st.sidebar.header("🔐 회원 시스템")

if not st.session_state.logged_in:
    menu = ["로그인", "회원가입"]
    choice = st.sidebar.selectbox("메뉴 선택", menu)
    
    if choice == "로그인":
        login_user = st.sidebar.text_input("닉네임(아이디)", key="login_id")
        login_password = st.sidebar.text_input("비밀번호", type="password", key="login_pw")
        
        if st.sidebar.button("로그인하기", use_container_width=True):
            if login_user and login_password:
                hashed_pswd = make_hashes(login_password)
                
                # 가입된 데이터가 있는지 확인
                if not df.empty:
                    # 정확히 아이디와 비밀번호가 일치하는 행 검색
                    user_record = df[(df["아이디"] == login_user) & (df["비밀번호"] == hashed_pswd)]
                    
                    if not user_record.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_id = login_user
                        st.sidebar.success(f"👋 반갑습니다, {login_user}님!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ 비밀번호가 틀렸거나 존재하지 않는 아이디입니다.")
                else:
                    st.sidebar.error("❌ 등록된 회원이 없습니다. 회원가입을 먼저 해주세요.")
            else:
                st.sidebar.error("아이디와 비밀번호를 모두 입력해 주세요.")
                    
    elif choice == "회원가입":
        new_user = st.sidebar.text_input("사용할 닉네임(아이디)", key="reg_id")
        new_password = st.sidebar.text_input("비밀번호 설정", type="password", key="reg_pw")
        
        if st.sidebar.button("가입하기", use_container_width=True):
            if new_user == "" or new_password == "":
                st.sidebar.error("빈칸을 모두 채워주세요.")
            elif not df.empty and new_user in df["아이디"].values:
                st.sidebar.error(" 이미 존재하는 닉네임입니다. 다른 이름을 사용해 주세요.")
            else:
                # 안전하게 새로 가입 정보를 누적하여 파일 저장
                hashed_new_password = make_hashes(new_password)
                signup_data = pd.DataFrame({
                    "아이디": [new_user], "비밀번호": [hashed_new_password],
                    "날짜": [str(datetime.date.today())], "연습 종류": ["가입 안내"],
                    "곡 명": ["첫 가입을 환영합니다!"], "최고 BPM": [0], "연습 분": [0], "연습 초": [0]
                })
                df = pd.concat([df, signup_data], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.sidebar.success("🎉 가입 성공! 로그인 메뉴를 선택해 로그인해 주세요.")

else:
    st.sidebar.write(f"🦁 현재 로그인: **{st.session_state.user_id}**님")
    if st.sidebar.button("로그아웃", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = ""
        st.rerun()

# ==========================================
# 🎸 메인 화면 제어 (로그인 안 되면 블라인드)
# ==========================================
if not st.session_state.logged_in:
    st.warning("🔒 이 일기장은 비공개 개인 일기장입니다. 왼쪽 메뉴에서 로그인을 진행해 주세요.")
    st.info("💡 처음 오셨다면 '회원가입'을 먼저 눌러 나만의 닉네임과 비밀번호를 만드시면 됩니다!")
else:
    # 🚨 로그인한 내 아이디 기록만 필터링
    my_df = df[df["아이디"] == st.session_state.user_id]
    
    st.sidebar.write("---")
    st.sidebar.subheader("🎯 나의 주간 연습 목표")
    weekly_goal = st.sidebar.number_input("이번 주 목표 시간 (분)", min_value=10, max_value=2000, value=120, step=10)
    
    st.write("---")
    st.subheader(f"🔥 {st.session_state.user_id}님의 이번 주 목표 달성률")
    
    real_practice_df = my_df[my_df["연습 종류"] != "가입 안내"]
    
    if not real_practice_df.empty:
        try:
            df_calc = real_practice_df.copy()
            df_calc["날짜"] = pd.to_datetime(df_calc["날짜"]).dt.date
            df_calc["총 연습 시간(분)"] = df_calc["연습 분"] + (df_calc["연습 초"] / 60)
            
            today = datetime.date.today()
            seven_days_ago = today - timedelta(days=7)
            recent_df = df_calc[df_calc["날짜"] > seven_days_ago]
            
            recent_total = recent_df["총 연습 시간(분)"].sum()
            progress_pct = min(recent_total / weekly_goal, 1.0)
            
            st.progress(progress_pct)
            st.write(f"**현재 {recent_total:.1f}분** / 목표 {weekly_goal}분 (달성률: {progress_pct*100:.1f}%)")
            
            if progress_pct >= 1.0:
                st.success("🎉 이번 주 목표 달성!!")
                st.balloons()
        except Exception:
            st.info("데이터 계산 중입니다.")
    else:
        st.info("아직 이번 주 기록이 없습니다. 타이머를 켜고 첫 경험치를 획득하세요!")
        
    st.write("---")
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
        st.success(f"⏱️ 연습 완료! 정보가 자동 입력되었습니다.")
        if st.button("💾 최종 기록 저장하기", type="primary", use_container_width=True):
            # 최신 전체 데이터 다시 로드 후 누적 저장
            df_latest = load_data()
            
            # 내 계정의 가입 시 비밀번호 해시 찾기
            user_rows = df_latest[df_latest["아이디"] == st.session_state.user_id]
            current_pw_hash = user_rows["비밀번호"].values[0] if not user_rows.empty else ""
            
            new_data = pd.DataFrame({
                "아이디": [st.session_state.user_id],
                "비밀번호": [current_pw_hash],
                "날짜": [str(datetime.date.today())],
                "연습 종류": [practice_type],
                "곡 명": [song_title if song_title else "-"],
                "최고 BPM": [bpm_input],
                "연습 분": [min_input],
                "연습 초": [sec_input]
            })
            
            df_combined = pd.concat([df_latest, new_data], ignore_index=True)
            df_combined.to_csv(DATA_FILE, index=False)
            
            st.session_state.status = "ready"
            st.session_state.elapsed_min = 0
            st.session_state.elapsed_sec = 0
            st.rerun()
            
    st.write("---")
    st.subheader(f"📊 {st.session_state.user_id}님의 성장 그래프")
    
    if not real_practice_df.empty:
        tab1, tab2 = st.tabs(["🔥 크로매틱 속도 변화", "⏱️ 일일 연습 시간 추이"])
        with tab1:
            bpm_data = real_practice_df[real_practice_df["연습 종류"] == "크로매틱"].set_index("날짜")["최고 BPM"]
            if not bpm_data.empty:
                st.line_chart(bpm_data)
            else:
                st.info("아직 크로매틱 연습 기록이 없습니다.")
        with tab2:
            try:
                time_data = df_calc.groupby("날짜")["총 연습 시간(분)"].sum()
                st.line_chart(time_data)
            except Exception:
                st.info("그래프를 구성 중입니다.")
                
        st.write("### 📝 나의 전체 기록 표")
        st.dataframe(real_practice_df.drop(columns=["비밀번호"]), use_container_width=True)
    else:
        st.info("아직 저장된 기타 연습 기록이 없습니다. 오늘 첫 연습을 시작해 보세요!")
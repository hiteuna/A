import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"
ADMIN_PASSWORD = "123"

st.set_page_config(page_title="2026 발표대회", layout="centered")

st.markdown("""
    <style>
    h3 { font-size: 1.3rem !important; text-align: center; }
    div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🏆 2026 남북한 사회통합사례 발표대회")

# [핵심] 웹사이트 주소 뒤에 붙은 ?judge=숫자 값을 읽어옴 (예: ?judge=1 이면 "심사위원 1번")
query_params = st.query_params
judge_num = query_params.get("judge", None)

if not judge_num:
    st.error("⚠️ 잘못된 접근입니다. 문자로 받으신 개인 링크를 통해 접속해 주세요!")
    st.stop()

current_judge = f"심사위원 {judge_num}번"

tab1, tab2 = st.tabs(["심사위원용", "🔒 주최측 관리자"])

with tab1:
    st.info(f"💡 안녕하세요! **{current_judge}**님용 평가 페이지입니다.\n\n- 발표를 보며 점수를 선택하고 **[저장]**을 누르면 실시간으로 기록됩니다.\n- 링크만 가지고 계시면 나중에 다시 들어와도 이어서 평가하실 수 있습니다!")
    
    presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
    
    for p in presenters:
        with st.form(key=f"form_{p}"):
            st.subheader(f"발표자: {p}")
            
            # 파일 읽기 및 기존 점수 불러오기
            if not os.path.exists(DATA_FILE):
                pd.DataFrame(columns=["심사위원"] + presenters).to_csv(DATA_FILE, index=False)
            df = pd.read_csv(DATA_FILE)
            
            # 해당 심사위원의 기존 점수 찾기
            stored_score = 5
            if current_judge in df["심사위원"].values:
                val = df.loc[df["심사위원"] == current_judge, p].values[0]
                if pd.notna(val): 
                    stored_score = int(val)

            score = st.radio(
                f"{p} 점수 선택", 
                list(range(11)), 
                index=stored_score, 
                horizontal=True, 
                key=f"radio_{current_judge}_{p}"
            )
            
            if st.form_submit_button(f"💾 '{p}' 점수 저장"):
                if current_judge not in df["심사위원"].values:
                    new_row = pd.DataFrame([{"심사위원": current_judge}])
                    df = pd.concat([df, new_row], ignore_index=True)
                
                df.loc[df["심사위원"] == current_judge, p] = score
                df.to_csv(DATA_FILE, index=False)
                st.success(f"'{p}' 발표자 점수({score}점)가 안전하게 저장되었습니다!")

with tab2:
    password = st.text_input("비밀번호", type="password")
    if password == ADMIN_PASSWORD:
        if st.button("🔄 데이터 초기화"):
            if os.path.exists(DATA_FILE): 
                os.remove(DATA_FILE)
            st.success("데이터가 초기화되었습니다.")
            st.rerun()
            
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                st.write("### 📋 상세 점수 현황", df)
                numeric_df = df.drop(columns=["심사위원"])
                result_df = pd.DataFrame({"총점": numeric_df.sum(), "평균점수": numeric_df.mean()}).round(2)
                result_df["등수"] = result_df["평균점수"].rank(ascending=False, method="min").astype(int)
                st.write("### 📊 최종 결과", result_df.sort_values(by="평균점수", ascending=False))
            else:
                st.info("아직 제출된 점수가 없습니다.")
        else:
            st.info("아직 제출된 점수가 없습니다.")
    else:
        st.warning("비밀번호가 필요합니다.")

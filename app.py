import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"
ADMIN_PASSWORD = "123"

st.set_page_config(page_title="2026 발표대회 O/X 심사", layout="centered")

st.markdown("""
    <style>
    h3 { font-size: 1.3rem !important; text-align: center; }
    div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🏆 2026 남북한 사회통합사례 발표대회 (O/X 심사)")

query_params = st.query_params
judge_num = query_params.get("judge", None)

tab1, tab2 = st.tabs(["심사위원용", "🔒 주최측 관리자"])

with tab1:
    if not judge_num:
        st.warning("⚠️ 개인 심사 링크로 접속하지 않으셨습니다.\n심사위원분들은 문자로 받으신 전용 링크로 다시 접속해 주세요.")
    else:
        current_judge = f"심사위원 {judge_num}번"
        st.info(f"💡 안녕하세요! **{current_judge}**님용 O/X 평가 페이지입니다.")
        
        presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
        
        for p in presenters:
            with st.form(key=f"form_{p}"):
                st.subheader(f"발표자: {p}")
                if not os.path.exists(DATA_FILE):
                    pd.DataFrame(columns=["심사위원"] + presenters).to_csv(DATA_FILE, index=False)
                df = pd.read_csv(DATA_FILE)
                
                # 기존 저장값 불러오기 (기본값은 'O' 또는 선택 안 함)
                stored_val = "O"
                if current_judge in df["심사위원"].values:
                    val = df.loc[df["심사위원"] == current_judge, p].values[0]
                    if pd.notna(val) and val in ["O", "X"]: 
                        stored_val = val

                options = ["O", "X"]
                default_idx = options.index(stored_val) if stored_val in options else 0

                score = st.radio(
                    f"{p} 평가", 
                    options, 
                    index=default_idx, 
                    horizontal=True, 
                    key=f"radio_{current_judge}_{p}"
                )
                
                if st.form_submit_button(f"💾 '{p}' 저장"):
                    if current_judge not in df["심사위원"].values:
                        new_row = pd.DataFrame([{"심사위원": current_judge}])
                        df = pd.concat([df, new_row], ignore_index=True)
                    df.loc[df["심사위원"] == current_judge, p] = score
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"'{p}' 평가({score}) 저장 완료!")

with tab2:
    password = st.text_input("관리자 비밀번호", type="password")
    if password == ADMIN_PASSWORD:
        if st.button("🔄 데이터 초기화"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.success("데이터가 초기화되었습니다.")
            st.rerun()
            
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                st.write("### 📋 심사위원별 상세 현황", df)
                
                # O/X 개수 합산 및 집계 계산
                numeric_df = df.drop(columns=["심사위원"])
                
                # 발표자별 'O'의 개수와 'X'의 개수 계산
                o_counts = (numeric_df == "O").sum()
                x_counts = (numeric_df == "X").sum()
                total_votes = o_counts + x_counts
                
                result_df = pd.DataFrame({
                    "O 개수": o_counts,
                    "X 개수": x_counts,
                    "총 참여 심사위원수": total_votes
                })
                
                # O 개수가 많은 순으로 등수 매기기
                result_df["순위"] = result_df["O 개수"].rank(ascending=False, method="min").astype(int)
                
                st.write("### 📊 발표자별 O/X 집계 결과", result_df.sort_values(by="O 개수", ascending=False))
            else:
                st.info("아직 제출된 심사 결과가 없습니다.")
        else:
            st.info("아직 제출된 심사 결과가 없습니다.")
    else:
        st.warning("관리자 비밀번호를 입력해 주세요.")

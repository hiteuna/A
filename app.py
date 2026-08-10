import pandas as pd
import streamlit as st

# 관리자 비밀번호 설정 (원하시는 숫자로 바꾸세요)
ADMIN_PASSWORD = "123"

if "shared_db" not in st.session_state:
    st.session_state.shared_db = []

st.title("🏆 2026 남북한 사회통합사례 발표대회")

# 탭 나누기 (심사위원용 / 주최측용)
tab1, tab2 = st.tabs(["심사위원용", "주최측 관리자용"])

with tab1:
    st.subheader("심사위원님 환영합니다!")
    with st.form("score_form"):
        presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
        current_judge_scores = {}
        for presenter in presenters:
            current_judge_scores[presenter] = st.slider(f"발표자: {presenter}", 0, 10, 5)
        
        if st.form_submit_button("📤 최종 점수 제출하기"):
            st.session_state.shared_db.append(current_judge_scores)
            st.success("점수가 제출되었습니다!")

with tab2:
    st.subheader("🔒 주최측 관리자 전용")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if password == ADMIN_PASSWORD:
        if st.button("🔄 테스트 데이터 초기화"):
            st.session_state.shared_db = []
            st.rerun()
            
        if len(st.session_state.shared_db) > 0:
            df_all = pd.DataFrame(st.session_state.shared_db)
            result_df = pd.DataFrame({"총점": df_all.sum(), "평균점수": df_all.mean()})
            result_df["등수"] = result_df["평균점수"].rank(ascending=False, method="min").astype(int)
            st.dataframe(result_df.sort_values(by="평균점수", ascending=False), use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
    else:
        st.warning("비밀번호를 입력해야 현황이 보입니다.")

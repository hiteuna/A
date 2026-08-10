import pandas as pd
import streamlit as st
import os

ADMIN_PASSWORD = "123"
DATA_FILE = "submissions.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["심사위원", "김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]).to_csv(DATA_FILE, index=False)

st.title("🏆 2026 남북한 사회통합사례 발표대회")

tab1, tab2 = st.tabs(["심사위원용", "주최측 관리자용"])

with tab1:
    st.subheader("심사위원님 환영합니다!")
    with st.form("score_form", clear_on_submit=True):
        presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
        
        st.write("각 발표자의 점수를 선택해 주세요 (0 ~ 10점)")
        current_agent_scores = {}
        
        # [수정된 부분] 0부터 10까지의 점수를 가로 버튼(radio)으로 분리하여 배치
        for p in presenters:
            current_agent_scores[p] = st.radio(
                f"발표자: {p}",
                options=list(range(11)), # 0부터 10까지
                index=5, # 기본 선택값 5점
                horizontal=True # 가로로 배치하여 스마트폰에서 보기 편하게 설정
            )
        
        if st.form_submit_button("📤 최종 점수 제출하기"):
            df = pd.read_csv(DATA_FILE)
            new_entry = {"심사위원": f"심사위원 {len(df) + 1}번"}
            new_entry.update(current_agent_scores)
            
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("점수가 기록되었습니다!")

with tab2:
    st.subheader("🔒 주최측 관리자 전용")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if password == ADMIN_PASSWORD:
        if st.button("🔄 데이터 초기화"):
            pd.DataFrame(columns=["심사위원", "김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]).to_csv(DATA_FILE, index=False)
            st.rerun()
            
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                st.write("### 📋 심사위원별 상세 점수 현황")
                st.dataframe(df, use_container_width=True)
                
                st.write("### 📊 최종 결과 (평균 순위)")
                numeric_df = df.drop(columns=["심사위원"])
                result_df = pd.DataFrame({"총점": numeric_df.sum(), "평균점수": numeric_df.mean()})
                result_df["등수"] = result_df["평균점수"].rank(ascending=False, method="min").astype(int)
                st.dataframe(result_df.sort_values(by="평균점수", ascending=False), use_container_width=True)
            else:
                st.info("아직 제출된 점수가 없습니다.")
    else:
        st.warning("비밀번호를 입력해야 현황이 보입니다.")

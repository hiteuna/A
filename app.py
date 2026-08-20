import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"

st.set_page_config(page_title="심사 평가", layout="centered")

st.markdown("<h3 style='text-align: center;'>🏆 2026 남북한 사회통합사례 발표대회</h3>", unsafe_allow_html=True)
st.write("---")

with st.form("score_form", clear_on_submit=True):
    presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
    current_agent_scores = {p: st.radio(f"발표자: {p}", list(range(11)), index=5, horizontal=True) for p in presenters}
    
    if st.form_submit_button("📤 최종 점수 제출하기"):
        if not os.path.exists(DATA_FILE):
            pd.DataFrame(columns=["심사위원"] + presenters).to_csv(DATA_FILE, index=False)
            
        df = pd.read_csv(DATA_FILE)
        new_entry = {"심사위원": f"심사위원 {len(df) + 1}번"}
        new_entry.update(current_agent_scores)
        
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("점수가 제출되었습니다!")

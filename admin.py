import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"

st.set_page_config(page_title="관리자 집계", layout="wide")
st.title("🔒 관리자 집계 페이지")

password = st.text_input("비밀번호 입력", type="password")
if password == "123":
    if st.button("🔄 데이터 초기화"):
        os.remove(DATA_FILE)
        st.rerun()
    
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.write("### 📋 상세 점수 현황", df)
        numeric_df = df.drop(columns=["심사위원"])
        result_df = pd.DataFrame({"총점": numeric_df.sum(), "평균점수": numeric_df.mean()})
        result_df["등수"] = result_df["평균점수"].rank(ascending=False, method="min").astype(int)
        st.write("### 📊 최종 결과", result_df.sort_values(by="평균점수", ascending=False))
    else:
        st.info("데이터가 없습니다.")

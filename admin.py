import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"

st.set_page_config(page_title="관리자 집계", layout="wide")
st.title("🔒 관리자 집계 페이지")

password = st.text_input("비밀번호 입력", type="password")
if password == "123":
    # 파일이 존재할 때만 삭제하도록 수정
    if st.button("🔄 데이터 초기화"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("데이터가 초기화되었습니다!")
            st.rerun()
        else:
            st.info("초기화할 데이터 파일이 없습니다.")
    
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            st.write("### 📋 상세 점수 현황", df)
            numeric_df = df.drop(columns=["심사위원"])
            result_df = pd.DataFrame({"총점": numeric_df.sum(), "평균점수": numeric_df.mean()})
            result_df["등수"] = result_df["평균점수"].rank(ascending=False, method="min").astype(int)
            st.write("### 📊 최종 결과", result_df.sort_values(by="평균점수", ascending=False))
        else:
            st.info("아직 제출된 점수가 없습니다.")
    else:
        st.info("아직 제출된 점수가 없습니다.")

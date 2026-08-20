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

tab1, tab2 = st.tabs(["심사위원용", "🔒 주최측 관리자"])

with tab1:
    st.subheader("심사위원 평가 페이지")
    
    # 심사위원을 사전에 지정하거나 고를 수 있게 설정
    judge_name = st.selectbox(
        "본인의 심사위원 성함을 선택해 주세요",
        ["심사위원 A", "심사위원 B", "심사위원 C", "심사위원 D", "심사위원 E", "심사위원 F", "심사위원 G"]
    )
    
    st.info(f"💡 현재 **{judge_name}**님으로 평가 중입니다. 새로고침하셔도 위 이름만 같으면 기존에 저장한 점수가 그대로 유지됩니다!")
    
    presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
    
    for p in presenters:
        with st.form(key=f"form_{p}"):
            st.subheader(f"발표자: {p}")
            
            # 파일 읽기 및 기존 점수 불러오기
            if not os.path.exists(DATA_FILE):
                pd.DataFrame(columns=["심사위원"] + presenters).to_csv(DATA_FILE, index=False)
            df = pd.read_csv(DATA_FILE)
            
            # 해당 심사위원의 기존 점수 찾기
            current_score = 5
            if judge_name in df["심사위원"].values:
                val = df.loc[df["심사위원"] == judge_name, p].values[0]
                if pd.notna(val): current_score = int(val)

            score = st.radio(f"{p} 점수", list(range(11)), index=int(current_score), horizontal=True, key=f"radio_{judge_name}_{p}")
            
            if st.form_submit_button(f"💾 '{p}' 저장"):
                if judge_name not in df["심사위원"].values:
                    new_row = pd.DataFrame([{"심사위원": judge_name}])
                    df = pd.concat([df, new_row], ignore_index=True)
                df.loc[df["심사위원"] == judge_name, p] = score
                df.to_csv(DATA_FILE, index=False)
                st.success(f"[{judge_name}] {p} 발표자 점수({score}점) 저장 완료!")

with tab2:
    if st.text_input("비밀번호", type="password") == ADMIN_PASSWORD:
        if st.button("🔄 데이터 초기화"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.rerun()
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            st.write("### 📋 상세 점수 현황", df)
            numeric_df = df.drop(columns=["심사위원"])
            result_df = pd.DataFrame({"총점": numeric_df.sum(), "평균점수": numeric_df.mean()}).round(2)
            result_df["등수"] = result_df["평균점수"].rank(ascending=False, method="min").astype(int)
            st.write("### 📊 최종 결과", result_df.sort_values(by="평균점수", ascending=False))
        else:
            st.info("아직 제출된 점수가 없습니다.")
    else:
        st.warning("비밀번호가 필요합니다.")

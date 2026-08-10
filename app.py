import pandas as pd
import streamlit as st
import os

ADMIN_PASSWORD = "123"
DATA_FILE = "submissions.csv"

# 데이터 파일 초기화 (없을 경우만 생성)
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["심사위원", "김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]).to_csv(DATA_FILE, index=False)

st.title("🏆 2026 남북한 사회통합사례 발표대회")

# 탭 구조
tab1, tab2 = st.tabs(["심사위원용", "주최측 관리자용"])

with tab1:
    st.subheader("심사위원님 환영합니다!")
    with st.form("score_form", clear_on_submit=True): # 제출 후 폼 초기화
        presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
        current_judge_scores = {p: st.slider(f"발표자: {p}", 0, 10, 5) for p in presenters}
        
        if st.form_submit_button("📤 최종 점수 제출하기"):
            df = pd.read_csv(DATA_FILE)
            new_entry = {"심사위원": f"심사위원 {len(df) + 1}번"}
            new_entry.update(current_judge_scores)
            
            # 새 데이터 추가
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("점수가 기록되었습니다!")

with tab2:
    st.subheader("🔒 주최측 관리자 전용")
    # 비밀번호 입력 확인
    password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if password == ADMIN_PASSWORD:
        if st.button("🔄 데이터 초기화"):
            pd.DataFrame(columns=["심사위원", "김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]).to_csv(DATA_FILE, index=False)
            st.rerun()
            
        # 점수 데이터 읽기 (제출 여부와 관계없이 파일 읽기)
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

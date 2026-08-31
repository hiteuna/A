import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"
ADMIN_PASSWORD = "123"

st.set_page_config(page_title="2026 발표대회 합격/불합격 심사", layout="centered")

st.markdown("""
    <style>
    h3 { font-size: 1.3rem !important; text-align: center; }
    div.stButton > button {
        width: 100%;
        font-size: 1.2rem !important;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🏆 2026 남북한 사회통합사례 발표대회 (합격/불합격 심사)")

query_params = st.query_params
judge_num = query_params.get("judge", None)

tab1, tab2 = st.tabs(["심사위원용", "🔒 주최측 관리자"])

with tab1:
    if not judge_num:
        st.warning("⚠️ 개인 심사 링크로 접속하지 않으셨습니다.\n심사위원분들은 문자로 받으신 전용 링크로 다시 접속해 주세요.")
    else:
        current_judge = f"심사위원 {judge_num}번"
        st.info(f"💡 안녕하세요! **{current_judge}**님용 평가 페이지입니다.\n- 발표자별로 **[ O (합격)]** 또는 **[ X (불합격)]**을 누르면 즉시 저장됩니다.\n- 모든 심사가 끝난 후 **[최종 심사 제출완료]** 버튼을 꼭 눌러주세요!")
        
        presenters = ["김수정", "김송금", "동혜경", "조영남", "이정규", "최화순", "전재현"]
        
        # 파일이 없거나 형식이 안 맞을 경우 대비한 초기화
        if not os.path.exists(DATA_FILE):
            init_dict = {"심사위원": [], "제출상태": []}
            for p in presenters:
                init_dict[p] = []
            pd.DataFrame(init_dict).to_csv(DATA_FILE, index=False)
        
        df = pd.read_csv(DATA_FILE)
        
        # "제출상태" 컬럼이 아예 없거나 타입 문제 방지를 위해 문자열로 강제 변환
        if "제출상태" not in df.columns:
            df["제출상태"] = ""
        df["제출상태"] = df["제출상태"].astype(str)
        for p in presenters:
            if p not in df.columns:
                df[p] = ""
            df[p] = df[p].astype(str)
            
        for p in presenters:
            st.markdown(f"---")
            st.subheader(f"📌 발표자: {p}")
            
            current_val = ""
            if current_judge in df["심사위원"].values:
                val = df.loc[df["심사위원"] == current_judge, p].values[0]
                if pd.notna(val): 
                    current_val = str(val)
            
            if current_val in ["O", "X"]:
                label_text = "합격(O)" if current_val == "O" else "불합격(X)"
                st.caption(f"현재 선택된 평가: **[{label_text}]**")
            else:
                st.caption("현재 미선택 상태")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"⭕ O (합격)", key=f"btn_O_{p}"):
                    if current_judge not in df["심사위원"].values:
                        new_row_data = {"심사위원": current_judge, "제출상태": ""}
                        for pres in presenters:
                            new_row_data[pres] = ""
                        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
                    
                    df.loc[df["심사위원"] == current_judge, p] = "O"
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"'{p}' -> 합격(O) 저장 완료!")
                    st.rerun()
                    
            with col2:
                if st.button(f"❌ X (불합격)", key=f"btn_X_{p}"):
                    if current_judge not in df["심사위원"].values:
                        new_row_data = {"심사위원": current_judge, "제출상태": ""}
                        for pres in presenters:
                            new_row_data[pres] = ""
                        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
                    
                    df.loc[df["심사위원"] == current_judge, p] = "X"
                    df.to_csv(DATA_FILE, index=False)
                    st.error(f"'{p}' -> 불합격(X) 저장 완료!")
                    st.rerun()

        # 하단 최종 제출 완료 버튼 영역
        st.markdown("---")
        st.markdown("### ✅ 모든 심사 완료 후 아래 버튼을 눌러주세요!")
        
        is_submitted = False
        if current_judge in df["심사위원"].values:
            status_val = df.loc[df["심사위원"] == current_judge, "제출상태"].values[0]
            if pd.notna(status_val) and status_val == "완료":
                is_submitted = True

        if is_submitted:
            st.success("🎉 **[제출완료]** 처리가 정상적으로 완료되었습니다! 수고하셨습니다.")
            if st.button("🔄 수정하기 (다시 평가하기)", key="btn_cancel_submit"):
                df.loc[df["심사위원"] == current_judge, "제출상태"] = ""
                df.to_csv(DATA_FILE, index=False)
                st.rerun()
        else:
            if st.button("🚀 최종 심사 제출완료", key="btn_final_submit"):
                if current_judge not in df["심사위원"].values:
                    new_row_data = {"심사위원": current_judge, "제출상태": "완료"}
                    for pres in presenters:
                        new_row_data[pres] = ""
                    df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
                else:
                    df.loc[df["심사위원"] == current_judge, "제출상태"] = "완료"
                df.to_csv(DATA_FILE, index=False)
                st.balloons()
                st.success("🎉 모든 심사가 최종 제출되었습니다. 감사합니다!")
                st.rerun()

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
                st.write("### 📋 심사위원별 상세 현황 및 제출 상태", df)
                
                score_df = df.drop(columns=[col for col in ["심사위원", "제출상태"] if col in df.columns])
                
                o_counts = (score_df == "O").sum()
                x_counts = (score_df == "X").sum()
                total_votes = o_counts + x_counts
                
                result_df = pd.DataFrame({
                    "합격(O) 개수": o_counts,
                    "불합격(X) 개수": x_counts,
                    "총 투표수": total_votes
                })
                result_df["순위"] = result_df["합격(O) 개수"].rank(ascending=False, method="min").astype(int)
                
                st.write("### 📊 발표자별 집계 결과", result_df.sort_values(by="합격(O) 개수", ascending=False))
            else:
                st.info("아직 제출된 심사 결과가 없습니다.")
        else:
            st.info("아직 제출된 심사 결과가 없습니다.")
    else:
        st.warning("관리자 비밀번호를 입력해 주세요.")

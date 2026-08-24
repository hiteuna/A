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
        st.info(f"💡 안녕하세요! **{current_judge}**님용 평가 페이지입니다.\n발표자별로 **[ O (합격)]** 또는 **[ X (불합격)]** 버튼을 누르시면 즉시 저장됩니다!")
        
        presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
        
        # 파일이 없으면 문자열을 담을 수 있는 데이터프레임으로 초기 생성
        if not os.path.exists(DATA_FILE):
            init_dict = {"심사위원": []}
            for p in presenters:
                init_dict[p] = []
            pd.DataFrame(init_dict).to_csv(DATA_FILE, index=False)
        
        df = pd.read_csv(DATA_FILE)
        
        for p in presenters:
            st.markdown(f"---")
            st.subheader(f"📌 발표자: {p}")
            
            current_val = ""
            if current_judge in df["심사위원"].values:
                val = df.loc[df["심사위원"] == current_judge, p].values[0]
                if pd.notna(val): 
                    current_val = str(val)
            
            if current_val:
                label_text = "합격(O)" if current_val == "O" else "불합격(X)"
                st.caption(f"현재 선택된 평가: **[{label_text}]**")
            else:
                st.caption("현재 미선택 상태")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"⭕ O (합격)", key=f"btn_O_{p}"):
                    if current_judge not in df["심사위원"].values:
                        new_row_data = {"심사위원": current_judge}
                        for pres in presenters:
                            new_row_data[pres] = ""
                        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
                    
                    # 해당 칸의 타입을 문자열로 강제 변환 후 저장
                    df[p] = df[p].astype(str)
                    df.loc[df["심사위원"] == current_judge, p] = "O"
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"'{p}' -> 합격(O) 저장 완료!")
                    st.rerun()
                    
            with col2:
                if st.button(f"❌ X (불합격)", key=f"btn_X_{p}"):
                    if current_judge not in df["심사위원"].values:
                        new_row_data = {"심사위원": current_judge}
                        for pres in presenters:
                            new_row_data[pres] = ""
                        df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
                    
                    # 해당 칸의 타입을 문자열로 강제 변환 후 저장
                    df[p] = df[p].astype(str)
                    df.loc[df["심사위원"] == current_judge, p] = "X"
                    df.to_csv(DATA_FILE, index=False)
                    st.error(f"'{p}' -> 불합격(X) 저장 완료!")
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
                st.write("### 📋 심사위원별 상세 현황", df)
                
                numeric_df = df.drop(columns=["심사위원"])
                o_counts = (numeric_df == "O").sum()
                x_counts = (numeric_df == "X").sum()
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

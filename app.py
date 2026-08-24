import pandas as pd
import streamlit as st
import os

DATA_FILE = "submissions.csv"
ADMIN_PASSWORD = "123"

st.set_page_config(page_title="2026 발표대회 O/X 심사", layout="centered")

# O와 X 버튼을 크고 시원하게 보이도록 CSS 스타일 적용
st.markdown("""
    <style>
    h3 { font-size: 1.3rem !important; text-align: center; }
    /* 버튼 스타일 강조 및 크기 조절 */
    div.stButton > button {
        width: 100%;
        font-size: 1.2rem !important;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 8px;
    }
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
        st.info(f"💡 안녕하세요! **{current_judge}**님용 평가 페이지입니다.\n발표자별로 **[ O ]** 또는 **[ X ]** 버튼을 누르시면 즉시 저장됩니다!")
        
        presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
        
        # 파일 읽기 준비
        if not os.path.exists(DATA_FILE):
            pd.DataFrame(columns=["심사위원"] + presenters).to_csv(DATA_FILE, index=False)
        
        df = pd.read_csv(DATA_FILE)
        
        for p in presenters:
            st.markdown(f"---")
            st.subheader(f"📌 발표자: {p}")
            
            # 현재 저장되어 있는 값 확인
            current_val = ""
            if current_judge in df["심사위원"].values:
                val = df.loc[df["심사위원"] == current_judge, p].values[0]
                if pd.notna(val): 
                    current_val = val
            
            if current_val:
                st.caption(f"현재 선택된 평가: **[{current_val}]**")
            else:
                st.caption("현재 미선택 상태")
            
            # O와 X를 나란히 배치하기 위해 열 나누기
            col1, col2 = st.columns(2)
            
            with col1:
                # O 버튼 (선택되어 있으면 파란색/강조 느낌을 위해 구분 가능)
                if st.button(f"⭕ O (찬성/적합)", key=f"btn_O_{p}"):
                    if current_judge not in df["심사위원"].values:
                        new_row = pd.DataFrame([{"심사위원": current_judge}])
                        df = pd.concat([df, new_row], ignore_index=True)
                    df.loc[df["심사위원"] == current_judge, p] = "O"
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"'{p}' -> O 저장 완료!")
                    st.rerun()
                    
            with col2:
                # X 버튼
                if st.button(f"❌ X (반대/부적합)", key=f"btn_X_{p}"):
                    if current_judge not in df["심사위원"].values:
                        new_row = pd.DataFrame([{"심사위원": current_judge}])
                        df = pd.concat([df, new_row], ignore_index=True)
                    df.loc[df["심사위원"] == current_judge, p] = "X"
                    df.to_csv(DATA_FILE, index=False)
                    st.error(f"'{p}' -> X 저장 완료!")
                    st.rerun()

with tab2:
    password = st.text_input("관리자 비밀번호", type="password")
    if password == ADMIN_PASSWORD:
        if st.button("🔄 데이터 초기화"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.success("데이터가 초기화되었습니다.")
            st.rerun()
            
        if os.path.exists(DATA_FILE):
            df = pr.read_csv(DATA_FILE) if 'pr' in globals() else pd.read_csv(DATA_FILE)
            if not df.empty:
                st.write("### 📋 심사위원별 상세 현황", df)
                
                numeric_df = df.drop(columns=["심사위원"])
                o_counts = (numeric_df == "O").sum()
                x_counts = (numeric_df == "X").sum()
                total_votes = o_counts + x_counts
                
                result_df = pd.DataFrame({
                    "O 개수": o_counts,
                    "X 개수": x_counts,
                    "총 투표수": total_votes
                })
                result_df["순위"] = result_df["O 개수"].rank(ascending=False, method="min").astype(int)
                
                st.write("### 📊 발표자별 O/X 집계 결과", result_df.sort_values(by="O 개수", ascending=False))
            else:
                st.info("아직 제출된 심사 결과가 없습니다.")
        else:
            st.info("아직 제출된 심사 결과가 없습니다.")
    else:
        st.warning("관리자 비밀번호를 입력해 주세요.")

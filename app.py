import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="2026 남북한 사회통합사례 발표대회", page_icon="🏆"
)

# 데이터 저장을 위한 세션 상태 초기화
if "submissions" not in st.session_state:
  st.session_state.submissions = []

st.title("🏆 2026 남북한 사회통합사례 발표대회 심사")
st.write(
    "심사위원님 환영합니다! 각 발표자의 점수를 매긴 후 제출해 주세요."
)

with st.form("score_form"):
  st.subheader("발표자별 점수 입력 (1 ~ 10점)")

  presenters = ["김송금", "김수정", "동혜경", "이정규", "전재현", "조영남", "최화순"]
  current_judge_scores = {}

  for presenter in presenters:
    current_judge_scores[presenter] = st.slider(
        f"발표자: {presenter}", 0, 10, 5
    )

  submitted = st.form_submit_button("📤 최종 점수 제출하기", type="primary")

  if submitted:
    st.session_state.submissions.append(current_judge_scores)
    st.success(
        "점수가 성공적으로 제출되었습니다! 창을 닫으셔도 됩니다."
    )

st.divider()

# --- [주최측용 실시간 집계 현황 및 초기화 버튼] ---
st.subheader("📊 [실시간] 현재 집계 현황 (주최측 전용)")

# 초기화 버튼 추가
if st.button("🔄 테스트 데이터 초기화 (처음부터 다시 시작)"):
  st.session_state.submissions = []
  st.rerun()

if len(st.session_state.submissions) > 0:
  df_all = pd.DataFrame(st.session_state.submissions)
  avg_scores = df_all.mean()
  total_scores = df_all.sum()

  result_df = pd.DataFrame({"총점": total_scores, "평균점수": avg_scores})
  result_df["등수"] = (
      result_df["평균점수"].rank(ascending=False, method="min").astype(int)
  )
  result_df = result_df.sort_values(by="평균점수", ascending=False)

  st.write(f"현재 총 제출된 심사지 수: **{len(df_all)}건**")
  st.dataframe(result_df, use_container_width=True)
else:
  st.info("아직 제출된 점수가 없습니다.")
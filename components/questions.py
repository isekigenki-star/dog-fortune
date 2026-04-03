import streamlit as st

CHOICE_COLORS = {
    "A": ("#FFE4E1", "#FF6B8A"),
    "B": ("#E1F0FF", "#5B9BD5"),
    "C": ("#E8FFE1", "#5BB55B"),
    "D": ("#FFF5E1", "#D4A017"),
}


def show_question(question: dict, data: dict) -> None:
    """1問分の選択肢を表示し、回答時にスコアを更新して次へ進む。"""
    q_id = question["id"]

    for choice in question["choices"]:
        label = choice["label"]
        text = choice["text"]
        bg, border = CHOICE_COLORS.get(label, ("#F5F5F5", "#999"))

        # ボタンのスタイルをラベルごとに切り替えるため、カスタムキーを使う
        btn_key = f"q{q_id}_{label}"

        # CSS injection でボタンの見た目を変える（キーで特定）
        st.markdown(
            f"""
            <style>
            div[data-testid="stButton"] > button[kind="secondary"]#btn_{btn_key} {{
                background-color: {bg};
                border: 2px solid {border};
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"　{label}）  {text}",
            key=btn_key,
            use_container_width=True,
        ):
            for breed, score in choice["scores"].items():
                st.session_state.scores[breed] += score
            st.session_state.current_q += 1
            total = len(data["questions"])
            if st.session_state.current_q >= total:
                st.session_state.page = "result"
            st.rerun()

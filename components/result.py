import streamlit as st
from typing import Callable
from components.dog_image import get_random_dog_image, build_hero_card_html


def show_result(scores: dict, breeds: dict, reset_func: Callable) -> None:
    """診断結果を表示する。"""
    # 最高スコアの犬種を取得（同点は辞書順で先頭 = 最初に登場した犬種）
    max_score = max(scores.values())
    result_breed = next(breed for breed, score in scores.items() if score == max_score)

    breed_data = breeds[result_breed]
    message = breed_data["message"]

    # 結果画像：初回のみ取得（キャッシュ優先）
    if st.session_state.get("result_image_url") is None:
        cache = st.session_state.get("breed_image_cache", {})
        cached_url = cache.get(result_breed)
        if cached_url:
            st.session_state["result_image_url"] = cached_url
        else:
            st.session_state["result_image_url"] = get_random_dog_image(result_breed) or ""

    result_image_url = st.session_state["result_image_url"]

    # 結果メッセージの最初の1文（句点まで）
    first_sentence = message.split("。")[0] + "。" if "。" in message else message

    # ヒーローカード
    st.markdown(build_hero_card_html(
        image_source=result_image_url,
        title=f"あなたは「{result_breed}」タイプです！",
        subtitle=first_sentence,
        badge="診断結果 🎉",
    ), unsafe_allow_html=True)

    # 結果メッセージ全文
    st.markdown(message)

    # スコア詳細（折りたたみ）
    with st.expander("全犬種のスコアを見る"):
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for breed, score in sorted_scores:
            b_data = breeds[breed]
            is_top = breed == result_breed
            bar_color = b_data["color"]
            label_style = "font-weight:700;" if is_top else ""
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; margin-bottom:8px; gap:10px;">
                    <span style="width:130px; font-size:14px; {label_style} color:#333;">
                        {b_data['emoji']} {breed}{"　✨" if is_top else ""}
                    </span>
                    <div style="flex:1; background:#F0F0F0; border-radius:8px; height:18px; overflow:hidden;">
                        <div style="
                            width:{min(score * 3, 100)}%;
                            background:{bar_color};
                            height:100%;
                            border-radius:8px;
                            transition: width 0.5s;
                        "></div>
                    </div>
                    <span style="font-size:13px; color:#666; width:30px; text-align:right;">{score}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if st.button("🔄　もう一度診断する", use_container_width=True):
        reset_func()
        st.rerun()

import json
import os
import random
import sys

import streamlit as st

# パス解決（components パッケージを確実に読み込む）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from components.questions import show_question
from components.result import show_result
from components.dog_image import get_random_dog_image, build_hero_card_html, BREED_MAP, prefetch_all_breed_images

# ─────────────────────────────────────────────
# ページ設定
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="犬種占い",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# グローバル CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #ffeef8 0%, #f0e6ff 100%);
    }

    .block-container {
        max-width: 720px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    .hero-card {
        position: relative;
        width: 100%;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        background-color: #1a1a2e;
    }

    .hero-card img {
        width: 100%;
        height: 420px;
        object-fit: contain;
        object-position: center;
        display: block;
        background-color: #1a1a2e;
    }

    .hero-card .hero-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 32px 28px 24px 28px;
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.75) 0%,
            rgba(0, 0, 0, 0.4) 60%,
            rgba(0, 0, 0, 0.0) 100%
        );
        color: white;
        box-sizing: border-box;
    }

    .hero-card .hero-title {
        font-size: 2rem;
        font-weight: bold;
        margin: 0 0 6px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        line-height: 1.3;
    }

    .hero-card .hero-subtitle {
        font-size: 1rem;
        margin: 0;
        opacity: 0.9;
        text-shadow: 0 1px 4px rgba(0,0,0,0.5);
    }

    .hero-card .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.25);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        margin-bottom: 10px;
        backdrop-filter: blur(4px);
    }

    /* ヨシキ専用ヒーローカード */
    .hero-card-yoshiki {
        position: relative;
        width: 100%;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        background-color: #1a1a2e;
    }

    .hero-card-yoshiki img {
        width: 100%;
        height: auto;          /* 縦長画像をそのまま表示 */
        max-height: 620px;     /* 長すぎる場合の上限 */
        object-fit: contain;
        object-position: center top; /* 上側（顔）を優先して表示 */
        display: block;
        background-color: #1a1a2e;
    }

    .hero-card-yoshiki .hero-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 32px 28px 24px 28px;
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.80) 0%,
            rgba(0, 0, 0, 0.45) 55%,
            rgba(0, 0, 0, 0.0) 100%
        );
        color: white;
        box-sizing: border-box;
    }

    .hero-card-yoshiki .hero-title {
        font-size: 2rem;
        font-weight: bold;
        margin: 0 0 6px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.7);
        line-height: 1.3;
    }

    .hero-card-yoshiki .hero-subtitle {
        font-size: 1rem;
        margin: 0;
        opacity: 0.92;
        text-shadow: 0 1px 4px rgba(0,0,0,0.6);
    }

    .hero-card-yoshiki .hero-badge {
        display: inline-block;
        background: rgba(255, 80, 80, 0.35);
        border: 1px solid rgba(255, 120, 120, 0.6);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        margin-bottom: 10px;
        backdrop-filter: blur(4px);
        color: white;
    }

    .stButton > button {
        background: linear-gradient(135deg, #ff6b9d, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 14px 40px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(168, 85, 247, 0.55) !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #ff6b9d, #a855f7) !important;
        border-radius: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# データ読み込み
# ─────────────────────────────────────────────
@st.cache_data
def load_data() -> dict:
    path = os.path.join(BASE_DIR, "data", "scoring.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_tennis_data() -> dict:
    path = os.path.join(BASE_DIR, "data", "tennis_scoring.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()
tennis_data = load_tennis_data()

ALL_BREEDS = list(BREED_MAP.keys())


def _get_tennis_breeds() -> list[str]:
    """tennis_scoring.json に登場する全犬種キーを返す（__YOSHIKI__ 含む）。"""
    breeds: set[str] = set()
    for q in tennis_data["questions"]:
        for c in q["choices"]:
            breeds.update(c["scores"].keys())
    return list(breeds)


# ─────────────────────────────────────────────
# セッション状態の初期化 / リセット
# ─────────────────────────────────────────────
def init_state() -> None:
    defaults = {
        "page": "start",
        "mode": None,
        "current_q": 0,
        "scores": {},
        "start_image_url": None,
        "quiz_image_urls": {},
        "result_image_url": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset() -> None:
    st.session_state.page = "start"
    st.session_state.mode = None
    st.session_state.current_q = 0
    st.session_state.scores = {}
    st.session_state.start_image_url = None
    st.session_state.quiz_image_urls = {}
    st.session_state.result_image_url = None


init_state()

# ─────────────────────────────────────────────
# スタート画面
# ─────────────────────────────────────────────
if st.session_state.page == "start":

    # 全犬種画像を一括プリフェッチ（初回のみ）
    if "breed_image_cache" not in st.session_state:
        with st.spinner("画像を読み込んでいます..."):
            st.session_state["breed_image_cache"] = prefetch_all_breed_images()

    # スタート画面用にキャッシュからランダム犬種の画像を1度だけ取得
    if st.session_state.start_image_url is None:
        cache = st.session_state["breed_image_cache"]
        breed = random.choice([b for b, url in cache.items() if url])
        st.session_state.start_image_url = cache.get(breed) or ""

    # ヒーローカード
    st.markdown(build_hero_card_html(
        image_source=st.session_state.start_image_url,
        title="🐾 あなたはどの犬種タイプ？",
        subtitle="10の質問に答えて、あなたにぴったりの犬種を診断します",
        badge="全10問・約2分",
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🐶 通常診断スタート", use_container_width=True):
            st.session_state.mode = "normal"
            st.session_state.scores = {breed: 0 for breed in data["breeds"]}
            st.session_state.page = "quiz"
            st.rerun()
    with col2:
        if st.button("🎾 テニス部専用診断", use_container_width=True):
            st.session_state.mode = "tennis"
            st.session_state.scores = {breed: 0 for breed in _get_tennis_breeds()}
            st.session_state.page = "quiz"
            st.rerun()

# ─────────────────────────────────────────────
# クイズ画面
# ─────────────────────────────────────────────
elif st.session_state.page == "quiz":
    mode = st.session_state.get("mode", "normal")
    active_data = tennis_data if mode == "tennis" else data
    total_q = len(active_data["questions"])

    current_idx = st.session_state.current_q

    # クイズ画像：質問ごとに1度だけ取得（キャッシュ優先）
    if current_idx not in st.session_state.quiz_image_urls:
        cache = st.session_state.get("breed_image_cache", {})
        if cache:
            breed = random.choice([b for b, url in cache.items() if url])
            st.session_state.quiz_image_urls[current_idx] = cache.get(breed) or ""
        else:
            breed = random.choice(ALL_BREEDS)
            st.session_state.quiz_image_urls[current_idx] = get_random_dog_image(breed) or ""

    quiz_img_url = st.session_state.quiz_image_urls[current_idx]
    question = active_data["questions"][current_idx]

    # ヒーローカード
    st.markdown(build_hero_card_html(
        image_source=quiz_img_url,
        title=question["text"],
        subtitle="",
        badge=f"Q{current_idx + 1} / {total_q}",
    ), unsafe_allow_html=True)

    # プログレスバー
    st.progress(current_idx / total_q)

    show_question(question, active_data)

# ─────────────────────────────────────────────
# 結果画面
# ─────────────────────────────────────────────
elif st.session_state.page == "result":
    mode = st.session_state.get("mode", "normal")
    scores = st.session_state.scores

    max_score = max(scores.values()) if scores else 0
    result_breed = next((b for b, s in scores.items() if s == max_score), None)

    # ─── ヨシキ判定 ───────────────────────────
    if mode == "tennis" and result_breed == "__YOSHIKI__":
        yoshiki_info = tennis_data.get("yoshiki", {})
        yoshiki_message = yoshiki_info.get("message", "")
        message_lines = yoshiki_message.split("\n")
        subtitle = message_lines[1] if len(message_lines) > 1 else yoshiki_message

        # 結果画像：初回のみ取得
        if st.session_state.get("result_image_url") is None:
            img = get_random_dog_image("__YOSHIKI__")
            if img is None:
                # yoshikiフォルダが空の場合はキャッシュからフォールバック
                cache = st.session_state.get("breed_image_cache", {})
                valid = [url for url in cache.values() if url]
                img = random.choice(valid) if valid else ""
            st.session_state["result_image_url"] = img or ""

        result_image = st.session_state["result_image_url"]

        st.markdown(build_hero_card_html(
            image_source=result_image,
            title="あなたは「ヨシキ」タイプです！",
            subtitle="バコルことに生きがいを感じており、ミックスダブルスを出禁になっています。🎾",
            badge="特別診断結果 🎾",
            card_class="hero-card-yoshiki",
        ), unsafe_allow_html=True)

        st.markdown(yoshiki_message)

        if st.button("🔄　もう一度診断する", use_container_width=True):
            reset()
            st.rerun()

    # ─── 通常結果（通常モード・テニス非ヨシキ）───
    else:
        # テニスモードの場合は __YOSHIKI__ をスコアから除外して show_result へ渡す
        display_scores = {k: v for k, v in scores.items() if k != "__YOSHIKI__"}
        show_result(display_scores, data["breeds"], reset)

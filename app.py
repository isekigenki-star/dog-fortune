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
from components.dog_image import (
    get_random_dog_image,
    build_hero_card_html,
    build_hero_card_no_image_html,
    BREED_MAP,
    prefetch_all_breed_images,
    _CAVALIER_IMAGES,
)

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
        height: 38vh;          /* 画面高さの38%に制限 */
        max-height: 320px;     /* PC表示の上限 */
        min-height: 160px;     /* 極端に小さくなる防止 */
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
        font-size: clamp(1.2rem, 4vw, 2rem); /* 画面幅に応じて自動調整 */
        font-weight: bold;
        margin: 0 0 4px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        line-height: 1.3;
    }

    .hero-card .hero-subtitle {
        font-size: clamp(0.8rem, 3vw, 1rem);
        margin: 0;
        opacity: 0.9;
        text-shadow: 0 1px 4px rgba(0,0,0,0.5);
    }

    .hero-card .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.25);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 20px;
        font-size: clamp(0.7rem, 2.5vw, 0.85rem);
        padding: 3px 10px;
        margin-bottom: 6px;
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
        height: 45vh;          /* 縦長画像なので少し大きめ */
        max-height: 420px;
        min-height: 200px;
        object-fit: contain;
        object-position: center top;
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
        font-size: clamp(1.2rem, 4vw, 2rem); /* 画面幅に応じて自動調整 */
        font-weight: bold;
        margin: 0 0 4px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.7);
        line-height: 1.3;
    }

    .hero-card-yoshiki .hero-subtitle {
        font-size: clamp(0.8rem, 3vw, 1rem);
        margin: 0;
        opacity: 0.92;
        text-shadow: 0 1px 4px rgba(0,0,0,0.6);
    }

    .hero-card-yoshiki .hero-badge {
        display: inline-block;
        background: rgba(255, 80, 80, 0.35);
        border: 1px solid rgba(255, 120, 120, 0.6);
        border-radius: 20px;
        font-size: clamp(0.7rem, 2.5vw, 0.85rem);
        padding: 3px 10px;
        margin-bottom: 6px;
        backdrop-filter: blur(4px);
        color: white;
    }

    .stButton > button {
        background: linear-gradient(135deg, #ff6b9d, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 10px 20px !important;
        font-size: clamp(0.85rem, 3vw, 1.1rem) !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4) !important;
        margin-top: 8px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(168, 85, 247, 0.55) !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #ff6b9d, #a855f7) !important;
        border-radius: 10px !important;
    }

    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .hero-card-no-image {
        position: relative;
        width: 100%;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        background: linear-gradient(135deg, #ff6b9d 0%, #a855f7 100%);
        min-height: 200px;
        display: flex;
        align-items: flex-end;
    }

    .hero-card-no-image .hero-overlay-static {
        width: 100%;
        padding: 32px 28px 24px 28px;
        color: white;
        box-sizing: border-box;
    }

    .hero-card-no-image .hero-title {
        font-size: clamp(1.2rem, 4vw, 2rem);
        font-weight: bold;
        margin: 0 0 6px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        line-height: 1.3;
        color: white;
    }

    .hero-card-no-image .hero-subtitle {
        font-size: clamp(0.8rem, 3vw, 1rem);
        margin: 0;
        opacity: 0.92;
        color: white;
    }

    .hero-card-no-image .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.25);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: clamp(0.7rem, 2.5vw, 0.85rem);
        margin-bottom: 10px;
        color: white;
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


@st.cache_data
def load_sushi_data() -> dict:
    path = os.path.join(BASE_DIR, "data", "sushi_scoring.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()
tennis_data = load_tennis_data()
sushi_data = load_sushi_data()

ALL_BREEDS = list(BREED_MAP.keys())

# ─────────────────────────────────────────────
# 寿司画像ヘルパー
# ─────────────────────────────────────────────
_SUSHI_DIR = os.path.join(BASE_DIR, "assets", "images", "sushi")
_SUSHI_IMAGES: list[str] = (
    [
        os.path.join(_SUSHI_DIR, f)
        for f in os.listdir(_SUSHI_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if os.path.isdir(_SUSHI_DIR)
    else []
)

_SUSHI_CHAIN_FILES: dict[str, str] = {
    "スシロー": "sushiro.jpg",
    "くら寿司": "kura.jpg",
    "はま寿司": "hama.jpg",
    "かっぱ寿司": "kappa.jpg",
}


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
        "page": "home",
        "mode": None,
        "current_q": 0,
        "scores": {},
        "start_image_url": None,
        "quiz_image_urls": {},
        "result_image_url": None,
        "home_image": None,
        # 寿司診断
        "sushi_q_index": 0,
        "sushi_scores": {},
        "sushi_quiz_images": {},
        "sushi_start_image": None,
        "sushi_result_image": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset() -> None:
    """犬種診断をリセットして start に戻る（もう一度診断する用）。"""
    st.session_state.page = "start"
    st.session_state.mode = None
    st.session_state.current_q = 0
    st.session_state.scores = {}
    st.session_state.start_image_url = None
    st.session_state.quiz_image_urls = {}
    st.session_state.result_image_url = None


def reset_to_home() -> None:
    """全状態をリセットしてホーム画面に戻る。"""
    st.session_state.page = "home"
    st.session_state.mode = None
    # 犬種診断関連
    st.session_state.current_q = 0
    st.session_state.scores = {}
    st.session_state.start_image_url = None
    st.session_state.quiz_image_urls = {}
    st.session_state.result_image_url = None
    # 回転寿司診断関連
    st.session_state.sushi_q_index = 0
    st.session_state.sushi_scores = {}
    st.session_state.sushi_quiz_images = {}
    st.session_state.sushi_start_image = None
    st.session_state.sushi_result_image = None
    for key in ("answers", "q_index", "quiz_images",
                "sushi_answers", "sushi_start_image_url", "sushi_result_image_url"):
        st.session_state.pop(key, None)


def _back_to_home_button() -> None:
    """「← 診断メニューに戻る」ボタンを各ページ最下部に表示する。"""
    st.markdown("---")
    if st.button("← 診断メニューに戻る", use_container_width=True):
        reset_to_home()
        st.rerun()


init_state()

# ─────────────────────────────────────────────
# ホーム画面
# ─────────────────────────────────────────────
if st.session_state.page == "home":

    # 背景画像: sushi または cavalier からランダムに1枚（初回のみ選択）
    if st.session_state.home_image is None:
        all_bg = _CAVALIER_IMAGES + _SUSHI_IMAGES
        st.session_state.home_image = random.choice(all_bg) if all_bg else ""

    if st.session_state.home_image:
        st.markdown(build_hero_card_html(
            image_source=st.session_state.home_image,
            title="🎯 あなたはどのタイプ？",
            subtitle="診断したい項目を選んでください",
            badge="診断メニュー",
        ), unsafe_allow_html=True)
    else:
        st.markdown("## 🎯 あなたはどのタイプ？")
        st.markdown("診断したい項目を選んでください")

    if st.button("🐶 犬種診断（通常）", use_container_width=True):
        st.session_state.mode = "normal"
        st.session_state.page = "start"
        st.rerun()

    if st.button("🎾 犬種診断（テニス部専用）", use_container_width=True):
        st.session_state.mode = "tennis"
        st.session_state.page = "start"
        st.rerun()

    if st.button("🍣 回転寿司チェーン診断", use_container_width=True):
        st.session_state.mode = "sushi"
        st.session_state.page = "sushi_start"
        st.rerun()

# ─────────────────────────────────────────────
# スタート画面（犬種診断）
# ─────────────────────────────────────────────
elif st.session_state.page == "start":

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

    _back_to_home_button()

# ─────────────────────────────────────────────
# クイズ画面（犬種診断）
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

    _back_to_home_button()

# ─────────────────────────────────────────────
# 結果画面（犬種診断）
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

    _back_to_home_button()

# ─────────────────────────────────────────────
# 回転寿司診断: スタート画面
# ─────────────────────────────────────────────
elif st.session_state.page == "sushi_start":

    if st.session_state.sushi_start_image is None:
        st.session_state.sushi_start_image = random.choice(_SUSHI_IMAGES) if _SUSHI_IMAGES else ""

    if st.session_state.sushi_start_image:
        st.markdown(build_hero_card_html(
            image_source=st.session_state.sushi_start_image,
            title="回転寿司チェーン診断",
            subtitle="9つの質問に答えて、あなたにぴったりの回転寿司チェーンを診断します",
            badge="全9問・約2分",
        ), unsafe_allow_html=True)
    else:
        st.markdown(build_hero_card_no_image_html(
            title="回転寿司チェーン診断",
            subtitle="9つの質問に答えて、あなたにぴったりの回転寿司チェーンを診断します",
            badge="全9問・約2分",
        ), unsafe_allow_html=True)

    if st.button("診断スタート！", use_container_width=True):
        st.session_state.page = "sushi_quiz"
        st.session_state.sushi_answers = {}
        st.session_state.sushi_q_index = 0
        st.session_state.sushi_scores = {chain: 0 for chain in sushi_data["results"]}
        st.rerun()

    _back_to_home_button()

# ─────────────────────────────────────────────
# 回転寿司診断: クイズ画面
# ─────────────────────────────────────────────
elif st.session_state.page == "sushi_quiz":
    questions = sushi_data["questions"]
    total_q = len(questions)
    current_idx = st.session_state.sushi_q_index

    # 画像：質問ごとに固定（セッション内）
    if current_idx not in st.session_state.sushi_quiz_images:
        img = random.choice(_SUSHI_IMAGES) if _SUSHI_IMAGES else ""
        st.session_state.sushi_quiz_images[current_idx] = img

    quiz_img = st.session_state.sushi_quiz_images[current_idx]
    question = questions[current_idx]

    if quiz_img:
        st.markdown(build_hero_card_html(
            image_source=quiz_img,
            title=question["question"],
            subtitle="",
            badge=f"Q{current_idx + 1} / {total_q}",
        ), unsafe_allow_html=True)
    else:
        st.markdown(build_hero_card_no_image_html(
            title=question["question"],
            badge=f"Q{current_idx + 1} / {total_q}",
        ), unsafe_allow_html=True)

    st.progress(current_idx / total_q)

    for choice in question["choices"]:
        btn_label = f"　{choice['label']}）  {choice['text']}"
        if st.button(btn_label, key=f"sushi_q{current_idx}_{choice['label']}", use_container_width=True):
            if "sushi_scores" not in st.session_state or not st.session_state.sushi_scores:
                st.session_state.sushi_scores = {chain: 0 for chain in sushi_data["results"]}
            for chain, score in choice["scores"].items():
                st.session_state.sushi_scores[chain] = st.session_state.sushi_scores.get(chain, 0) + score
            st.session_state.sushi_q_index += 1
            if st.session_state.sushi_q_index >= total_q:
                st.session_state.page = "sushi_result"
            st.rerun()

    _back_to_home_button()

# ─────────────────────────────────────────────
# 回転寿司診断: 結果画面
# ─────────────────────────────────────────────
elif st.session_state.page == "sushi_result":
    scores = st.session_state.get("sushi_scores", {})
    results = sushi_data["results"]

    max_score = max(scores.values()) if scores else 0
    result_chain = next((c for c, s in scores.items() if s == max_score), None)

    if result_chain and result_chain in results:
        chain_info = results[result_chain]

        # 結果画像（初回のみ決定）
        if st.session_state.sushi_result_image is None:
            chain_file = _SUSHI_CHAIN_FILES.get(result_chain)
            chain_img_path = os.path.join(_SUSHI_DIR, chain_file) if chain_file else None
            if chain_img_path and os.path.isfile(chain_img_path):
                st.session_state.sushi_result_image = chain_img_path
            elif _SUSHI_IMAGES:
                st.session_state.sushi_result_image = random.choice(_SUSHI_IMAGES)
            else:
                st.session_state.sushi_result_image = ""

        result_img = st.session_state.sushi_result_image
        message = chain_info["message"]
        message_lines = [line for line in message.split("\n") if line.strip()]
        subtitle = message_lines[1] if len(message_lines) > 1 else message_lines[0]
        title = f"あなたは「{result_chain}」タイプです！"

        if result_img:
            st.markdown(build_hero_card_html(
                image_source=result_img,
                title=title,
                subtitle=subtitle,
                badge="診断結果",
            ), unsafe_allow_html=True)
        else:
            st.markdown(build_hero_card_no_image_html(
                title=title,
                subtitle=subtitle,
                badge="診断結果",
            ), unsafe_allow_html=True)

        st.markdown(message)

        with st.expander("全チェーンのスコアを見る"):
            for chain, score in sorted(scores.items(), key=lambda x: -x[1]):
                chain_emoji = results.get(chain, {}).get("emoji", "")
                st.write(f"{chain_emoji} {chain}: {score}点")

        if st.button("🔄 もう一度診断する", use_container_width=True):
            st.session_state.sushi_q_index = 0
            st.session_state.sushi_scores = {}
            st.session_state.sushi_quiz_images = {}
            st.session_state.sushi_start_image = None
            st.session_state.sushi_result_image = None
            st.session_state.pop("sushi_answers", None)
            st.session_state.page = "sushi_start"
            st.rerun()

    _back_to_home_button()

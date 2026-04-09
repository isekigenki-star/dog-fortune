import base64
import io
import os
import random

import requests

# 犬種名 → (breed, sub_breed or None)
BREED_MAP: dict[str, tuple[str, str | None]] = {
    "柴犬": ("shiba", None),
    "ゴールデンレトリバー": ("retriever", "golden"),
    "トイプードル": ("poodle", "toy"),
    "フレンチブルドッグ": ("bulldog", "french"),
    "ボーダーコリー": ("collie", "border"),
    "ハスキー": ("husky", None),
    "ダックスフント": ("dachshund", None),
    "ラブラドール": ("labrador", None),
    "キャバリエ": ("spaniel", "blenheim"),
    "パグ": ("pug", None),
}

_BASE = "https://dog.ceo/api/breed"
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "cavalier")
_CAVALIER_IMAGES = [
    os.path.join(_ASSETS_DIR, f)
    for f in os.listdir(_ASSETS_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
] if os.path.isdir(_ASSETS_DIR) else []

YOSHIKI_IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "yoshiki")
_YOSHIKI_IMAGES = [
    os.path.join(YOSHIKI_IMAGE_DIR, f)
    for f in os.listdir(YOSHIKI_IMAGE_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
] if os.path.isdir(YOSHIKI_IMAGE_DIR) else []


def _build_url(breed: str, sub: str | None, suffix: str) -> str:
    if sub:
        return f"{_BASE}/{breed}/{sub}/{suffix}"
    return f"{_BASE}/{breed}/{suffix}"


def build_hero_card_html(
    image_source: str,
    title: str,
    subtitle: str = "",
    badge: str = "",
    card_class: str = "hero-card",
) -> str:
    """ヒーローカードのHTMLを生成して返す。エラー時は空文字列を返す。"""
    try:
        if image_source.startswith("http"):
            image_src = image_source
        else:
            from PIL import Image
            img = Image.open(image_source)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            encoded = base64.b64encode(buf.getvalue()).decode()
            image_src = f"data:image/jpeg;base64,{encoded}"

        badge_html = f'<span class="hero-badge">{badge}</span>' if badge else ""
        subtitle_html = f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ""

        return f"""<div class="{card_class}">
  <img src="{image_src}" alt="{title}">
  <div class="hero-overlay">
    {badge_html}
    <p class="hero-title">{title}</p>
    {subtitle_html}
  </div>
</div>"""
    except Exception:
        return ""


def build_hero_card_no_image_html(title: str, subtitle: str = "", badge: str = "") -> str:
    """画像なしバージョンのヒーローカードを生成して返す。背景はグラデーションのみ。"""
    badge_html = f'<span class="hero-badge">{badge}</span>' if badge else ""
    subtitle_html = f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""<div class="hero-card-no-image">
  <div class="hero-overlay-static">
    {badge_html}
    <p class="hero-title">{title}</p>
    {subtitle_html}
  </div>
</div>"""


def get_random_dog_image(breed_key: str) -> str | None:
    """breed_key（日本語犬種名）に対応するランダム画像URL1枚を返す。失敗時はNone。"""
    if breed_key == "__YOSHIKI__":
        return random.choice(_YOSHIKI_IMAGES) if _YOSHIKI_IMAGES else None

    entry = BREED_MAP.get(breed_key)
    if entry is None:
        return None
    breed, sub = entry
    url = _build_url(breed, sub, "images/random")
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            return data["message"]
    except Exception:
        pass
    return None


def prefetch_all_breed_images() -> dict:
    """全犬種の画像URLをまとめて取得して返す。キャバリエはローカルパスを使用。"""
    result = {}
    for breed_key in BREED_MAP:
        try:
            if breed_key == "キャバリエ":
                result[breed_key] = random.choice(_CAVALIER_IMAGES) if _CAVALIER_IMAGES else None
            else:
                result[breed_key] = get_random_dog_image(breed_key)
        except Exception:
            result[breed_key] = None
    return result


def get_multiple_dog_images(breed_key: str, count: int = 10) -> list[str]:
    """breed_keyに対応する画像URLをcount枚分リストで返す。失敗時は空リスト。"""
    entry = BREED_MAP.get(breed_key)
    if entry is None:
        return []
    breed, sub = entry
    url = _build_url(breed, sub, f"images/random/{count}")
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            msgs = data["message"]
            return msgs if isinstance(msgs, list) else [msgs]
    except Exception:
        pass
    return []

"""
🎨 Nanban Image Studio — free AI image creation from text prompts.

Two free tiers, zero config to start:

  1. Best quality (if you have a hosted image key, e.g. NVIDIA build.nvidia.com):
     calls the provider's OpenAI-compatible /images/generations endpoint
     (FLUX 1.1 Pro / Stable Diffusion 3.5 Large). Same key you already paste for chat.

  2. Free & keyless (default fallback): Pollinations FLUX — no key, no signup,
     works straight away. Laptop stays light (runs in the cloud, not your GPU).

So choosing "Auto" just works: with a key you get the best model, without one you
still get a good free image. Nothing to install, no GPU needed.
"""

import base64
import time
import urllib.parse
from pathlib import Path

import config

# where generated images are saved
OUT_DIR = config.BASE_DIR / "data" / "images"

# aspect-ratio presets  (label -> WxH)
SIZES = {
    "⬛ Square 1:1": (1024, 1024),
    "📱 Portrait 2:3": (1024, 1536),
    "🖼️ Landscape 3:2": (1536, 1024),
    "🎞️ Wide 16:9": (1344, 768),
}

# NVIDIA image models (OpenAI-compatible /images/generations on integrate.api.nvidia.com)
_NV_MODELS = {
    "flux": "black-forest-labs/flux.1-dev",
    "flux-pro": "black-forest-labs/flux-1.1-pro",
    "sd35": "stabilityai/stable-diffusion-3.5-large",
}


def _out_path(ext: str = "jpg") -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR / f"nanban-{int(time.time()*1000)}.{ext}"


def _has_image_key() -> bool:
    """A hosted key is set AND the provider base looks like it can do images (NVIDIA)."""
    base = (getattr(config, "HOSTED_BASE_URL", "") or "").lower()
    return bool(getattr(config, "HOSTED_API_KEY", "")) and "nvidia" in base


# ----------------------------------------------------------------- engines

def _nvidia(prompt: str, w: int, h: int, model_key: str) -> Path:
    """Best-quality tier: FLUX / SD 3.5 via the hosted OpenAI-compatible image endpoint."""
    import llm
    client = llm._openai_client()
    model = _NV_MODELS.get(model_key, _NV_MODELS["flux"])
    # NVIDIA accepts a few fixed sizes; snap to the nearest allowed WxH string
    size = f"{w}x{h}"
    r = client.images.generate(model=model, prompt=prompt, n=1,
                               size=size, response_format="b64_json")
    item = r.data[0]
    p = _out_path("png")
    if getattr(item, "b64_json", None):
        p.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        import requests
        p.write_bytes(requests.get(item.url, timeout=60).content)
    else:
        raise RuntimeError("provider returned no image")
    return p


def _pollinations(prompt: str, w: int, h: int) -> Path:
    """Free keyless tier: Pollinations FLUX. Returns a JPEG."""
    import random
    import requests
    q = urllib.parse.quote(prompt, safe="")
    url = (f"https://image.pollinations.ai/prompt/{q}"
           f"?width={w}&height={h}&model=flux&nologo=true&seed={random.randint(1, 10**9)}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    p = _out_path("jpg")
    p.write_bytes(r.content)
    return p


# ----------------------------------------------------------------- public

def engines() -> list[str]:
    """Engine choices for the UI (Auto first)."""
    opts = ["✨ Auto — best available"]
    if _has_image_key():
        opts += ["🏆 FLUX 1.1 Pro (key)", "🎨 FLUX.1-dev (key)", "🖌️ Stable Diffusion 3.5 (key)"]
    opts += ["🆓 Pollinations FLUX (free, no key)"]
    return opts


def generate(prompt: str, size_label: str = "⬛ Square 1:1",
             engine: str = "✨ Auto — best available") -> tuple[str, str]:
    """
    Make an image. Returns (file_path, status_message). file_path is "" on failure.
    Never raises — if the best engine fails it silently falls back to the free one.
    """
    prompt = (prompt or "").strip()
    if not prompt:
        return "", "✍️ Type what you want to see first."
    w, h = SIZES.get(size_label, (1024, 1024))

    want_key = "key" in engine
    want_free = "Pollinations" in engine or "free" in engine
    model_key = ("flux-pro" if "1.1 Pro" in engine
                 else "sd35" if "Stable Diffusion" in engine else "flux")

    # explicit free pick, or no key available → go straight to Pollinations
    if want_free or (engine.startswith("✨") and not _has_image_key()):
        try:
            p = _pollinations(prompt, w, h)
            return str(p), "🆓 Made with Pollinations FLUX (free)."
        except Exception as e:
            return "", f"Couldn't reach the free image service ({e}). Check your internet and try again."

    # key tier (explicit, or Auto with a key)
    try:
        p = _nvidia(prompt, w, h, model_key)
        nice = {"flux-pro": "FLUX 1.1 Pro", "sd35": "Stable Diffusion 3.5", "flux": "FLUX.1-dev"}[model_key]
        return str(p), f"🏆 Made with {nice} (your hosted key)."
    except Exception as e:
        if want_key:   # user forced the key engine → still try free so they get an image
            try:
                p = _pollinations(prompt, w, h)
                return str(p), f"🏆 key engine failed ({e}); 🆓 fell back to free Pollinations FLUX."
            except Exception as e2:
                return "", f"Both image engines failed ({e2})."
        # Auto → quiet fallback
        try:
            p = _pollinations(prompt, w, h)
            return str(p), "🆓 Made with Pollinations FLUX (free)."
        except Exception as e2:
            return "", f"Couldn't make the image ({e2})."

"""
Look and feel of the Nanban web app: one theme + one stylesheet, shared by app.py and server.py.
A warm, modern, Claude-style interface — centered reading column, flat assistant text,
a soft card for your own messages, and a big rounded composer. Works the same on laptop,
iPad and phone, in light and dark mode.
"""

import gradio as gr
from gradio.themes.utils import colors, fonts, sizes

# Warm "clay" accent (Nanban's own identity — a terracotta/coral, not a blue).
CLAY = colors.Color(
    name="clay", c50="#fbf4f0", c100="#f6e7dd", c200="#ecc9b4", c300="#e0a888", c400="#d4875f",
    c500="#c56a44", c600="#b0563a", c700="#8f4531", c800="#6f372a", c900="#582d24", c950="#331812",
)


def theme() -> gr.themes.Base:
    return gr.themes.Base(
        primary_hue=CLAY, secondary_hue=CLAY, neutral_hue=colors.stone,
        text_size=sizes.text_md, spacing_size=sizes.spacing_md, radius_size=sizes.radius_lg,
        font=[fonts.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        font_mono=[fonts.GoogleFont("JetBrains Mono"), "Consolas", "ui-monospace", "monospace"],
    ).set(
        # warm paper (light) / warm charcoal (dark)
        body_background_fill="#f7f4ef", body_background_fill_dark="#201e1b",
        block_background_fill="#ffffff", block_background_fill_dark="#2a2724",
        block_border_color="#eadfd3", block_border_color_dark="#3a352f",
        block_shadow="none", block_shadow_dark="none",
        block_label_background_fill="transparent", block_label_background_fill_dark="transparent",
        block_title_text_weight="600",
        input_background_fill="#ffffff", input_background_fill_dark="#2f2b27",
        input_border_color="#e7dccf", input_border_color_dark="#423c35",
        input_border_color_focus="#c56a44", input_border_color_focus_dark="#d4875f",
        input_shadow_focus="0 0 0 3px rgba(197,106,68,.16)", input_shadow_focus_dark="0 0 0 3px rgba(212,135,95,.22)",
        button_primary_background_fill="#c56a44", button_primary_background_fill_hover="#b0563a",
        button_primary_background_fill_dark="#c56a44", button_primary_background_fill_hover_dark="#d4875f",
        button_primary_text_color="#ffffff",
        button_secondary_background_fill="#f3e9df", button_secondary_background_fill_hover="#ecddcf",
        button_secondary_background_fill_dark="#352f2a", button_secondary_background_fill_hover_dark="#423a33",
        button_secondary_text_color="#8f4531", button_secondary_text_color_dark="#e0a888",
        button_secondary_border_color="transparent", button_secondary_border_color_dark="transparent",
        border_color_primary="#eadfd3", border_color_primary_dark="#3a352f",
        color_accent_soft="#f6ece2", color_accent_soft_dark="#352f2a",
        checkbox_background_color_selected="#c56a44", checkbox_background_color_selected_dark="#c56a44",
        slider_color="#c56a44",
    )


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap');

/* ===== base ===== */
:root {
  --nb-gutter: 16px; --nb-radius: 16px;
  --nb-accent: #c56a44; --nb-accent-hover: #b0563a;
  --nb-col: 780px;                 /* centered reading column width */
  --nb-user-bg: #f0e4d7;           /* soft card for the user's own message (light) */
  --nb-serif: 'Instrument Serif', Georgia, 'Times New Roman', serif;
}
.dark { --nb-user-bg: #37312b; }
footer, .built-with, a[href*="gradio.app"] { display: none !important; }
gradio-app, .gradio-container { max-width: 100% !important; }
body, .gradio-container { -webkit-font-smoothing: antialiased; }
.block.padded:has(#mode-info), .block:has(#topbar), .block:has(#brand), .block.padded:has(#status) { padding: 0 !important; }
.prose:has(#topbar), .prose:has(#brand) { margin: 0 !important; }
.column { gap: 10px !important; }

/* ===== sidebar ===== */
.sidebar-parent .sidebar { border-right: 1px solid var(--border-color-primary); background: var(--block-background-fill); }
.sidebar .sidebar-content { min-height: 100dvh; padding: 16px 14px calc(14px + env(safe-area-inset-bottom)) !important; display: flex; flex-direction: column; }
.sidebar .sidebar-content > .column { flex: 1; gap: 6px !important; }
.sidebar .toggle-button { top: 14px !important; width: 34px; height: 34px; border-radius: 10px !important; border: 1px solid var(--border-color-primary) !important; background: var(--block-background-fill) !important; box-shadow: none !important; }
#brand { display: flex; align-items: center; gap: 10px; padding: 0 2px 10px; }
#brand img { width: 38px; height: 38px; border-radius: 11px; }
#brand .name { font-weight: 700; font-size: 17px; letter-spacing: -.01em; line-height: 1.2; }
#brand .sub { font-size: 12px; color: var(--body-text-color-subdued); margin-top: 2px; }
#new-chat { width: 100%; height: 42px; justify-content: center; font-weight: 600; font-size: 14px; margin: 0 0 8px; border-radius: 12px !important; }
.sidebar .gr-accordion { border: none !important; background: transparent !important; padding: 0 !important; }
.sidebar .gr-accordion > .label-wrap { width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 9px 10px !important; border-radius: 10px; font-weight: 600; font-size: 14px; }
.sidebar .gr-accordion > .label-wrap:hover { background: var(--color-accent-soft); }
.sidebar .gr-accordion > .label-wrap .icon { font-size: 9px; opacity: .55; }
.sidebar .gr-accordion [data-testid="accordion-content"] { padding: 2px 10px 8px; }
.sidebar .gr-accordion [data-testid="accordion-content"] .block { border: none !important; background: transparent !important; padding: 0 !important; }
.sidebar .gr-accordion .prose { font-size: 13px; }
#status { margin-top: auto; padding: 12px 10px 0; border-top: 1px solid var(--border-color-primary); font-size: 12.5px; line-height: 1.7; color: var(--body-text-color-subdued); }
#status p { margin: 0; }
#status code { font-size: 11px; padding: 1px 5px; }

/* ===== top bar ===== */
#topbar { display: flex; align-items: center; justify-content: space-between; min-height: 44px; padding: 6px 0 2px; }
#topbar .title { font-weight: 700; font-size: 16px; display: none; }
#topbar .badges { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; margin-left: auto; }
.badge { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; padding: 5px 10px; border-radius: 999px; background: var(--color-accent-soft); color: var(--body-text-color); white-space: nowrap; line-height: 1; }
.badge.ok { background: #e7f3ea; color: #2f6b45; }
.badge.warn { background: #fbefdc; color: #8a5a00; }
.dark .badge.ok { background: #22311f; color: #86cfa0; }
.dark .badge.warn { background: #3a2c0a; color: #f0c060; }

/* ===== tabs ===== */
.tabs { gap: 0 !important; }
.tabs .tab-wrapper { border: none !important; margin: 2px 0 10px !important; padding: 0 !important; }
.tabs .tab-container { gap: 4px; border: none !important; }
.tabs [role="tab"] { border: none !important; border-radius: 999px !important; padding: 8px 15px !important; margin: 0 !important; font-weight: 600; font-size: 14px; color: var(--body-text-color-subdued) !important; background: transparent !important; }
.tabs [role="tab"]::after, .tabs [role="tab"]::before, .tabs .tab-container::after, .tabs .tab-container::before { display: none !important; }
.tabs [role="tab"].selected { background: var(--color-accent-soft) !important; color: var(--button-secondary-text-color) !important; }
.tabitem { padding: 0 !important; border: none !important; }
.tabitem > .column { gap: 12px !important; }

/* ===== reading column (chat) — left-aligned so it lines up with the tabs ===== */
#chat-col { max-width: 820px; width: 100%; margin: 0; gap: 12px !important; }

/* ===== mode pills ===== */
#modes { padding: 0 !important; border: none !important; background: transparent !important; }
#modes .wrap { display: flex !important; flex-wrap: nowrap !important; gap: 8px !important; overflow-x: auto; padding: 2px 2px 4px; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
#modes .wrap::-webkit-scrollbar { display: none; }
#modes label { display: inline-flex; align-items: center; height: 36px; border-radius: 999px !important; padding: 0 15px !important; border: 1px solid var(--border-color-primary) !important; background: var(--block-background-fill) !important; font-weight: 600; font-size: 13.5px; white-space: nowrap; cursor: pointer; transition: all .16s ease; box-shadow: none !important; }
#modes label:hover { border-color: var(--nb-accent) !important; transform: translateY(-1px); }
#modes label.selected { background: var(--nb-accent) !important; border-color: var(--nb-accent) !important; color: #fff !important; box-shadow: 0 4px 12px rgba(197,106,68,.26) !important; }
#modes input[type="radio"] { display: none !important; }
#mode-info { margin: -4px 0 0 2px !important; }
#mode-info, #mode-info p { font-size: 13px; color: var(--body-text-color-subdued); font-style: normal; line-height: 1.5; }
#allow-actions { padding: 10px 12px; border: 1px dashed var(--border-color-primary); border-radius: 10px; }
#allow-actions label { font-size: 13px; }

/* ===== chat: flat, document-like (Claude style) ===== */
#chat { border: none !important; background: transparent !important; min-height: 320px; }
#chat .message-wrap { padding: 6px 0 !important; gap: 14px; }
#chat .message-row { max-width: 100% !important; }
/* assistant = flat prose, no bubble */
#chat .bot, #chat .bot.message { background: transparent !important; border: none !important; box-shadow: none !important; padding: 2px 2px !important; font-size: 16px; line-height: 1.65; border-radius: 0 !important; }
/* user = soft warm card, right aligned */
#chat .user, #chat .user.message { background: var(--nb-user-bg) !important; color: var(--body-text-color) !important; border: none !important; border-radius: 16px !important; padding: 11px 15px !important; font-size: 15.5px; line-height: 1.55; }
#chat .user *, #chat .user.message * { color: var(--body-text-color) !important; }
#chat .avatar-container { display: none !important; }
#chat .message-row.bot-row { justify-content: flex-start; }
#chat .message-row.user-row { justify-content: flex-end; }
#chat .bot pre, #chat .bot code { font-size: 13.5px; }
#chat .bot pre { border-radius: 12px !important; }
#chat .icon-button-wrapper.top-panel, #chat > .top-panel { display: none !important; }
#chat .icon-button-wrapper { background: transparent !important; border: none !important; }

/* greeting / empty state */
#chat .placeholder-content { opacity: 1; text-align: center; max-width: 480px; margin: 12vh auto 0; }
#chat .placeholder-content h3 { font-family: var(--nb-serif); font-weight: 400; font-size: 38px; line-height: 1.1; letter-spacing: .01em; margin-bottom: 10px; color: var(--body-text-color); }
#chat .placeholder-content p { font-size: 15px; color: var(--body-text-color-subdued); }

/* ===== composer ===== */
#composer { position: sticky; bottom: 0; z-index: 5; padding: 8px 0 calc(8px + env(safe-area-inset-bottom)); background: linear-gradient(to bottom, transparent, var(--body-background-fill) 22%); gap: 10px !important; }
#composer .block { border-radius: 26px !important; border: 1px solid var(--border-color-primary) !important; background: var(--block-background-fill) !important; padding: 5px 7px 5px 12px !important; box-shadow: 0 2px 14px rgba(60,40,24,.07) !important; }
.dark #composer .block { box-shadow: 0 2px 14px rgba(0,0,0,.28) !important; }
#composer .input-container { display: flex; align-items: center; gap: 6px; }
#composer textarea { font-size: 16px !important; border: none !important; background: transparent !important; box-shadow: none !important; padding: 11px 8px !important; }
#composer .submit-button, #composer .stop-button { width: 38px !important; height: 38px !important; min-width: 38px; margin: 0 !important; border-radius: 50% !important; display: flex; align-items: center; justify-content: center; border: none !important; }
#composer .submit-button { background: var(--nb-accent) !important; color: #fff !important; }
#composer .submit-button:hover { background: var(--nb-accent-hover) !important; }
#composer .submit-button svg { width: 18px; height: 18px; }
#composer .stop-button { background: #efe7dd !important; color: #6f372a !important; }
.dark #composer .stop-button { background: #423a33 !important; color: #e0a888 !important; }
#examples, #examples > div, #examples .gallery, #examples .block, .block:has(#examples), .block:has(.gallery-item), #composer .block:has(.gallery) { padding: 0 !important; border: none !important; background: transparent !important; box-shadow: none !important; }
#examples .label { display: none !important; }
#examples .gallery { display: flex !important; flex-wrap: nowrap !important; overflow-x: auto; gap: 8px; scrollbar-width: none; padding: 0 2px 4px; justify-content: center; }
#examples .gallery::-webkit-scrollbar { display: none; }
#examples .gallery-item, #examples button { flex: 0 0 auto; width: auto !important; max-width: none !important; height: 34px; border-radius: 999px !important; border: 1px solid var(--border-color-primary) !important; background: var(--block-background-fill) !important; color: var(--body-text-color-subdued) !important; font-size: 13px !important; padding: 0 14px !important; white-space: nowrap; }
#examples button:hover { border-color: var(--nb-accent) !important; color: var(--body-text-color) !important; }

/* ===== terminal ===== */
#term-card { background: #1b1813; border-radius: var(--nb-radius); padding: 14px !important; border: 1px solid #332d26; gap: 12px !important; max-width: 920px; margin: 0 auto; width: 100%; }
#term-card .block, #term-card .form, #term-out, #term-in { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
#term-card .row { align-items: center; }
#term-shell .wrap { display: flex; gap: 6px; }
#term-shell label { display: inline-flex; align-items: center; height: 32px; border-radius: 999px !important; padding: 0 12px !important; font-size: 13px; background: #2a241d !important; border: 1px solid #3a332b !important; color: #d8cfc2 !important; box-shadow: none !important; }
#term-shell label.selected { background: var(--nb-accent) !important; color: #fff !important; border-color: var(--nb-accent) !important; }
#term-shell input[type="radio"] { display: none !important; }
#term-cwd { text-align: right; }
#term-cwd, #term-cwd * { color: #9a8f7f !important; font-family: var(--font-mono); font-size: 12px; }
#term-cwd code { background: #2a241d !important; border: none !important; }
#term-out label > span, #term-out span[data-testid="block-info"] { color: #9a8f7f !important; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
#term-out textarea { font-family: var(--font-mono) !important; font-size: 13px !important; background: #120f0b !important; color: #ece6da !important; border: 1px solid #332d26 !important; border-radius: 10px !important; line-height: 1.55; padding: 12px !important; }
#term-in .input-container { display: flex; align-items: center; gap: 8px; }
#term-in textarea { font-family: var(--font-mono) !important; font-size: 15px !important; background: #2a241d !important; color: #fff !important; border: 1px solid #3a332b !important; border-radius: 12px !important; padding: 10px 14px !important; }
#term-in textarea::placeholder { color: #7a7060; }
#term-in .submit-button { height: 40px; padding: 0 16px; border-radius: 12px !important; background: var(--nb-accent) !important; color: #fff !important; border: none !important; font-weight: 600; }
#term-card #explain-btn { background: #2a241d !important; color: #d8cfc2 !important; border: 1px solid #3a332b !important; height: 36px; }
#term-note, #term-note * { color: #7a7060 !important; font-size: 12px; line-height: 1.5; }

/* ===== security / admin shared width ===== */
.tabitem .block:has(.admin-card), .admin-wrap { max-width: 1000px; margin: 0 auto; width: 100%; }

/* ===== admin ===== */
.admin-card { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius); padding: 14px 16px !important; background: var(--block-background-fill); gap: 6px !important; min-height: 100%; }
.admin-card .prose { font-size: 13.5px; line-height: 1.7; }
.admin-card .block { padding: 0 !important; border: none !important; background: transparent !important; }
.admin-card h4 { margin: 0 0 4px; font-size: 14px; }
.row:has(#admin-refresh) { justify-content: flex-end; }
#admin-refresh { flex: 0 0 auto !important; width: auto !important; min-width: 0 !important; height: 34px; padding: 0 14px; }
.admin-acc { border: 1px solid var(--border-color-primary) !important; border-radius: var(--nb-radius) !important; }
.admin-acc > .label-wrap { padding: 12px 16px !important; font-weight: 600; }

/* ===== 💾 Storage — folder-style cards, one per component ===== */
.stor-drive { background: var(--block-background-fill); border: 1px solid var(--border-color-primary);
  border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; }
.stor-drive-top { display: flex; justify-content: space-between; font-weight: 600; font-size: 13.5px; gap: 10px; }
.stor-bar { height: 8px; border-radius: 999px; background: var(--color-accent-soft); overflow: hidden; margin: 9px 0 5px; }
.stor-bar-fill { height: 100%; background: linear-gradient(90deg, #c56a44, #e0a888); border-radius: 999px; }
.stor-drive-sub { font-size: 12px; color: var(--body-text-color-subdued); }
.stor-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.stor-card { border: 1px solid var(--border-color-primary); border-radius: 14px; overflow: hidden;
  background: var(--block-background-fill); display: flex; flex-direction: column; }
.stor-head { display: flex; align-items: center; gap: 9px; padding: 10px 14px; background: var(--color-accent-soft);
  border-bottom: 1px solid var(--border-color-primary); }
.stor-ico { font-size: 17px; line-height: 1; }
.stor-name { font-weight: 700; font-size: 13.5px; flex: 1; color: var(--body-text-color); }
.stor-size { font-weight: 700; font-size: 12px; background: var(--nb-accent); color: #fff; padding: 2px 10px; border-radius: 999px; white-space: nowrap; }
.stor-body { padding: 6px 14px 12px; }
.stor-item { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0;
  border-bottom: 1px dashed var(--border-color-primary); font-size: 13px; }
.stor-item:last-child { border-bottom: none; }
.stor-lbl { color: var(--body-text-color); }
.stor-val { color: var(--body-text-color-subdued); font-variant-numeric: tabular-nums; white-space: nowrap; }
.stor-tip { margin-top: 9px; font-size: 11.5px; color: var(--body-text-color-subdued); }
.stor-tip code, .stor-item code { background: var(--color-accent-soft); padding: 1px 5px; border-radius: 5px; font-size: 11px; }
.stor-pre { font-family: var(--font-mono); font-size: 11px; white-space: pre; overflow-x: auto; margin: 2px 0; color: var(--body-text-color); }
.stor-empty { padding: 16px; color: var(--body-text-color-subdued); font-size: 13px; }
@media (max-width: 760px) { .stor-grid { grid-template-columns: 1fr; } }

/* ===== 📊 usage bars ===== */
.use-row { display: flex; align-items: center; gap: 8px; padding: 5px 0; font-size: 12.5px; }
.use-name { flex: 0 0 42%; color: var(--body-text-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.use-track { flex: 1; height: 8px; border-radius: 999px; background: var(--color-accent-soft); overflow: hidden; }
.use-fill { display: block; height: 100%; background: linear-gradient(90deg, #c56a44, #e0a888); border-radius: 999px; }
.use-n { flex: 0 0 auto; color: var(--body-text-color-subdued); font-variant-numeric: tabular-nums; }
/* floating voice/theme toolbar */
#nb-tools button:hover { border-color: var(--nb-accent) !important; }

/* compact image attach dropzone in the composer column */
#img-in { max-width: 820px; width: 100%; margin: 0; }
#img-in .wrap, #img-in .image-frame { min-height: 64px !important; font-size: 12px; }
#img-in [data-testid="image"] { border: 1px dashed var(--border-color-primary) !important; border-radius: 12px; }

/* ===== 🎨 Image Studio ===== */
#img-wrap { max-width: 880px; margin: 0 auto; width: 100%; gap: 12px !important; }
.img-hero { text-align: center; padding: 6px 0 2px; }
.img-hero h2 { margin: 0 0 4px; font-size: 1.5rem; }
.img-hero p { margin: 0 auto; max-width: 620px; color: var(--body-text-color-subdued); font-size: 0.92rem; }
#img-prompt textarea { font-size: 1rem !important; border-radius: 14px !important; }
#img-controls { gap: 10px !important; flex-wrap: wrap; }
#img-gen { border-radius: 12px !important; font-weight: 600; }
#img-status { text-align: center; min-height: 1.2em; color: var(--body-text-color-subdued); }
#img-out { border-radius: 16px !important; overflow: hidden; background: var(--block-background-fill); }
#img-out img { border-radius: 16px; }
@media (max-width: 640px) { #img-controls > * { flex: 1 1 100% !important; } }

/* ===== 🇮🇳 India Lab (futuristic) ===== */
#il-wrap { max-width: 1120px; margin: 0 auto; width: 100%; gap: 14px !important; }
.il-hero {
  border-radius: 20px; padding: 26px 24px; text-align: center; color: #eaf2ff;
  background:
    radial-gradient(1200px 300px at 20% -40%, rgba(255,153,51,.30), transparent 60%),
    radial-gradient(1000px 320px at 90% 140%, rgba(19,136,8,.32), transparent 60%),
    linear-gradient(135deg, #0b1020 0%, #121a33 55%, #0b1428 100%);
  box-shadow: 0 10px 40px rgba(10,18,40,.35); position: relative; overflow: hidden;
}
.il-hero-badge {
  display: inline-block; font-size: .72rem; letter-spacing: .14em; font-weight: 700;
  padding: 5px 12px; border-radius: 999px; margin-bottom: 10px;
  background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.18); color: #cfe0ff;
}
.il-hero h1 { margin: 2px 0 8px; font-size: 1.9rem; letter-spacing: -.01em;
  background: linear-gradient(90deg,#ff9a3c,#ffd27a,#8ef5b0); -webkit-background-clip: text;
  background-clip: text; color: transparent; }
.il-hero p { margin: 0 auto 12px; max-width: 640px; color: #b9c6e4; font-size: .96rem; }
.il-hero .il-safe {
  font-size: .82rem; color: #ffe0b8; background: rgba(255,153,51,.12);
  border: 1px solid rgba(255,153,51,.30); border-radius: 12px; padding: 9px 13px;
  max-width: 760px; margin: 0 auto; }

#il-filters { gap: 10px !important; flex-wrap: wrap; align-items: center; }
.il-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; margin-top: 4px; }
.il-card {
  border-radius: 16px; padding: 15px 15px 13px; cursor: default;
  background: var(--block-background-fill); border: 1px solid var(--border-color-primary);
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease; }
.il-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(20,30,60,.18);
  border-color: #ff9a3c; }
.il-card-top { display: flex; justify-content: space-between; align-items: center; }
.il-ico { font-size: 1.7rem; }
.il-fut { font-size: .64rem; font-weight: 700; color: #7c3aed; background: rgba(124,58,237,.12);
  border: 1px solid rgba(124,58,237,.30); padding: 2px 7px; border-radius: 999px; }
.il-name { font-weight: 700; margin: 8px 0 3px; font-size: 1.02rem; }
.il-lvl { font-size: .74rem; opacity: .8; margin-bottom: 7px; }
.il-what { font-size: .83rem; color: var(--body-text-color-subdued); line-height: 1.45; min-height: 3.2em; }
.il-tools { font-size: .74rem; margin-top: 8px; color: var(--body-text-color-subdued);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.il-row2 { display: flex; gap: 6px; margin-top: 10px; }
.il-tag { font-size: .7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.il-atk { color: #c0392b; background: rgba(192,57,43,.10); border: 1px solid rgba(192,57,43,.25); }
.il-def { color: #1f8a4c; background: rgba(31,138,76,.10); border: 1px solid rgba(31,138,76,.25); }
.il-empty { text-align: center; padding: 30px; color: var(--body-text-color-subdued); }
#il-detail { border: 1px solid var(--border-color-primary); border-radius: 16px; padding: 4px 20px;
  background: var(--block-background-fill); }
#il-detail h2 { margin-top: 12px; }
#il-platforms { font-size: .9rem; }
@media (max-width: 640px) { .il-hero h1 { font-size: 1.5rem; } #il-filters > * { flex: 1 1 100% !important; } }

/* ===== 🩺 Self-repair doctor ===== */
.doc-wrap { display: flex; flex-direction: column; gap: 8px; }
.doc-head { font-weight: 700; font-size: 14px; padding: 4px 2px 6px; color: var(--body-text-color); }
.doc-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 13px; border-radius: 11px;
  border: 1px solid var(--border-color-primary); background: var(--block-background-fill); font-size: 13px; line-height: 1.5; }
.doc-ico { font-size: 15px; line-height: 1.35; flex: 0 0 auto; }
.doc-txt { color: var(--body-text-color); }
.doc-ok { border-left: 3px solid #37a05f; }
.doc-fixed { border-left: 3px solid var(--nb-accent); background: var(--color-accent-soft); }
.doc-warn { border-left: 3px solid #d79a2b; }
.doc-fail { border-left: 3px solid #d7483b; }

/* ===== 🌍 Remote access ===== */
#ra-view { margin-top: 2px; }
.ra-idle, .ra-warn, .ra-live { border: 1px solid var(--border-color-primary); border-radius: 12px; padding: 14px 16px; font-size: 13px; line-height: 1.55; }
.ra-idle { background: var(--block-background-fill); color: var(--body-text-color-subdued); }
.ra-warn { background: #fdf3e7; border-color: #ecc9a3; color: #7a4a12; }
.dark .ra-warn { background: #332516; border-color: #5a4425; color: #e7c79b; }
.ra-live { background: var(--block-background-fill); display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px; }
.ra-badge { font-weight: 700; font-size: 13.5px; color: #2f6b45; }
.ra-qr { width: 190px; height: 190px; border-radius: 12px; border: 1px solid var(--border-color-primary); background: #fff; padding: 8px; }
.ra-scan { font-size: 13px; color: var(--body-text-color); }
.ra-url { font-family: var(--font-mono); font-size: 13px; font-weight: 600; color: var(--nb-accent); word-break: break-all; }
.ra-note { font-size: 11.5px; color: var(--body-text-color-subdued); max-width: 380px; }
.ra-warn code, .ra-note code, .ra-idle code { background: var(--color-accent-soft); padding: 1px 5px; border-radius: 5px; font-size: 11px; }

/* ===== 🐉 Kali section ===== */
#kali-wrap { max-width: 1180px; margin: 0 auto; width: 100%; gap: 12px !important; }
#kali-head { align-items: center; }
#kali-title, #kali-title * { margin: 0 !important; font-size: 18px; }
#kali-status, #kali-status p { font-size: 13px; margin: 0 !important; }

/* connect — compact, clean */
.kali-acc { border: 1px solid var(--border-color-primary) !important; border-radius: 14px !important; background: var(--block-background-fill) !important; }
.kali-acc > .label-wrap { padding: 11px 16px !important; font-weight: 600; font-size: 13.5px; }
.kali-acc [data-testid="accordion-content"] { padding: 2px 16px 14px !important; }
.kali-acc input { font-size: 14px !important; }
.kali-acc .gr-button { align-self: flex-end; }

#kali-main { gap: 14px !important; align-items: stretch; }
#kali-term-col, #kali-ref-col { gap: 12px !important; }

/* ---- terminal: a real terminal window ---- */
#kali-term { background: #0c0a07; border: 1px solid #2c2620 !important; border-radius: 16px; padding: 0 !important;
  overflow: hidden; gap: 0 !important; box-shadow: 0 12px 34px rgba(26,16,6,.16); }
#kali-term-head { align-items: center; justify-content: space-between; padding: 9px 13px; background: #161210;
  border-bottom: 1px solid #2c2620; margin: 0 !important; gap: 8px; flex-wrap: nowrap !important; min-width: 0; }
#kali-term-head > *:first-child { flex: 1 1 auto; min-width: 0; width: auto !important; }
#kali-term-head > *:last-child { flex: 0 0 auto; width: auto !important; }
#kali-term-chrome, #kali-term-chrome .prose { width: auto !important; margin: 0 !important; }
.term-chrome { display: flex; align-items: center; gap: 7px; }
.term-chrome .dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.term-chrome .dot.r { background: #ff5f57; } .term-chrome .dot.y { background: #febc2e; } .term-chrome .dot.g { background: #28c840; }
.term-chrome .term-name { margin-left: 8px; color: #8a8072; font-family: var(--font-mono); font-size: 12px; }
#kali-target { margin: 0 !important; }
#kali-target .wrap { display: flex; gap: 2px; background: #0c0a07; border: 1px solid #2c2620; border-radius: 10px; padding: 2px; }
#kali-target label { display: inline-flex; align-items: center; height: 28px; border-radius: 8px !important; padding: 0 12px !important;
  font-size: 12px; background: transparent !important; border: none !important; color: #9a8f7f !important; box-shadow: none !important; }
#kali-target label.selected { background: var(--nb-accent) !important; color: #fff !important; }
#kali-target input[type="radio"] { display: none !important; }
#kali-out { padding: 0 !important; background: transparent !important; border: none !important; }
#kali-out textarea { font-family: var(--font-mono) !important; font-size: 12.5px !important; background: #0c0a07 !important;
  color: #c8f7b0 !important; border: none !important; border-radius: 0 !important; line-height: 1.55; padding: 14px !important; }
#kali-out .icon-button-wrapper { background: transparent !important; border: none !important; }
#kali-in { border-top: 1px solid #2c2620; padding: 8px !important; background: #120f0b; }
#kali-in .input-container { display: flex; align-items: center; gap: 8px; }
#kali-in textarea { font-family: var(--font-mono) !important; font-size: 14px !important; background: #221d17 !important;
  color: #fff !important; border: 1px solid #332d26 !important; border-radius: 10px !important; padding: 9px 13px !important; }
#kali-in textarea::placeholder { color: #6f665a; }
#kali-in .submit-button { height: 38px; padding: 0 18px; border-radius: 10px !important; background: var(--nb-accent) !important;
  color: #fff !important; border: none !important; font-weight: 600; }

/* ---- AI helper ---- */
#kali-ai { border: 1px solid var(--border-color-primary); border-radius: 14px; padding: 13px 14px !important;
  background: var(--block-background-fill); gap: 10px !important; }
#kali-ai .block { border: none !important; background: transparent !important; padding: 0 !important; }
#kali-ai-label, #kali-ai-label * { font-size: 13px; margin: 0 !important; color: var(--body-text-color); }
#kali-ai-in textarea { font-size: 14px !important; border-radius: 10px !important; }
#kali-ai .gr-button { white-space: nowrap; }

/* ---- compact connect card (right column) ---- */
#kali-connect { border: 1px solid var(--border-color-primary); border-radius: 14px; padding: 0 !important;
  background: var(--block-background-fill); gap: 0 !important; overflow: hidden; }
#kali-connect .block { border: none !important; background: transparent !important; }
#kali-connect-title { padding: 0 !important; }
#kali-connect .ref-head { padding: 9px 13px; font-size: 13px; }
#kali-connect .ref-head .ref-ico { font-size: 14px; }
#kali-connect-body { padding: 9px 12px 10px !important; gap: 6px !important; }
#kali-connect-body > .block { padding: 0 !important; gap: 2px !important; }
#kali-connect textarea, #kali-connect input { font-size: 12.5px !important; border-radius: 8px !important;
  padding: 6px 10px !important; min-height: 0 !important; line-height: 1.3 !important; }
#kali-connect label > span:first-child, #kali-connect .block-info,
#kali-connect span[data-testid="block-info"] { font-size: 10.5px !important; margin-bottom: 1px !important;
  text-transform: uppercase; letter-spacing: .03em; opacity: .8; }
#kali-connect-btns { gap: 7px !important; flex-wrap: nowrap !important; margin-top: 1px; }
#kali-connect-btns .gr-button { flex: 1 1 0; min-width: 0; min-height: 32px !important; height: 32px;
  padding: 0 10px !important; font-size: 12.5px !important; }
#kali-connect-hint, #kali-connect-hint * { font-size: 10.5px !important; color: var(--body-text-color-subdued);
  margin: 0 !important; line-height: 1.45; }
#kali-connect-hint code { font-size: 9.5px !important; padding: 0 3px; }

/* ---- reference: card with a header strip ---- */
#kali-ref { border: 1px solid var(--border-color-primary); border-radius: 16px; padding: 0 !important;
  background: var(--block-background-fill); gap: 0 !important; overflow: hidden; }
#kali-ref .block { border: none !important; background: transparent !important; }
#kali-ref-title { padding: 0 !important; }
.ref-head { display: flex; align-items: center; gap: 9px; padding: 13px 16px; background: var(--color-accent-soft);
  border-bottom: 1px solid var(--border-color-primary); font-weight: 700; font-size: 14.5px; color: var(--body-text-color); }
.ref-head .ref-ico { font-size: 16px; }
#kali-ref-search { padding: 12px 14px 4px !important; }
#kali-ref-search input { font-size: 13.5px !important; border-radius: 10px !important; background: var(--input-background-fill) !important; }
#kali-ref-view { padding: 6px 16px 16px !important; font-size: 13.5px; line-height: 1.62; }
#kali-ref-view h2 { font-size: 16px; margin: 2px 0 8px; }
#kali-ref-view h3 { font-size: 15px; margin: 4px 0 6px; }
#kali-ref-view code { font-size: 12px; background: var(--color-accent-soft); padding: 1px 5px; border-radius: 5px; }
#kali-ref-view ul { margin: 4px 0; padding-left: 18px; }
#kali-ref-view li { margin: 3px 0; }

/* ============================================================
   🐉 KALI OS — immersive dark "full page" theme (scoped to #kali-wrap only)
   Deep navy desktop + electric-blue dragon accents. No other tab changes.
   ============================================================ */
#kali-wrap {
  --k-bg: #0a0e17; --k-panel: #111726; --k-field: #0c1322; --k-border: #1f2b40;
  --k-text: #cdd9ea; --k-mut: #7e8ca5; --k-head: #eaf2ff; --k-term: #9bf0b0;
  --nb-accent: #4d8bff; --nb-accent-hover: #2f6fe0;        /* flips Run/toggle to Kali blue */
  max-width: none !important; width: 100%; color: var(--k-text);
  background:
    radial-gradient(1100px 520px at 78% -12%, #16254486 0%, #0a0e1700 60%),
    linear-gradient(180deg, #0c1322 0%, #0a0e17 100%);
  border: 1px solid var(--k-border); border-radius: 18px;
  padding: 18px 18px 22px !important; min-height: calc(100dvh - 128px);
  box-shadow: 0 18px 60px rgba(4,10,24,.35);
}
/* a thin neon top accent, like an OS title strip */
#kali-wrap #kali-head { position: relative; padding-bottom: 2px; }
#kali-wrap #kali-title, #kali-wrap #kali-title * { color: var(--k-head) !important; }
#kali-wrap #kali-status, #kali-wrap #kali-status p { color: var(--k-mut) !important; }
#kali-wrap #kali-status strong { color: var(--k-text) !important; }
#kali-wrap #kali-status code, #kali-wrap #kali-connect-hint code, #kali-wrap #kali-ref-view code {
  background: var(--k-field) !important; color: #86e7ff !important; border: 1px solid var(--k-border) !important; }

/* panels (connect, reference, AI helper) → dark glass cards */
#kali-wrap #kali-connect, #kali-wrap #kali-ref, #kali-wrap #kali-ai {
  background: var(--k-panel) !important; border: 1px solid var(--k-border) !important;
  box-shadow: 0 10px 34px rgba(3,8,20,.45) !important; }
#kali-wrap .ref-head { background: linear-gradient(90deg, #16284a, #0f1a34) !important;
  border-bottom: 1px solid var(--k-border) !important; }
#kali-wrap .ref-head, #kali-wrap .ref-head * { color: var(--k-head) !important; }
/* make every inner wrapper transparent so the dark panels show through
   (the dark panels, fields and terminal keep their colour via #id selectors) */
#kali-wrap .block, #kali-wrap .form, #kali-wrap .gap, #kali-wrap .styler,
#kali-wrap .md, #kali-wrap .prose, #kali-wrap #kali-connect-body,
#kali-wrap #kali-connect-body > * { background: transparent !important; }
#kali-wrap #kali-connect input, #kali-wrap #kali-connect textarea,
#kali-wrap #kali-ref-search input, #kali-wrap #kali-ref-search textarea,
#kali-wrap #kali-ai-in input, #kali-wrap #kali-ai-in textarea {
  background: var(--k-field) !important; border: 1px solid var(--k-border) !important; color: var(--k-text) !important; }
#kali-wrap #kali-connect input::placeholder, #kali-wrap #kali-connect textarea::placeholder,
#kali-wrap #kali-ref-search input::placeholder, #kali-wrap #kali-ref-search textarea::placeholder,
#kali-wrap #kali-ai-in textarea::placeholder { color: #5f6f88 !important; }
#kali-wrap #kali-connect-hint, #kali-wrap #kali-connect-hint * { color: var(--k-mut) !important; }
#kali-wrap #kali-ai-label, #kali-wrap #kali-ai-label * { color: var(--k-text) !important; }
#kali-wrap #kali-ref-view, #kali-wrap #kali-ref-view p, #kali-wrap #kali-ref-view li { color: var(--k-text) !important; }
#kali-wrap #kali-ref-view h2, #kali-wrap #kali-ref-view h3, #kali-wrap #kali-ref-view strong { color: var(--k-head) !important; }
#kali-wrap #kali-ref-view em { color: var(--k-mut) !important; }

/* terminal: subtle blue glow so it reads as the OS centrepiece */
#kali-wrap #kali-term { border-color: #233250 !important;
  box-shadow: 0 0 0 1px #233250, 0 14px 46px rgba(20,60,130,.22) !important; }

/* buttons → Kali blue */
#kali-wrap button.primary, #kali-wrap .primary.gr-button, #kali-wrap #kali-in .submit-button {
  background: linear-gradient(180deg, #5a95ff, #2f6fe0) !important; border: none !important; color: #fff !important; }
#kali-wrap button.primary:hover, #kali-wrap #kali-in .submit-button:hover {
  background: linear-gradient(180deg, #4d8bff, #255fcf) !important; }
#kali-wrap button.secondary {
  background: var(--k-field) !important; border: 1px solid var(--k-border) !important; color: #b9c7dd !important; }
#kali-wrap button.secondary:hover { border-color: var(--nb-accent) !important; color: #fff !important; }

/* ===== responsive ===== */
@media (max-width: 900px) {
  #kali-main { flex-direction: column; }
  #kali-ref { min-height: auto; }
  :root { --nb-gutter: 12px; }
  #topbar { padding: 6px 0 2px 46px; }
  #topbar .title { display: block; }
  .tabs .tab-wrapper { margin: 0 0 10px !important; }
  .tabs [role="tab"] { padding: 7px 12px !important; font-size: 13px; }
  #chat .bot, #chat .bot.message { font-size: 15.5px; }
  .admin-card { min-height: auto; }
}
@media (max-width: 600px) {
  .badge { font-size: 11px; padding: 4px 8px; }
  .hide-sm { display: none !important; }
  #chat .placeholder-content h3 { font-size: 32px; }
  #composer textarea { font-size: 16px !important; } /* 16px stops iOS zooming in */
}
@media (hover: none) { #modes label, #examples button { -webkit-tap-highlight-color: transparent; } }

/* ===== desktop polish: no empty top band, mode pills wrap, tight rhythm ===== */
@media (min-width: 901px) {
  #topbar { min-height: 30px !important; padding: 2px 0 0 !important; }
  .tabs .tab-wrapper { margin: 2px 0 14px !important; }
  /* let all mode pills show (wrap to a second line) instead of being cut off */
  #modes .wrap { flex-wrap: wrap !important; overflow: visible !important; row-gap: 8px !important; }
}
/* wide screens: lift the status badges onto the top-right corner, same line as the tabs */
@media (min-width: 1200px) {
  .gradio-container { position: relative; }
  .block:has(#topbar) { position: absolute !important; top: 16px; right: 26px; width: auto !important;
    min-height: 0 !important; padding: 0 !important; margin: 0 !important; z-index: 40; }
  #topbar { min-height: 0 !important; justify-content: flex-end; }
  .tabs .tab-wrapper { margin: 6px 0 16px !important; }
}

/* ===== mobile: make ALL tabs reachable (no hidden overflow menu) ===== */
@media (max-width: 760px) {
  .tabs .tab-wrapper { overflow: visible !important; }
  .tabs .tab-container[role="tablist"] {
    display: flex !important; flex-wrap: nowrap !important; justify-content: flex-start !important;
    overflow-x: auto !important; overflow-y: hidden; -webkit-overflow-scrolling: touch;
    scrollbar-width: none; gap: 6px; padding: 2px 2px 4px; scroll-snap-type: x proximity;
  }
  .tabs .tab-container[role="tablist"]::-webkit-scrollbar { display: none; }
  .tabs .tab-container[role="tablist"] button { display: inline-flex !important; flex: 0 0 auto; scroll-snap-align: start; }
  .tabs .overflow-menu, .tabs [aria-label="More tabs"] { display: none !important; }
  .tabs .tab-container.visually-hidden { display: none !important; }
  #topbar { padding: 8px 0 2px 46px; }
  #modes label { height: 38px; font-size: 14px; }
  #chat .placeholder-content { margin-top: 8vh; }
  #composer textarea { padding: 12px 10px !important; }
  #composer .submit-button, #composer .stop-button { width: 40px !important; height: 40px !important; }
}
"""

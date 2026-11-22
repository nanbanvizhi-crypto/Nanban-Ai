"""
Look and feel of the Nanban web app: one theme + one stylesheet, shared by app.py and server.py.

Ultra-modern fintech-style interface: an airy off-white canvas with soft pastel gradient
blooms, a bright lime-green accent, near-black primary actions, big rounded corners, soft
shadows and a clean geometric font (Plus Jakarta Sans). Works the same on laptop, iPad and
phone, in light and dark mode.
"""

import gradio as gr
from gradio.themes.utils import colors, fonts, sizes

# Bright lime / chartreuse accent (the app's highlight colour — selected states, progress,
# checkmarks, focus rings). Primary BUTTONS are near-black; lime is the spark on top.
LIME = colors.Color(
    name="lime", c50="#f6fce3", c100="#ecf9c4", c200="#def58f", c300="#cdee5a", c400="#bfe63a",
    c500="#a9d31f", c600="#86a916", c700="#657f16", c800="#4f6318", c900="#425219", c950="#232d08",
)


def theme() -> gr.themes.Base:
    return gr.themes.Base(
        primary_hue=LIME, secondary_hue=LIME, neutral_hue=colors.gray,
        text_size=sizes.text_md, spacing_size=sizes.spacing_md, radius_size=sizes.radius_lg,
        font=[fonts.GoogleFont("Plus Jakarta Sans"), "ui-sans-serif", "system-ui",
              "-apple-system", "Segoe UI", "sans-serif"],
        font_mono=[fonts.GoogleFont("JetBrains Mono"), "Consolas", "ui-monospace", "monospace"],
    ).set(
        # airy off-white canvas (light) / deep charcoal (dark)
        body_background_fill="#f3f3ef", body_background_fill_dark="#121315",
        block_background_fill="#ffffff", block_background_fill_dark="#1d1f22",
        block_border_color="#eceae4", block_border_color_dark="#2b2e32",
        block_shadow="0 1px 2px rgba(20,22,18,.04)", block_shadow_dark="none",
        block_label_background_fill="transparent", block_label_background_fill_dark="transparent",
        block_title_text_weight="700",
        input_background_fill="#ffffff", input_background_fill_dark="#232629",
        input_border_color="#e7e5df", input_border_color_dark="#33373b",
        input_border_color_focus="#bfe63a", input_border_color_focus_dark="#bfe63a",
        input_shadow_focus="0 0 0 3px rgba(169,211,31,.22)", input_shadow_focus_dark="0 0 0 3px rgba(169,211,31,.26)",
        # primary = near-black pill (fintech CTA); lime is for accents/selected states in CSS
        button_primary_background_fill="#141514", button_primary_background_fill_hover="#000000",
        button_primary_background_fill_dark="#eef1e6", button_primary_background_fill_hover_dark="#ffffff",
        button_primary_text_color="#ffffff", button_primary_text_color_dark="#141514",
        button_secondary_background_fill="#f1f1ec", button_secondary_background_fill_hover="#e8e8e1",
        button_secondary_background_fill_dark="#2a2e31", button_secondary_background_fill_hover_dark="#343a3e",
        button_secondary_text_color="#1f2420", button_secondary_text_color_dark="#e7eae2",
        button_secondary_border_color="transparent", button_secondary_border_color_dark="transparent",
        border_color_primary="#eceae4", border_color_primary_dark="#2b2e32",
        color_accent_soft="#eef9d2", color_accent_soft_dark="#2c3317",
        checkbox_background_color_selected="#bfe63a", checkbox_background_color_selected_dark="#bfe63a",
        slider_color="#a9d31f",
    )


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500;1,600&display=swap');

/* ===== base ===== */
:root {
  --nb-gutter: 16px; --nb-radius: 20px; --nb-radius-sm: 14px; --nb-radius-lg: 26px;
  --nb-accent: #a9d31f; --nb-accent-bright: #bfe63a; --nb-accent-hover: #96bd16;
  --nb-ink: #141514;                /* near-black primary */
  --nb-col: 820px;                  /* centered reading column width */
  --nb-user-bg: #eef9d2;            /* soft lime card for the user's own message (light) */
  --nb-card-shadow: 0 8px 30px rgba(28,32,20,.07);
  --nb-serif: 'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif;
}
.dark { --nb-ink: #eef1e6; --nb-user-bg: #2c3317; --nb-card-shadow: 0 10px 34px rgba(0,0,0,.35); }

footer, .built-with, a[href*="gradio.app"] { display: none !important; }
gradio-app, .gradio-container { max-width: 100% !important; }
body, .gradio-container { -webkit-font-smoothing: antialiased; letter-spacing: -.004em; }

/* soft pastel gradient "blooms" behind everything (light) */
.gradio-container {
  background:
    radial-gradient(760px 460px at 10% -8%, rgba(191,230,58,.20), transparent 58%),
    radial-gradient(720px 440px at 98% 2%, rgba(255,176,138,.16), transparent 55%),
    radial-gradient(820px 560px at 72% 112%, rgba(150,196,255,.14), transparent 60%),
    var(--body-background-fill) !important;
  background-attachment: fixed !important;
}
.dark .gradio-container {
  background:
    radial-gradient(760px 460px at 10% -8%, rgba(169,211,31,.12), transparent 58%),
    radial-gradient(720px 440px at 98% 2%, rgba(255,150,110,.08), transparent 55%),
    radial-gradient(820px 560px at 72% 112%, rgba(90,140,220,.10), transparent 60%),
    var(--body-background-fill) !important;
}

h1, h2, h3, h4 { letter-spacing: -.02em; }
.block.padded:has(#mode-info), .block:has(#topbar), .block:has(#brand), .block.padded:has(#status) { padding: 0 !important; }
.prose:has(#topbar), .prose:has(#brand) { margin: 0 !important; }
.column { gap: 10px !important; }

/* ===== sidebar ===== */
.sidebar-parent .sidebar { border-right: 1px solid var(--border-color-primary); background: rgba(255,255,255,.72); backdrop-filter: blur(14px); }
.dark .sidebar-parent .sidebar { background: rgba(24,26,29,.72); }
.sidebar .sidebar-content { min-height: 100dvh; padding: 18px 14px calc(14px + env(safe-area-inset-bottom)) !important; display: flex; flex-direction: column; }
.sidebar .sidebar-content > .column { flex: 1; gap: 6px !important; }
.sidebar .toggle-button { top: 14px !important; width: 36px; height: 36px; border-radius: 12px !important; border: 1px solid var(--border-color-primary) !important; background: var(--block-background-fill) !important; box-shadow: var(--nb-card-shadow) !important; }
#brand { display: flex; align-items: center; gap: 11px; padding: 0 2px 12px; }
#brand img { width: 40px; height: 40px; border-radius: 13px; box-shadow: var(--nb-card-shadow); }
#brand .name { font-weight: 800; font-size: 17px; letter-spacing: -.02em; line-height: 1.2; }
#brand .sub { font-size: 12px; color: var(--body-text-color-subdued); margin-top: 2px; }
#new-chat { width: 100%; height: 44px; justify-content: center; font-weight: 700; font-size: 14px; margin: 0 0 8px; border-radius: 14px !important; }
.sidebar .gr-accordion { border: none !important; background: transparent !important; padding: 0 !important; }
.sidebar .gr-accordion > .label-wrap { width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 10px 12px !important; border-radius: 12px; font-weight: 600; font-size: 14px; }
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
#topbar .title { font-weight: 800; font-size: 16px; display: none; }
#topbar .badges { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; margin-left: auto; }
.badge { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; padding: 6px 11px; border-radius: 999px; background: rgba(255,255,255,.7); border: 1px solid var(--border-color-primary); color: var(--body-text-color); white-space: nowrap; line-height: 1; backdrop-filter: blur(8px); }
.dark .badge { background: rgba(32,35,38,.7); }
.badge.ok { background: #eef9d2; border-color: #d6ef9a; color: #4f6318; }
.badge.warn { background: #fdeccd; border-color: #f3d79a; color: #8a5a00; }
.dark .badge.ok { background: #28310f; border-color: #3f5018; color: #c6ee6a; }
.dark .badge.warn { background: #3a2c0a; border-color: #5a4420; color: #f0c060; }

/* ===== tabs — pill bar, active = black pill ===== */
.tabs { gap: 0 !important; }
.tabs .tab-wrapper { border: none !important; margin: 2px 0 12px !important; padding: 0 !important; }
.tabs .tab-container { gap: 5px; border: none !important; }
.tabs [role="tab"] { border: 1px solid transparent !important; border-radius: 999px !important; padding: 9px 16px !important; margin: 0 !important; font-weight: 600; font-size: 14px; color: var(--body-text-color-subdued) !important; background: rgba(255,255,255,.55) !important; transition: all .15s ease; }
.dark .tabs [role="tab"] { background: rgba(32,35,38,.5) !important; }
.tabs [role="tab"]:hover { border-color: var(--border-color-primary) !important; color: var(--body-text-color) !important; }
.tabs [role="tab"]::after, .tabs [role="tab"]::before, .tabs .tab-container::after, .tabs .tab-container::before { display: none !important; }
.tabs [role="tab"].selected { background: var(--nb-ink) !important; color: #fff !important; border-color: var(--nb-ink) !important; box-shadow: 0 6px 18px rgba(18,20,16,.22) !important; }
.dark .tabs [role="tab"].selected { color: #141514 !important; }
.tabitem { padding: 0 !important; border: none !important; }
.tabitem > .column { gap: 12px !important; }

/* ===== reading column (chat) ===== */
#chat-col { max-width: 840px; width: 100%; margin: 0; gap: 12px !important; }

/* ===== mode pills ===== */
#modes { padding: 0 !important; border: none !important; background: transparent !important; }
#modes .wrap { display: flex !important; flex-wrap: nowrap !important; gap: 8px !important; overflow-x: auto; padding: 2px 2px 4px; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
#modes .wrap::-webkit-scrollbar { display: none; }
#modes label { display: inline-flex; align-items: center; height: 38px; border-radius: 999px !important; padding: 0 16px !important; border: 1px solid var(--border-color-primary) !important; background: rgba(255,255,255,.72) !important; font-weight: 600; font-size: 13.5px; white-space: nowrap; cursor: pointer; transition: all .16s ease; box-shadow: none !important; backdrop-filter: blur(6px); }
.dark #modes label { background: rgba(32,35,38,.6) !important; }
#modes label:hover { border-color: var(--nb-accent) !important; transform: translateY(-1px); }
#modes label.selected { background: var(--nb-ink) !important; border-color: var(--nb-ink) !important; color: #fff !important; box-shadow: 0 6px 16px rgba(18,20,16,.24) !important; }
.dark #modes label.selected { color: #141514 !important; }
#modes input[type="radio"] { display: none !important; }
#mode-info { margin: -4px 0 0 2px !important; }
#mode-info, #mode-info p { font-size: 13px; color: var(--body-text-color-subdued); font-style: normal; line-height: 1.5; }
#allow-actions { padding: 11px 13px; border: 1px dashed var(--border-color-primary); border-radius: 14px; background: rgba(255,255,255,.5); }
#allow-actions label { font-size: 13px; }

/* ===== chat: flat, document-like ===== */
#chat { border: none !important; background: transparent !important; min-height: 320px; }
#chat .message-wrap { padding: 6px 0 !important; gap: 14px; }
#chat .message-row { max-width: 100% !important; }
#chat .bot, #chat .bot.message { background: transparent !important; border: none !important; box-shadow: none !important; padding: 2px 2px !important; font-size: 16px; line-height: 1.66; border-radius: 0 !important; }
#chat .user, #chat .user.message { background: var(--nb-user-bg) !important; color: var(--body-text-color) !important; border: none !important; border-radius: 18px 18px 6px 18px !important; padding: 11px 16px !important; font-size: 15.5px; line-height: 1.55; }
#chat .user *, #chat .user.message * { color: var(--body-text-color) !important; }
#chat .avatar-container { display: none !important; }
#chat .message-row.bot-row { justify-content: flex-start; }
#chat .message-row.user-row { justify-content: flex-end; }
#chat .bot pre, #chat .bot code { font-size: 13.5px; }
#chat .bot pre { border-radius: 14px !important; }
#chat .icon-button-wrapper.top-panel, #chat > .top-panel { display: none !important; }
#chat .icon-button-wrapper { background: transparent !important; border: none !important; }

/* greeting / empty state */
#chat .placeholder-content { opacity: 1; text-align: center; max-width: 520px; margin: 12vh auto 0; }
#chat .placeholder-content h3 { font-family: var(--nb-serif); font-weight: 800; font-size: 40px; line-height: 1.08; letter-spacing: -.03em; margin-bottom: 10px; color: var(--body-text-color); }
#chat .placeholder-content p { font-size: 15px; color: var(--body-text-color-subdued); }

/* ===== composer ===== */
#composer { position: sticky; bottom: 0; z-index: 5; padding: 8px 0 calc(8px + env(safe-area-inset-bottom)); background: linear-gradient(to bottom, transparent, var(--body-background-fill) 24%); gap: 10px !important; }
#composer .block { border-radius: var(--nb-radius-lg) !important; border: 1px solid var(--border-color-primary) !important; background: rgba(255,255,255,.86) !important; padding: 5px 7px 5px 14px !important; box-shadow: var(--nb-card-shadow) !important; backdrop-filter: blur(10px); }
.dark #composer .block { background: rgba(30,33,36,.86) !important; }
#composer .input-container { display: flex; align-items: center; gap: 6px; }
#composer textarea { font-size: 16px !important; border: none !important; background: transparent !important; box-shadow: none !important; padding: 12px 8px !important; }
#composer .submit-button, #composer .stop-button { width: 40px !important; height: 40px !important; min-width: 40px; margin: 0 !important; border-radius: 50% !important; display: flex; align-items: center; justify-content: center; border: none !important; }
#composer .submit-button { background: var(--nb-ink) !important; color: #fff !important; }
.dark #composer .submit-button { color: #141514 !important; }
#composer .submit-button:hover { background: #000 !important; transform: translateY(-1px); }
#composer .submit-button svg { width: 18px; height: 18px; }
#composer .stop-button { background: #ececec !important; color: #141514 !important; }
.dark #composer .stop-button { background: #343a3e !important; color: #e7eae2 !important; }
#examples, #examples > div, #examples .gallery, #examples .block, .block:has(#examples), .block:has(.gallery-item), #composer .block:has(.gallery) { padding: 0 !important; border: none !important; background: transparent !important; box-shadow: none !important; backdrop-filter: none !important; }
#examples .label { display: none !important; }
#examples .gallery { display: flex !important; flex-wrap: nowrap !important; overflow-x: auto; gap: 8px; scrollbar-width: none; padding: 0 2px 4px; justify-content: center; }
#examples .gallery::-webkit-scrollbar { display: none; }
#examples .gallery-item, #examples button { flex: 0 0 auto; width: auto !important; max-width: none !important; height: 36px; border-radius: 999px !important; border: 1px solid var(--border-color-primary) !important; background: rgba(255,255,255,.66) !important; color: var(--body-text-color-subdued) !important; font-size: 13px !important; padding: 0 15px !important; white-space: nowrap; }
.dark #examples .gallery-item, .dark #examples button { background: rgba(32,35,38,.55) !important; }
#examples button:hover { border-color: var(--nb-accent) !important; color: var(--body-text-color) !important; }

/* ===== terminal ===== */
#term-card { background: #15171a; border-radius: var(--nb-radius); padding: 15px !important; border: 1px solid #262a2e; gap: 12px !important; max-width: 940px; margin: 0 auto; width: 100%; box-shadow: var(--nb-card-shadow); }
#term-card .block, #term-card .form, #term-out, #term-in { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
#term-card .row { align-items: center; }
#term-shell .wrap { display: flex; gap: 6px; }
#term-shell label { display: inline-flex; align-items: center; height: 32px; border-radius: 999px !important; padding: 0 13px !important; font-size: 13px; background: #23272b !important; border: 1px solid #333840 !important; color: #cdd3d9 !important; box-shadow: none !important; }
#term-shell label.selected { background: var(--nb-accent-bright) !important; color: #141514 !important; border-color: var(--nb-accent-bright) !important; }
#term-shell input[type="radio"] { display: none !important; }
#term-cwd { text-align: right; }
#term-cwd, #term-cwd * { color: #8a919a !important; font-family: var(--font-mono); font-size: 12px; }
#term-cwd code { background: #23272b !important; border: none !important; }
#term-out label > span, #term-out span[data-testid="block-info"] { color: #8a919a !important; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
#term-out textarea { font-family: var(--font-mono) !important; font-size: 13px !important; background: #0e1013 !important; color: #e6ebe2 !important; border: 1px solid #262a2e !important; border-radius: 12px !important; line-height: 1.55; padding: 12px !important; }
#term-in .input-container { display: flex; align-items: center; gap: 8px; }
#term-in textarea { font-family: var(--font-mono) !important; font-size: 15px !important; background: #23272b !important; color: #fff !important; border: 1px solid #333840 !important; border-radius: 12px !important; padding: 10px 14px !important; }
#term-in textarea::placeholder { color: #727982; }
#term-in .submit-button { height: 40px; padding: 0 16px; border-radius: 12px !important; background: var(--nb-accent-bright) !important; color: #141514 !important; border: none !important; font-weight: 700; }
#term-card #explain-btn { background: #23272b !important; color: #cdd3d9 !important; border: 1px solid #333840 !important; height: 36px; }
#term-note, #term-note * { color: #727982 !important; font-size: 12px; line-height: 1.5; }

/* ===== security / admin shared width ===== */
.tabitem .block:has(.admin-card), .admin-wrap { max-width: 1000px; margin: 0 auto; width: 100%; }

/* ===== admin ===== */
.admin-card { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius); padding: 16px 18px !important; background: var(--block-background-fill); gap: 6px !important; min-height: 100%; box-shadow: var(--nb-card-shadow); }
.admin-card .prose { font-size: 13.5px; line-height: 1.7; }
.admin-card .block { padding: 0 !important; border: none !important; background: transparent !important; }
.admin-card h4 { margin: 0 0 4px; font-size: 14px; }
.row:has(#admin-refresh) { justify-content: flex-end; }
#admin-refresh { flex: 0 0 auto !important; width: auto !important; min-width: 0 !important; height: 36px; padding: 0 15px; }
.admin-acc { border: 1px solid var(--border-color-primary) !important; border-radius: var(--nb-radius) !important; }
.admin-acc > .label-wrap { padding: 13px 17px !important; font-weight: 700; }

/* ===== 💾 Storage ===== */
.stor-drive { background: var(--block-background-fill); border: 1px solid var(--border-color-primary);
  border-radius: var(--nb-radius-sm); padding: 13px 15px; margin-bottom: 12px; box-shadow: var(--nb-card-shadow); }
.stor-drive-top { display: flex; justify-content: space-between; font-weight: 700; font-size: 13.5px; gap: 10px; }
.stor-bar { height: 8px; border-radius: 999px; background: var(--color-accent-soft); overflow: hidden; margin: 9px 0 5px; }
.stor-bar-fill { height: 100%; background: linear-gradient(90deg, #a9d31f, #cdee5a); border-radius: 999px; }
.stor-drive-sub { font-size: 12px; color: var(--body-text-color-subdued); }
.stor-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.stor-card { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius-sm); overflow: hidden;
  background: var(--block-background-fill); display: flex; flex-direction: column; box-shadow: var(--nb-card-shadow); }
.stor-head { display: flex; align-items: center; gap: 9px; padding: 11px 15px; background: var(--color-accent-soft);
  border-bottom: 1px solid var(--border-color-primary); }
.stor-ico { font-size: 17px; line-height: 1; }
.stor-name { font-weight: 700; font-size: 13.5px; flex: 1; color: var(--body-text-color); }
.stor-size { font-weight: 700; font-size: 12px; background: var(--nb-ink); color: #fff; padding: 3px 11px; border-radius: 999px; white-space: nowrap; }
.dark .stor-size { color: #141514; background: var(--nb-accent-bright); }
.stor-body { padding: 6px 15px 12px; }
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
.use-fill { display: block; height: 100%; background: linear-gradient(90deg, #a9d31f, #cdee5a); border-radius: 999px; }
.use-n { flex: 0 0 auto; color: var(--body-text-color-subdued); font-variant-numeric: tabular-nums; }
#nb-tools button:hover { border-color: var(--nb-accent) !important; }

/* compact image attach dropzone in the composer column */
#img-in { max-width: 840px; width: 100%; margin: 0; }
#img-in .wrap, #img-in .image-frame { min-height: 64px !important; font-size: 12px; }
#img-in [data-testid="image"] { border: 1px dashed var(--border-color-primary) !important; border-radius: 14px; }

/* ===== 🎨 Image Studio ===== */
#img-wrap { max-width: 900px; margin: 0 auto; width: 100%; gap: 12px !important; }
.img-hero { text-align: center; padding: 6px 0 2px; }
.img-hero h2 { margin: 0 0 4px; font-size: 1.6rem; font-weight: 800; letter-spacing: -.03em; }
.img-hero p { margin: 0 auto; max-width: 620px; color: var(--body-text-color-subdued); font-size: 0.92rem; }
#img-prompt textarea { font-size: 1rem !important; border-radius: var(--nb-radius-sm) !important; }
#img-controls { gap: 10px !important; flex-wrap: wrap; }
#img-gen { border-radius: 14px !important; font-weight: 700; }
#img-status { text-align: center; min-height: 1.2em; color: var(--body-text-color-subdued); }
#img-out { border-radius: var(--nb-radius) !important; overflow: hidden; background: var(--block-background-fill); box-shadow: var(--nb-card-shadow); }
#img-out img { border-radius: var(--nb-radius); }
@media (max-width: 640px) { #img-controls > * { flex: 1 1 100% !important; } }

/* ===== 🇮🇳 India Lab (futuristic) ===== */
#il-wrap { max-width: 1120px; margin: 0 auto; width: 100%; gap: 14px !important; }
#il-filters { gap: 10px !important; flex-wrap: wrap; align-items: center; }
.il-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; margin-top: 4px; }
.il-card {
  border-radius: var(--nb-radius-sm); padding: 15px 15px 13px; cursor: default;
  background: var(--block-background-fill); border: 1px solid var(--border-color-primary); box-shadow: var(--nb-card-shadow);
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease; }
.il-card:hover { transform: translateY(-3px); box-shadow: 0 16px 34px rgba(28,32,20,.14);
  border-color: var(--nb-accent); }
.il-card-top { display: flex; justify-content: space-between; align-items: center; }
.il-ico { font-size: 1.7rem; }
.il-fut { font-size: .64rem; font-weight: 700; color: #6b8f12; background: var(--color-accent-soft);
  border: 1px solid #d6ef9a; padding: 2px 7px; border-radius: 999px; }
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
#il-detail { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius); padding: 4px 20px;
  background: var(--block-background-fill); box-shadow: var(--nb-card-shadow); }
#il-detail h2 { margin-top: 12px; }
#il-platforms { font-size: .9rem; }
@media (max-width: 640px) { #il-filters > * { flex: 1 1 100% !important; } }

/* ===== 🩺 Self-repair doctor ===== */
.doc-wrap { display: flex; flex-direction: column; gap: 8px; }
.doc-head { font-weight: 800; font-size: 14px; padding: 4px 2px 6px; color: var(--body-text-color); }
.doc-item { display: flex; align-items: flex-start; gap: 10px; padding: 11px 14px; border-radius: 13px;
  border: 1px solid var(--border-color-primary); background: var(--block-background-fill); font-size: 13px; line-height: 1.5; box-shadow: var(--nb-card-shadow); }
.doc-ico { font-size: 15px; line-height: 1.35; flex: 0 0 auto; }
.doc-txt { color: var(--body-text-color); }
.doc-ok { border-left: 3px solid #86a916; }
.doc-fixed { border-left: 3px solid var(--nb-accent); background: var(--color-accent-soft); }
.doc-warn { border-left: 3px solid #d79a2b; }
.doc-fail { border-left: 3px solid #d7483b; }

/* ===== 🌍 Remote access ===== */
#ra-view { margin-top: 2px; }
.ra-idle, .ra-warn, .ra-live { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius-sm); padding: 15px 17px; font-size: 13px; line-height: 1.55; box-shadow: var(--nb-card-shadow); }
.ra-idle { background: var(--block-background-fill); color: var(--body-text-color-subdued); }
.ra-warn { background: #fdf3e7; border-color: #ecc9a3; color: #7a4a12; }
.dark .ra-warn { background: #332516; border-color: #5a4425; color: #e7c79b; }
.ra-live { background: var(--block-background-fill); display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px; }
.ra-badge { font-weight: 800; font-size: 13.5px; color: #4f6318; }
.ra-qr { width: 190px; height: 190px; border-radius: 14px; border: 1px solid var(--border-color-primary); background: #fff; padding: 8px; }
.ra-scan { font-size: 13px; color: var(--body-text-color); }
.ra-url { font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: #6b8f12; word-break: break-all; }
.ra-note { font-size: 11.5px; color: var(--body-text-color-subdued); max-width: 380px; }
.ra-warn code, .ra-note code, .ra-idle code { background: var(--color-accent-soft); padding: 1px 5px; border-radius: 5px; font-size: 11px; }

/* ===== 🐉 Kali section ===== */
#kali-wrap { max-width: 1180px; margin: 0 auto; width: 100%; gap: 12px !important; }
#kali-head { align-items: center; }
#kali-title, #kali-title * { margin: 0 !important; font-size: 18px; }
#kali-status, #kali-status p { font-size: 13px; margin: 0 !important; }
.kali-acc { border: 1px solid var(--border-color-primary) !important; border-radius: var(--nb-radius-sm) !important; background: var(--block-background-fill) !important; }
.kali-acc > .label-wrap { padding: 12px 17px !important; font-weight: 700; font-size: 13.5px; }
.kali-acc [data-testid="accordion-content"] { padding: 2px 16px 14px !important; }
.kali-acc input { font-size: 14px !important; }
.kali-acc .gr-button { align-self: flex-end; }
#kali-main { gap: 14px !important; align-items: stretch; }
#kali-term-col, #kali-ref-col { gap: 12px !important; }
#kali-term { background: #0c0a07; border: 1px solid #2c2620 !important; border-radius: var(--nb-radius); padding: 0 !important;
  overflow: hidden; gap: 0 !important; box-shadow: 0 12px 34px rgba(10,14,24,.18); }
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
#kali-ai { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius-sm); padding: 14px 15px !important;
  background: var(--block-background-fill); gap: 10px !important; box-shadow: var(--nb-card-shadow); }
#kali-ai .block { border: none !important; background: transparent !important; padding: 0 !important; }
#kali-ai-label, #kali-ai-label * { font-size: 13px; margin: 0 !important; color: var(--body-text-color); }
#kali-ai-in textarea { font-size: 14px !important; border-radius: 10px !important; }
#kali-ai .gr-button { white-space: nowrap; }
#kali-connect { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius-sm); padding: 0 !important;
  background: var(--block-background-fill); gap: 0 !important; overflow: hidden; box-shadow: var(--nb-card-shadow); }
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
#kali-ref { border: 1px solid var(--border-color-primary); border-radius: var(--nb-radius); padding: 0 !important;
  background: var(--block-background-fill); gap: 0 !important; overflow: hidden; box-shadow: var(--nb-card-shadow); }
#kali-ref .block { border: none !important; background: transparent !important; }
#kali-ref-title { padding: 0 !important; }
.ref-head { display: flex; align-items: center; gap: 9px; padding: 14px 17px; background: var(--color-accent-soft);
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
   🐉 KALI OS — immersive dark theme (scoped to #kali-wrap only)
   ============================================================ */
#kali-wrap {
  --k-bg: #0a0e17; --k-panel: #111726; --k-field: #0c1322; --k-border: #1f2b40;
  --k-text: #cdd9ea; --k-mut: #7e8ca5; --k-head: #eaf2ff; --k-term: #9bf0b0;
  --nb-accent: #4d8bff; --nb-accent-hover: #2f6fe0;
  max-width: none !important; width: 100%; color: var(--k-text);
  background:
    radial-gradient(1100px 520px at 78% -12%, #16254486 0%, #0a0e1700 60%),
    linear-gradient(180deg, #0c1322 0%, #0a0e17 100%);
  border: 1px solid var(--k-border); border-radius: 22px;
  padding: 18px 18px 22px !important; min-height: calc(100dvh - 128px);
  box-shadow: 0 18px 60px rgba(4,10,24,.35);
}
#kali-wrap #kali-head { position: relative; padding-bottom: 2px; }
#kali-wrap #kali-title, #kali-wrap #kali-title * { color: var(--k-head) !important; }
#kali-wrap #kali-status, #kali-wrap #kali-status p { color: var(--k-mut) !important; }
#kali-wrap #kali-status strong { color: var(--k-text) !important; }
#kali-wrap #kali-status code, #kali-wrap #kali-connect-hint code, #kali-wrap #kali-ref-view code {
  background: var(--k-field) !important; color: #86e7ff !important; border: 1px solid var(--k-border) !important; }
#kali-wrap #kali-connect, #kali-wrap #kali-ref, #kali-wrap #kali-ai {
  background: var(--k-panel) !important; border: 1px solid var(--k-border) !important;
  box-shadow: 0 10px 34px rgba(3,8,20,.45) !important; }
#kali-wrap .ref-head { background: linear-gradient(90deg, #16284a, #0f1a34) !important;
  border-bottom: 1px solid var(--k-border) !important; }
#kali-wrap .ref-head, #kali-wrap .ref-head * { color: var(--k-head) !important; }
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
#kali-wrap #kali-term { border-color: #233250 !important;
  box-shadow: 0 0 0 1px #233250, 0 14px 46px rgba(20,60,130,.22) !important; }
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
  .tabs [role="tab"] { padding: 8px 13px !important; font-size: 13px; }
  #chat .bot, #chat .bot.message { font-size: 15.5px; }
  .admin-card { min-height: auto; }
}
@media (max-width: 600px) {
  .badge { font-size: 11px; padding: 4px 9px; }
  .hide-sm { display: none !important; }
  #chat .placeholder-content h3 { font-size: 33px; }
  #composer textarea { font-size: 16px !important; }
}
@media (hover: none) { #modes label, #examples button { -webkit-tap-highlight-color: transparent; } }

/* ===== desktop polish ===== */
@media (min-width: 901px) {
  #topbar { min-height: 30px !important; padding: 2px 0 0 !important; }
  .tabs .tab-wrapper { margin: 2px 0 14px !important; }
  #modes .wrap { flex-wrap: wrap !important; overflow: visible !important; row-gap: 8px !important; }
}
@media (min-width: 1200px) {
  .gradio-container { position: relative; }
  .block:has(#topbar) { position: absolute !important; top: 16px; right: 26px; width: auto !important;
    min-height: 0 !important; padding: 0 !important; margin: 0 !important; z-index: 40; }
  #topbar { min-height: 0 !important; justify-content: flex-end; }
  .tabs .tab-wrapper { margin: 6px 0 16px !important; }
}

/* ===== mobile: make ALL tabs reachable ===== */
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
  #composer .submit-button, #composer .stop-button { width: 42px !important; height: 42px !important; }
}

/* ===== hard overrides: force pill colours over Gradio component defaults ===== */
#modes .wrap label, #modes label {
  background: rgba(255,255,255,.72) !important; color: var(--body-text-color) !important;
  border: 1px solid var(--border-color-primary) !important; }
.dark #modes .wrap label, .dark #modes label { background: rgba(32,35,38,.6) !important; }
#modes .wrap label.selected, #modes label.selected {
  background: var(--nb-ink) !important; border-color: var(--nb-ink) !important; color: #fff !important; }
.dark #modes .wrap label.selected, .dark #modes label.selected { color: #141514 !important; }
.tabs .tab-container button[role="tab"].selected, .tabs [role="tab"].selected {
  background: var(--nb-ink) !important; color: #fff !important; border-color: var(--nb-ink) !important; }
.dark .tabs .tab-container button[role="tab"].selected, .dark .tabs [role="tab"].selected { color: #141514 !important; }
#term-shell .wrap label.selected, #term-shell label.selected {
  background: var(--nb-accent-bright) !important; color: #141514 !important; border-color: var(--nb-accent-bright) !important; }

/* ============================ UI v2 — clean-up layer ============================ */
/* Status badges used to float over the tab bar; the same info is in the sidebar footer. */
.block:has(> #topbar), .block:has(#topbar) { display: none !important; }

/* Tab bar: one tidy row that scrolls instead of clipping */
.tabs .tab-container { flex-wrap: nowrap !important; overflow-x: auto !important; scrollbar-width: none; }
.tabs .tab-container::-webkit-scrollbar { display: none; }
.tabs [role="tab"] { white-space: nowrap; flex: 0 0 auto; }

/* Chat: centred reading column, like modern chat apps */
#chat-col { max-width: 900px !important; margin: 0 auto !important; }
#chat .message-wrap { gap: 10px !important; }
#chat .bot .prose, #chat .bot.message { font-size: 15.5px; line-height: 1.62; }
#chat pre { border-radius: 12px !important; }

/* Mode description + reply language share one slim line */
#mode-row { align-items: center !important; flex-wrap: nowrap !important; gap: 10px !important; margin-top: -4px; }
#mode-row > div:has(#mode-info), #mode-row > #mode-info { flex: 1 1 auto !important; min-width: 0 !important; }
#mode-info { margin: 0 !important; }
#reply-lang { flex: 0 0 176px !important; min-width: 176px !important; max-width: 176px !important;
  border: 1px solid var(--border-color-primary) !important; border-radius: 999px !important;
  padding: 0 4px !important; background: var(--block-background-fill) !important; overflow: visible !important; }
#reply-lang .wrap, #reply-lang .wrap-inner, #reply-lang .secondary-wrap { border: none !important; box-shadow: none !important;
  background: transparent !important; min-height: 30px !important; }
#reply-lang input { font-size: 12.5px !important; height: 30px !important; padding: 0 8px !important; font-weight: 600; }
#reply-lang .info, #reply-lang [data-testid="block-info"] { display: none !important; }

/* Image upload: tucked away behind the paperclip until needed */
#img-in { display: none !important; }
body.nb-attach #img-in { display: block !important; }
#composer-row { align-items: flex-end !important; gap: 8px !important; flex-wrap: nowrap !important; }
#composer-row > div:has(textarea), #composer-row > .block { flex: 1 1 auto !important; min-width: 0 !important; }
#attach-btn { flex: 0 0 44px !important; min-width: 44px !important; width: 44px !important; height: 44px !important;
  border-radius: 50% !important; padding: 0 !important; font-size: 18px !important; margin-bottom: 6px;
  border: 1px solid var(--border-color-primary) !important; background: var(--block-background-fill) !important; }
body.nb-attach #attach-btn { border-color: var(--nb-accent, #b7e23c) !important; }
#examples { opacity: .9; }

/* Floating voice tools: smaller and out of the way */
#nb-tools { right: 12px !important; bottom: 92px !important; gap: 6px !important; }
#nb-tools button { width: 36px !important; height: 36px !important; font-size: 15px !important; }
#nb-tools #nb-vizhi { width: 50px !important; height: 50px !important; font-size: 22px !important; }

/* ---------------- Kali tab: one clean surface, big desktop ---------------- */
#kali-wrap { max-width: none !important; }
#kali-desk { position: relative; border: none !important; padding: 0 !important; margin: 0 0 8px !important;
  background: transparent !important; box-shadow: none !important; }
#kali-desk > .styler, #kali-desk .styler { background: transparent !important; border: none !important; box-shadow: none !important; }
#kali-desk-txt { padding: 2px 2px 6px !important; }
#kali-desk-txt .kd-ico { font-size: 20px !important; }
#kali-desk-txt .kd-title { font-size: 14px !important; }
#kali-desk-txt .kd-sub { display: none !important; }
#kali-desk-actions { position: absolute !important; right: 0; top: -4px; width: auto !important; margin: 0 !important;
  gap: 6px !important; background: transparent !important; z-index: 3; }
#kali-desk-reload, #kali-desk-full { min-height: 30px !important; height: 30px !important; font-size: 12px !important;
  border-radius: 8px !important; padding: 0 12px !important; }
#kali-desk-frame { margin-top: 0 !important; padding: 0 !important; }
.kdesk-frame { height: calc(100dvh - 168px) !important; min-height: 500px !important; border-radius: 12px !important;
  border: 1px solid rgba(43,212,189,.35) !important; }
.kdesk-hint { display: none !important; }
#kali-desk-status { margin: 4px 2px 0 !important; font-size: 12px !important; opacity: .8; }
@media (max-width: 860px) { .kdesk-frame { height: 62dvh !important; min-height: 380px !important; } }

/* v2 nits */
#reply-lang { height: 34px !important; min-height: 34px !important; padding: 0 2px !important; align-self: center !important; }
#reply-lang > *, #reply-lang .container, #reply-lang label { padding: 0 !important; margin: 0 !important; min-height: 0 !important; }
#reply-lang .wrap { min-height: 32px !important; height: 32px !important; padding: 0 6px !important; }
#kali-desk-actions { right: 2px !important; top: -2px !important; width: max-content !important; max-width: 60% !important;
  flex-wrap: nowrap !important; justify-content: flex-end !important; }
#kali-desk-actions > * { flex: 0 0 auto !important; }
#kali-desk-reload, #kali-desk-full { min-width: max-content !important; white-space: nowrap !important; }

/* =====================================================================================
   UI v3 — "NEXUS" look: left navigation, glass panels, neon teal→violet accent, mono HUD
   ===================================================================================== */
:root, .gradio-container {
  --nx-a: #0fb5a6; --nx-b: #6d5cf5; --nx-line: rgba(30,45,90,.13); --nx-panel: rgba(255,255,255,.72);
  --nx-solid: #ffffff; --nx-side: rgba(250,251,253,.9); --nx-dim: #6b7487; --nx-hover: rgba(40,60,120,.06);
  --nx-mono: "JetBrains Mono", "Cascadia Code", "Cascadia Mono", Consolas, ui-monospace, monospace;
}
.dark, .dark .gradio-container, body.dark {
  --nx-a: #2ee6d6; --nx-b: #7c6cff; --nx-line: rgba(125,160,255,.14); --nx-panel: rgba(13,19,34,.66);
  --nx-solid: #0b1120; --nx-side: rgba(7,11,21,.9); --nx-dim: #8b98b3; --nx-hover: rgba(125,160,255,.08);
  --body-background-fill: #060912 !important; --background-fill-primary: #0a101d !important;
  --background-fill-secondary: #0c1322 !important; --block-background-fill: #0c1322 !important;
  --block-border-color: rgba(125,160,255,.14) !important; --border-color-primary: rgba(125,160,255,.14) !important;
  --input-background-fill: #0a1020 !important; --input-border-color: rgba(125,160,255,.18) !important;
  --body-text-color: #e6edf7 !important; --body-text-color-subdued: #8b98b3 !important;
  --block-label-text-color: #9fb0cc !important; --block-title-text-color: #cfdaf0 !important;
  --button-secondary-background-fill: #111a2d !important; --button-secondary-background-fill-hover: #17223a !important;
  --button-secondary-border-color: rgba(125,160,255,.18) !important; --button-secondary-text-color: #dbe6f7 !important;
  --button-primary-background-fill: linear-gradient(135deg, #2ee6d6, #7c6cff) !important;
  --button-primary-background-fill-hover: linear-gradient(135deg, #63f1e5, #978bff) !important;
  --button-primary-text-color: #04121a !important; --button-primary-border-color: transparent !important;
  --color-accent: #2ee6d6 !important; --color-accent-soft: rgba(46,230,214,.12) !important;
  --nb-accent: #2ee6d6; --nb-accent-bright: #2ee6d6; --nb-ink: #e6edf7; --nb-user-bg: rgba(124,108,255,.18);
  --code-background-fill: #070b15 !important; --table-even-background-fill: #0c1322 !important;
  --table-odd-background-fill: #0a101d !important; --panel-background-fill: #0c1322 !important;
}

/* deep-space canvas with a faint engineering grid */
.dark .gradio-container, body.dark, .dark gradio-app {
  background:
    radial-gradient(900px 520px at 88% -8%, rgba(124,108,255,.17), transparent 62%),
    radial-gradient(760px 520px at -6% 106%, rgba(46,230,214,.12), transparent 62%),
    linear-gradient(rgba(125,160,255,.034) 1px, transparent 1px) 0 0 / 100% 38px,
    linear-gradient(90deg, rgba(125,160,255,.034) 1px, transparent 1px) 0 0 / 38px 100%,
    #060912 !important;
  background-attachment: fixed !important;
}
* { scrollbar-width: thin; scrollbar-color: rgba(125,160,255,.28) transparent; }
::selection { background: rgba(46,230,214,.3); }

/* ---------- no menus on top: the tab bars live off-screen, the sidebar drives them ---------- */
.tabs > .tab-wrapper { position: absolute !important; left: -12000px !important; top: 0 !important; width: 5000px !important;
  height: 1px !important; overflow: hidden !important; opacity: 0 !important; pointer-events: none !important; margin: 0 !important; }
#modes, .block:has(> #modes) { display: none !important; }
#hist-pick, #hist-go, .block:has(> #hist-pick) { display: none !important; }
#viz-in, #viz-go, #viz-out, #viz-say, .block:has(> #viz-in), .block:has(> #viz-out), .block:has(> #viz-say) { display: none !important; }

/* ---------- sidebar ---------- */
.sidebar-parent .sidebar { background: var(--nx-side) !important; border-right: 1px solid var(--nx-line) !important;
  backdrop-filter: blur(16px) saturate(1.2); }
.sidebar .sidebar-content { overflow-y: auto !important; padding: 16px 12px 12px !important; }
.sidebar .sidebar-content > .column { gap: 2px !important; }
.sidebar .block:has(.nb-sec-title), .sidebar .block:has(#nb-hist), #nb-nav-wrap, #nb-hist-wrap, #nb-hist-head, #nb-ws-head {
  border: none !important; background: transparent !important; padding: 0 !important; margin: 0 !important;
  box-shadow: none !important; min-height: 0 !important; overflow: visible !important; }
#brand .name { font-family: var(--nx-mono) !important; letter-spacing: .14em; text-transform: uppercase; font-size: 15px !important;
  background: linear-gradient(90deg, var(--nx-a), var(--nx-b)); -webkit-background-clip: text; background-clip: text; color: transparent !important; }
#brand .sub { font-family: var(--nx-mono); font-size: 10.5px !important; letter-spacing: .06em; color: var(--nx-dim) !important; }
#brand img { box-shadow: 0 0 0 1px rgba(46,230,214,.35), 0 6px 22px rgba(46,230,214,.22) !important; }
#new-chat { height: 40px !important; border-radius: 12px !important; font-family: var(--nx-mono) !important; font-size: 12.5px !important;
  letter-spacing: .06em; border: 1px solid transparent !important; color: var(--body-text-color) !important;
  background: linear-gradient(var(--nx-solid), var(--nx-solid)) padding-box,
              linear-gradient(120deg, var(--nx-a), var(--nx-b)) border-box !important;
  transition: box-shadow .2s, transform .12s; margin-bottom: 4px; }
#new-chat:hover { box-shadow: 0 0 22px rgba(46,230,214,.22); transform: translateY(-1px); }
.nb-sec-title { font: 600 10px var(--nx-mono); letter-spacing: .2em; color: var(--nx-dim); padding: 14px 8px 6px;
  display: flex; justify-content: space-between; align-items: center; text-transform: uppercase; }
.nb-sec-title span { letter-spacing: .08em; opacity: .7; text-transform: none; }

#nb-nav { display: flex; flex-direction: column; gap: 2px; }
.nbn-item { position: relative; display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 10px;
  cursor: pointer; font-size: 13.5px; font-weight: 600; color: var(--body-text-color); user-select: none;
  transition: background .15s, box-shadow .15s, transform .12s; }
.nbn-item:hover { background: var(--nx-hover); transform: translateX(2px); }
.nbn-item.active { background: linear-gradient(90deg, rgba(46,230,214,.16), rgba(124,108,255,.07));
  box-shadow: inset 0 0 0 1px rgba(46,230,214,.26); }
.nbn-item.active::before { content: ""; position: absolute; left: -7px; top: 9px; bottom: 9px; width: 3px; border-radius: 3px;
  background: linear-gradient(var(--nx-a), var(--nx-b)); box-shadow: 0 0 12px var(--nx-a); }
.nbn-ico { width: 20px; text-align: center; font-size: 15px; line-height: 1; filter: saturate(.9); }
.nbn-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nbn-chev { margin-left: auto; font-size: 11px; opacity: .5; padding: 3px 5px; border-radius: 6px; transition: transform .2s, opacity .15s; }
.nbn-chev:hover { opacity: 1; background: var(--nx-hover); }
.nbn-item.open .nbn-chev { transform: rotate(180deg); }
.nbn-sub { display: none; margin: 2px 0 6px 19px; padding-left: 9px; border-left: 1px dashed var(--nx-line); }
.nbn-sub.open { display: block; animation: nbIn .2s ease both; }
.nbn-subitem { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: 8px; font-size: 12.5px;
  color: var(--nx-dim); cursor: pointer; transition: background .15s, color .15s; }
.nbn-subitem:hover { color: var(--body-text-color); background: var(--nx-hover); }
.nbn-subitem.active { color: var(--nx-a); background: rgba(46,230,214,.09); font-weight: 600; }
.nbn-sico { width: 16px; text-align: center; font-size: 12.5px; }

#nb-hist { max-height: 26vh; overflow-y: auto; padding-right: 2px; }
.nbh-group { font: 600 9.5px var(--nx-mono); letter-spacing: .14em; color: var(--nx-dim); padding: 8px 8px 3px; text-transform: uppercase; opacity: .75; }
.nbh-item { display: flex; align-items: center; gap: 6px; padding: 6px 8px; border-radius: 8px; font-size: 12.5px; cursor: pointer;
  color: var(--body-text-color); opacity: .84; transition: background .15s, opacity .15s; }
.nbh-item:hover { background: var(--nx-hover); opacity: 1; }
.nbh-item.active { background: rgba(124,108,255,.15); box-shadow: inset 0 0 0 1px rgba(124,108,255,.3); opacity: 1; }
.nbh-title { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nbh-del { opacity: 0; font-size: 10.5px; padding: 2px 6px; border-radius: 6px; transition: opacity .15s, background .15s; }
.nbh-item:hover .nbh-del { opacity: .55; }
.nbh-del:hover { opacity: 1 !important; background: rgba(255,90,90,.18); color: #ff8f8f; }
.nbh-empty { font-size: 12px; color: var(--nx-dim); padding: 4px 8px 8px; line-height: 1.5; }

.sidebar .gr-accordion > .label-wrap { font-size: 13px !important; border-radius: 10px !important; }
#status { font-family: var(--nx-mono) !important; font-size: 10.5px !important; letter-spacing: .02em; }
#status code { background: rgba(46,230,214,.08) !important; color: var(--nx-a) !important; border: 1px solid rgba(46,230,214,.2); border-radius: 6px; }

/* ---------- chat ---------- */
.tabitem { padding-top: 6px !important; }
#chat-col { max-width: 920px !important; gap: 10px !important; }
#mode-row { padding: 7px 8px 7px 12px !important; border: 1px solid var(--nx-line) !important; border-radius: 14px !important;
  background: var(--nx-panel) !important; backdrop-filter: blur(12px); margin: 0 !important; }
#mode-info p { margin: 0 !important; display: flex; align-items: center; gap: 10px; min-width: 0; }
.nb-mode-chip { font: 600 11.5px var(--nx-mono); letter-spacing: .04em; padding: 4px 10px; border-radius: 999px; white-space: nowrap;
  color: var(--nx-a); background: rgba(46,230,214,.1); border: 1px solid rgba(46,230,214,.26); }
.nb-mode-about { color: var(--nx-dim); font-size: 12.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
#reply-lang { font-family: var(--nx-mono) !important; background: var(--nx-solid) !important; border-color: var(--nx-line) !important; }
#reply-lang input { font-family: var(--nx-mono) !important; font-size: 11.5px !important; }

@keyframes nbIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes nbFloat { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
#chat .message-row { animation: nbIn .26s ease both; }
#chat .bot-row .bot { position: relative; padding: 2px 0 2px 18px !important; }
#chat .bot-row .bot::before { content: ""; position: absolute; left: 0; top: 7px; bottom: 7px; width: 2px; border-radius: 2px;
  background: linear-gradient(var(--nx-a), var(--nx-b)); opacity: .8; }
#chat .user.message, #chat .user { border-radius: 16px 16px 4px 16px !important; padding: 10px 15px !important; }
.dark #chat .user.message, .dark #chat .user {
  background: linear-gradient(135deg, rgba(124,108,255,.24), rgba(46,230,214,.12)) !important;
  border: 1px solid rgba(124,108,255,.36) !important; box-shadow: 0 8px 26px rgba(124,108,255,.13); }
#chat pre { background: #070b15 !important; border: 1px solid var(--nx-line) !important; border-radius: 12px !important; }
#chat pre code, #chat code { font-family: var(--nx-mono) !important; font-size: 12.8px !important; }
#chat .bot :not(pre) > code { color: var(--nx-a) !important; background: rgba(46,230,214,.09) !important;
  border: 1px solid rgba(46,230,214,.18); border-radius: 6px; padding: 1px 6px; }
#chat .bot a { color: var(--nx-a) !important; }
#chat .bot table { border: 1px solid var(--nx-line) !important; border-radius: 10px; overflow: hidden; }
#chat .message-buttons button, #chat .icon-button { opacity: .45; transition: opacity .15s; }
#chat .message-buttons:hover button, #chat .icon-button:hover { opacity: 1; }

/* empty state */
.nb-hero { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 7vh 0 2vh; text-align: center; }
.nb-hero-orb { width: 86px; height: 86px; border-radius: 26px; display: grid; place-items: center; color: #04121a;
  font: 800 30px var(--nx-mono); background: linear-gradient(135deg, var(--nx-a), var(--nx-b));
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.18), 0 18px 60px rgba(46,230,214,.3), 0 0 90px rgba(124,108,255,.28);
  animation: nbFloat 5s ease-in-out infinite; }
.nb-hero-title { font: 800 30px/1 var(--nx-mono); letter-spacing: .34em; padding-left: .34em;
  background: linear-gradient(90deg, var(--nx-a), var(--nx-b)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.nb-hero-sub { color: var(--nx-dim); font-size: 14.5px; }
.nb-hero-stats { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 4px; }
.nb-hero-stats span { font: 500 10.5px var(--nx-mono); letter-spacing: .06em; padding: 5px 11px; border-radius: 999px;
  border: 1px solid var(--nx-line); color: var(--nx-dim); background: var(--nx-panel); }
.nb-hero-stats span:first-child { color: var(--nx-a); border-color: rgba(46,230,214,.3); }

/* composer: glass capsule with a neon edge */
.dark #composer { background: linear-gradient(to bottom, transparent, rgba(6,9,18,.92) 42%) !important; }
#composer-row > div:has(textarea), #composer-row > .block { border-radius: 18px !important; border: 1px solid transparent !important;
  background: linear-gradient(var(--nx-solid), var(--nx-solid)) padding-box,
              linear-gradient(120deg, rgba(46,230,214,.6), rgba(124,108,255,.6)) border-box !important;
  box-shadow: 0 12px 44px rgba(0,0,0,.28); transition: box-shadow .25s; }
#composer-row > div:has(textarea):focus-within { box-shadow: 0 12px 44px rgba(0,0,0,.3), 0 0 30px rgba(46,230,214,.2); }
#composer textarea { font-size: 15px !important; }
#composer textarea::placeholder { font-family: var(--nx-mono); font-size: 12.5px; opacity: .55; letter-spacing: .02em; }
#composer .submit-button { background: linear-gradient(135deg, var(--nx-a), var(--nx-b)) !important; color: #04121a !important;
  box-shadow: 0 4px 18px rgba(46,230,214,.36); border: none !important; }
#composer .submit-button:hover { background: linear-gradient(135deg, #63f1e5, #978bff) !important; transform: translateY(-1px) scale(1.04); }
#attach-btn { background: var(--nx-panel) !important; border: 1px solid var(--nx-line) !important; backdrop-filter: blur(8px);
  transition: border-color .15s, box-shadow .15s; }
#attach-btn:hover { border-color: var(--nx-a) !important; box-shadow: 0 0 16px rgba(46,230,214,.2); }
#examples button, #examples .gallery-item { border-radius: 999px !important; border: 1px solid var(--nx-line) !important;
  background: var(--nx-panel) !important; font-size: 12px !important; color: var(--nx-dim) !important; transition: all .15s; }
#examples button:hover, #examples .gallery-item:hover { color: var(--body-text-color) !important; border-color: rgba(46,230,214,.4) !important; }

/* floating voice tools */
#nb-tools button { background: var(--nx-panel) !important; border: 1px solid var(--nx-line) !important; backdrop-filter: blur(8px); }
#nb-tools #nb-vizhi { box-shadow: 0 0 0 1px rgba(46,230,214,.4), 0 8px 30px rgba(46,230,214,.3) !important; }

/* generic surfaces in the other sections pick up the same glass language */
.dark .block { border-color: var(--nx-line); }
.dark input:focus, .dark textarea:focus { border-color: rgba(46,230,214,.5) !important; }
.dark button.primary, .dark .primary.svelte-xzq5jh { font-weight: 700 !important; }
.dark .tabitem h1, .dark .tabitem h2, .dark .tabitem h3 { letter-spacing: -.01em; }

/* v3 nits */
#brand .name, .nb-hero-title { background: none !important; -webkit-text-fill-color: currentColor !important;
  color: var(--nx-a) !important; text-shadow: 0 0 22px rgba(46,230,214,.45); }
.nb-hero-title { font-size: 28px !important; }
#composer #composer-row > .block, #composer #composer-row > div:has(textarea) {
  border-radius: 18px !important; border: 1px solid transparent !important;
  background: linear-gradient(var(--nx-solid), var(--nx-solid)) padding-box,
              linear-gradient(120deg, rgba(46,230,214,.6), rgba(124,108,255,.6)) border-box !important; }
#composer #composer-row .input-container, #composer #composer-row label, #composer #composer-row textarea {
  background: transparent !important; }
#reply-lang .icon-wrap, #reply-lang svg { right: 8px !important; }

/* =====================================================================================
   UI v4 — alignment / spacing fixes found in the full-page audit of every section
   ===================================================================================== */
/* 1. Chat: replies were wider than their column (padding on top of width:100%) and got cut off on the right */
#chat .message-row, #chat .bot-row .flex-wrap, #chat .bot-row .bot { box-sizing: border-box !important; max-width: 100% !important; min-width: 0 !important; }
#chat .bot-row .bot { width: 100% !important; }
#chat .bot .message, #chat .bot .message-content, #chat .bot .prose, #chat .bot .md {
  max-width: 100% !important; min-width: 0 !important; overflow-wrap: anywhere; box-sizing: border-box !important; }
#chat pre { max-width: 100% !important; overflow-x: auto !important; white-space: pre; }
#chat .bot table { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
#chat .bot th, #chat .bot td { padding: 7px 12px !important; border-color: var(--nx-line) !important; }
#chat .bot th { background: rgba(46,230,214,.07) !important; font-family: var(--nx-mono); font-size: 12px; letter-spacing: .03em; }
#chat .bot hr { border: none !important; border-top: 1px solid var(--nx-line) !important; margin: 14px 0 !important; }
#chat .bot ol, #chat .bot ul { padding-left: 22px !important; }
#chat .bot li { margin: 4px 0 !important; }
/* 2. Chat fills the window now that the top bars are gone (was leaving ~200px empty at the bottom) */
#chat { height: calc(100dvh - 232px) !important; min-height: 300px !important; }
/* 3. The floating voice buttons must never sit on top of page content */
.tabitem > .column { padding-right: 60px !important; box-sizing: border-box !important; }
@media (max-width: 900px) { .tabitem > .column { padding-right: 0 !important; } }

/* 4. Sidebar: one type scale + one left edge for every row */
.sidebar .gr-accordion > .label-wrap { padding: 8px 10px !important; min-height: 0 !important; }
.sidebar .gr-accordion > .label-wrap > span, .sidebar .gr-accordion > .label-wrap span:first-child {
  font-size: 13.5px !important; font-weight: 600 !important; }
.sidebar .gr-accordion { margin: 0 !important; }
#status { padding: 10px 8px 0 !important; }
#status p { line-height: 1.95 !important; }
#status code { font-size: 9.5px !important; padding: 1px 5px !important; white-space: nowrap; letter-spacing: 0; }

/* 5. Cards (Security / Admin / India Lab): Gradio paints a Group's backdrop with the border colour,
      which showed as a slate box with text glued to its edge */
.dark .gr-group, .dark .gr-group > .styler, .dark .admin-card > .styler { background: transparent !important; }
.admin-card { padding: 16px 18px !important; border-radius: 16px !important; background: var(--nx-panel) !important;
  border: 1px solid var(--nx-line) !important; }
.admin-card > .styler { display: flex !important; flex-direction: column !important; gap: 10px !important; }
.admin-card .row { gap: 8px !important; }
.admin-card h4 { font-size: 14.5px !important; margin: 0 0 2px !important; }
#lesson-reader { padding: 4px 2px 2px !important; }
#lesson-reader h1 { font-size: 1.45rem !important; line-height: 1.25 !important; margin: 10px 0 8px !important; }
#lesson-reader h2 { font-size: 1.12rem !important; margin: 16px 0 6px !important; color: var(--nx-a); }

/* 6. Buttons inside sections were flat, square and ~20px tall */
.tabitem button.primary, .tabitem button.secondary, .tabitem button.stop {
  border-radius: 10px !important; min-height: 36px !important; }
.tabitem .row:has(> button) { gap: 8px !important; }
#kali-power-btns { gap: 8px !important; }

/* 7. Kali: AI Shell row — input and Run button on one baseline */
#kali-ai .row { align-items: center !important; gap: 8px !important; }
#kali-ai-run { min-height: 40px !important; height: 40px !important; align-self: center !important; }

/* 8. Terminal: same glass + navy language as the rest (was a grey card from the old theme) */
.dark #term-card { background: var(--nx-panel) !important; border: 1px solid var(--nx-line) !important; backdrop-filter: blur(10px); }
.dark #term-out textarea { background: #05080f !important; border: 1px solid var(--nx-line) !important; }
.dark #term-in textarea, .dark #term-in input { background: #0a1020 !important; border: 1px solid var(--nx-line) !important; border-radius: 10px !important; }
.dark #term-cwd code { background: rgba(46,230,214,.08) !important; color: var(--nx-a) !important; }
.dark #term-card #explain-btn { background: #111a2d !important; border: 1px solid var(--nx-line) !important; color: #dbe6f7 !important; }

/* 9. Images: prompt box edge matches the theme */
#img-prompt textarea { border: 1px solid var(--nx-line) !important; box-shadow: none !important; border-radius: 12px !important; }
#img-prompt textarea:focus { border-color: rgba(46,230,214,.5) !important; }

/* 10. India Lab hero was a white card with washed-out text in the dark theme */
.dark .il-hero { background: linear-gradient(135deg, rgba(46,230,214,.10), rgba(124,108,255,.13)), #0c1322 !important;
  border: 1px solid var(--nx-line) !important; color: #e6edf7 !important; box-shadow: 0 18px 60px rgba(0,0,0,.35) !important; }
.dark .il-hero h1 { color: #eef3fb !important; }
.dark .il-hero p { color: #a9b8d2 !important; }
.dark .il-hero p b, .dark .il-hero p strong, .dark .il-hero p span, .dark .il-hero p em { color: var(--nx-a) !important; background: none !important; }
.dark .il-hero .il-safe { color: #f2cd92 !important; background: rgba(255,176,138,.09) !important; border-color: rgba(255,176,138,.28) !important; }
.dark .il-hero-badge { color: var(--nx-a) !important; background: rgba(46,230,214,.10) !important; border: 1px solid rgba(46,230,214,.3) !important; }

/* ===================== UI v5 — India Lab LIVE ARSENAL ===================== */
#il-arsenal { border: 1px solid rgba(46,230,214,.3) !important; border-radius: 16px !important; padding: 14px 16px !important;
  background: linear-gradient(135deg, rgba(46,230,214,.07), rgba(124,108,255,.09)), var(--nx-panel, #0c1322) !important;
  margin: 8px 0 14px !important; box-shadow: 0 10px 40px rgba(0,0,0,.28); }
.il-ars-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; }
.il-ars-t { font: 800 15px/1 var(--nx-mono, monospace); letter-spacing: .02em; color: #2ee6d6 !important; text-shadow: 0 0 18px rgba(46,230,214,.4); }
.il-ars-live { font: 700 10px var(--nx-mono, monospace); letter-spacing: .12em; color: #2ee6d6;
  padding: 3px 10px; border-radius: 999px; border: 1px solid rgba(46,230,214,.4); background: rgba(46,230,214,.08); animation: ilpulse 2s infinite; }
@keyframes ilpulse { 0%,100% { opacity: 1; } 50% { opacity: .55; } }
#il-top10 { gap: 7px !important; flex-wrap: wrap !important; }
#il-top10 .il-toolbtn { flex: 0 0 auto !important; min-width: max-content !important; border-radius: 10px !important;
  min-height: 34px !important; font-size: 12.5px !important; font-weight: 600 !important; white-space: nowrap;
  background: rgba(10,16,32,.7) !important; border: 1px solid rgba(46,230,214,.22) !important; color: #dbe6f7 !important;
  transition: all .14s; }
#il-top10 .il-toolbtn:hover { border-color: var(--nx-a, #2ee6d6) !important; transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(46,230,214,.22); color: #fff !important; }
#il-domtools { margin-top: 2px !important; }
#il-oprow { gap: 8px !important; margin-top: 10px !important; align-items: center !important; }
#il-op-in textarea { border: 1px solid rgba(124,108,255,.35) !important; border-radius: 11px !important; background: rgba(8,12,24,.8) !important; font-size: 13.5px !important; }
#il-op-run { min-height: 40px !important; height: 40px !important; align-self: center !important; border-radius: 11px !important;
  background: linear-gradient(135deg, var(--nx-a, #2ee6d6), var(--nx-b, #7c6cff)) !important; color: #04121a !important; font-weight: 800 !important; border: none !important; }
#il-labout { margin-top: 10px !important; }
#il-labout textarea { font-family: var(--nx-mono, monospace) !important; font-size: 12.5px !important; line-height: 1.55 !important;
  background: #05080f !important; color: #c8ffe8 !important; border: 1px solid rgba(46,230,214,.22) !important; border-radius: 12px !important;
  height: 300px !important; }
#il-cmdrow { gap: 7px !important; margin-top: 8px !important; align-items: center !important; }
#il-cmd-in textarea { font-family: var(--nx-mono, monospace) !important; font-size: 12.5px !important;
  background: #0a1020 !important; border: 1px solid rgba(46,230,214,.22) !important; border-radius: 10px !important; }
#il-cmd-run, #il-cmd-stop { min-height: 38px !important; height: 38px !important; align-self: center !important; border-radius: 10px !important; }
#il-autofix { margin-top: 7px !important; font-size: 12px !important; }
#il-autofix label { font-size: 12px !important; color: var(--nx-dim, #8b98b3) !important; }
@media (max-width: 760px) { #il-labout textarea { height: 220px !important; } #il-oprow, #il-cmdrow { flex-wrap: wrap !important; } }
"""

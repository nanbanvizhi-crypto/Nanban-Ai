"""🎨 Images tab — type a prompt, get an AI image. Free, no GPU, no install."""

import gradio as gr

import images

_IDEAS = [
    "a cozy Tamil Nadu filter-coffee shop at sunrise, warm light, cinematic",
    "a futuristic resort reception desk, glass and brass, ultra modern, 3d render",
    "a cute robot mascot named Nanban, friendly, sticker style, white background",
    "a south-indian thali on a banana leaf, top-down, food photography, vivid",
    "a neon cyberpunk city street in the rain, reflections, 4k, highly detailed",
]


def build():
    with gr.Column(elem_id="img-wrap"):
        gr.HTML('<div class="img-hero"><h2>🎨 Nanban Image Studio</h2>'
                '<p>Type what you want to see. Free AI image creation — no GPU, no install. '
                'With a hosted key you get the best models (FLUX 1.1 Pro / SD 3.5); '
                'without one it still makes a great image free.</p></div>')

        prompt = gr.Textbox(
            placeholder="A detailed scene… e.g. 'a golden retriever astronaut on the moon, cinematic, 4k'",
            show_label=False, lines=2, max_lines=5, elem_id="img-prompt", autofocus=True)

        with gr.Row(elem_id="img-controls"):
            size = gr.Radio(choices=list(images.SIZES.keys()), value="⬛ Square 1:1",
                            show_label=False, container=False, scale=3)
            engine = gr.Radio(choices=images.engines(), value=images.engines()[0],
                              show_label=False, container=False, scale=3)

        gen = gr.Button("🎨 Create image", variant="primary", elem_id="img-gen")
        status = gr.Markdown("", elem_id="img-status")
        out = gr.Image(show_label=False, interactive=False, height=460, elem_id="img-out")

        gr.Examples(examples=[[i] for i in _IDEAS], inputs=prompt, label="💡 Try one")

    def _run(p, s, e):
        yield gr.update(), "⏳ Painting your image… (10–30s)"
        path, msg = images.generate(p, s, e)
        if path:
            yield gr.update(value=path), msg
        else:
            yield gr.update(), msg

    gen.click(_run, [prompt, size, engine], [out, status])
    prompt.submit(_run, [prompt, size, engine], [out, status])

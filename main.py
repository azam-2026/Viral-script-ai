"""Mobile-friendly Gradio app for generating short-form video content."""

import os
import re

import gradio as gr
from g4f import Provider
from g4f.client import Client


def generate_ai_text(topic: str) -> str:
    """Ask the keyless public AI provider to create content for a topic."""
    client = Client()
    prompt = f"""
You are a senior short-form video strategist delivering a professional video
blueprint. Create a high-retention 60-second short-form video for:
{topic}

Return exactly these labeled sections:
HOOK 1: <a unique hook>
HOOK 2: <a unique hook>
HOOK 3: <a unique hook>
SCRIPT:
⏱️ 0-5s
[Visual or B-Roll cue] VOICEOVER: <Hinglish line>
⏱️ 5-20s
[Visual or B-Roll cue] VOICEOVER: <Hinglish line>
⏱️ 20-50s
[Visual or B-Roll cue] VOICEOVER: <Hinglish line>
⏱️ 50-60s
[Visual or B-Roll cue] VOICEOVER: <Hinglish line>
CTA:
<one high-CTR call to action>
HASHTAGS:
<exactly 10 targeted hashtags separated by spaces>

Requirements:
1. Write exactly 3 psychological retention hooks using different Pattern
   Interrupt techniques such as a surprising contradiction, open loop, or
   unexpected question. Make each hook meaningfully different.
2. Divide the script into exactly these timestamps: 0-5s, 5-20s, 20-50s,
   and 50-60s.
3. Put at least one specific Visual or B-Roll cue in square brackets inside
   every timestamp scene, such as [Fast Zoom-in], [Text Pop: 100K Views],
   [Show Screen Recording], [Cut to Creator Reaction], or [Split Screen].
4. Make every VOICEOVER line natural, punchy Hinglish designed for high
   retention in a short video. Include a strong opening, useful value, and
   an ending payoff.
5. Make the CTA specific and high-CTR without promising guaranteed results.
6. Include exactly 10 relevant, targeted, non-duplicate hashtags.
7. Use clear headings and tasteful emojis. Do not use markdown code fences or
   add extra sections outside the labels above.
"""

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        provider=Provider.Gemini,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("The AI provider returned an empty response.")
    return content.strip()


def extract_section(text: str, start: str, end: str | None = None) -> str:
    """Extract a labeled section from the AI response."""
    end_pattern = rf"(?=\n\s*{end}\s*:)" if end else r"$"
    match = re.search(
        rf"{start}\s*:\s*(.*?){end_pattern}",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def parse_content(text: str) -> tuple[str, str, str, str, str, str]:
    """Split the AI response into the UI's separate output fields."""
    hooks = [
        extract_section(text, "HOOK 1", "HOOK 2"),
        extract_section(text, "HOOK 2", "HOOK 3"),
        extract_section(text, "HOOK 3", "SCRIPT"),
    ]
    script = extract_section(text, "SCRIPT", "CTA")
    cta = extract_section(text, "CTA", "HASHTAGS")
    hashtag_section = extract_section(text, "HASHTAGS")
    hashtags = re.findall(r"(?<!\w)#[\w\u0080-\uffff]+", hashtag_section)

    if len(hashtags) != 10:
        raise RuntimeError(
            f"The AI returned {len(hashtags)} hashtags instead of exactly 10."
        )
    if not all((*hooks, script, cta)):
        raise RuntimeError(
            "The AI returned an unexpected format. Please try the topic again."
        )
    return (*hooks, script, cta, " ".join(hashtags))


def generate_content(topic: str) -> tuple[str, str, str, str, str, str, str]:
    """Generate content and return it in the UI's output order."""
    topic = topic.strip()
    if not topic:
        return "", "", "", "", "", "", "Enter a topic to generate content."

    try:
        blueprint = parse_content(generate_ai_text(topic))
        return (
            *blueprint,
            "Generated a live professional blueprint with a public AI provider.",
        )
    except Exception as error:
        return (
            "",
            "",
            "",
            "",
            "",
            "",
            f"Generation failed: {error}",
        )


APP_CSS = """
body {
    background: linear-gradient(145deg, #f6f8ff 0%, #fff8f1 100%);
}

.app-shell {
    max-width: 900px;
    margin: 0 auto;
}

.hero {
    text-align: center;
    padding: 12px 0 8px;
}

.hero h1 {
    color: #18213d;
    margin-bottom: 6px;
}

.hero p {
    color: #5f6780;
    margin-top: 0;
}

.generate-button {
    min-height: 48px;
    font-weight: 700;
}

@media (max-width: 640px) {
    .app-shell {
        padding: 0 8px;
    }

    .hero h1 {
        font-size: 1.7rem;
    }
}
"""


with gr.Blocks(
    title="Pro AI Script & Hook Generator",
) as demo:
    with gr.Column(elem_classes="app-shell"):
        gr.Markdown(
            """
            <div class="hero">
              <h1>Professional Video Blueprint</h1>
              <p>Generated a ready-to-record professional video blueprint in seconds.</p>
            </div>
            """
        )

        topic = gr.Textbox(
            label="Video topic",
            placeholder="e.g. YouTube Growth",
            lines=2,
        )
        generate_button = gr.Button(
            "Generate Professional Blueprint",
            variant="primary",
            elem_classes="generate-button",
        )

        status = gr.Markdown()

        with gr.Group():
            gr.Markdown("### 🧠 Psychological Retention Hooks")
            hook_1 = gr.Textbox(label="⚡ Pattern Interrupt Hook 1", lines=2)
            hook_2 = gr.Textbox(label="⚡ Pattern Interrupt Hook 2", lines=2)
            hook_3 = gr.Textbox(label="⚡ Pattern Interrupt Hook 3", lines=2)

        script = gr.Textbox(
            label="🎬 Timestamped Hinglish Voiceover + Visual Blueprint",
            lines=12,
        )
        cta = gr.Textbox(
            label="🎯 High-CTR Call To Action",
            lines=3,
        )
        hashtags = gr.Textbox(
            label="🚀 10 Targeted Viral Hashtags",
            lines=2,
        )

        generate_button.click(
            fn=generate_content,
            inputs=topic,
            outputs=[hook_1, hook_2, hook_3, script, cta, hashtags, status],
        )
        topic.submit(
            fn=generate_content,
            inputs=topic,
            outputs=[hook_1, hook_2, hook_3, script, cta, hashtags, status],
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=port,
        show_error=True,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="orange",
            neutral_hue="slate",
        ),
        css=APP_CSS,
    )

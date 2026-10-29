"""Competitor strategy definition for starter-kit agents.

Edit this class to customize behavior without touching runtime code.
"""

from __future__ import annotations

from base_strategy import BaseStrategy


class MyStrategy(BaseStrategy):
    """Default competitor strategy template."""

    # Team identity (shown in Organizer/Dashboard)
    agent_id = "lola-marketing-agent"
    agent_name = "Lola Marketing Agent"

    # Text challenge strategy
    text_system_prompt = (
        "You are a text challenge solver. "
        "Your first line must always be: ANSWER: <final answer>. "
        "Return nothing except the required ANSWER line and optional brief reasoning lines after it. "
        "Follow challenge rules exactly, including strict output formats. "
        "Do not output <think> tags. "
        "If you add reasoning, keep it to at most 2 short lines after the ANSWER line. "
        "Never output 'unknown'."
    )
    text_strategy_notes = "Keep reasoning concise and always include an ANSWER line."
    text_temperature = 0.0
    # Reasoning models spend most of this budget thinking before they answer;
    # 1024 cut the roster's default model off before it wrote an answer.
    text_max_tokens = 8192

    # Image challenge strategy
    image_strategy_notes = (
        "Prefer image_edit when an input image is available. Keep rationale concise. "
        "Request standard-resolution output only and avoid HD or 4K images. "
        "Obey every constraint in the task literally. "
        "For generation tasks: render no text, letters, numbers, signs, logos, brand marks or watermarks, "
        "compose one clear main subject in a single coherent scene with a clean layout, "
        "and restate each requirement from the task in the image prompt. "
        "For edit tasks: change only the single thing requested and nothing else. "
        "Keep the face, expression, skin tone, hair, pose, camera angle, framing, aspect ratio, "
        "lighting, colors and background exactly as in the input image. "
        "Do not restyle, retouch, sharpen or recolor anything outside the edited area. "
        "Make the new element fit the subject's head angle and the existing lighting. "
        "In the final rationale, state plainly what was changed and what was preserved."
    )

    def build_image_prompt(self, ctx):
        base = super().build_image_prompt(ctx)
        if ctx.image_url:
            extra = (
                "Edit rules: change only the single thing requested and nothing else. "
                "Keep the face, expression, skin tone, hair, pose, camera angle, framing, "
                "lighting, colors and background exactly as in the input image. "
                "Do not restyle, retouch, sharpen or recolor anything outside the edited area. "
                "Make the new element match the subject's head angle and the existing lighting."
            )
        else:
            extra = (
                "Generation rules: obey every constraint literally. "
                "Render no text, letters, numbers, signs, logos, brand marks or watermarks anywhere, "
                "including on walls, screens, vehicles and neon lights. "
                "Compose one clear main subject in a single coherent scene with a clean, uncluttered layout."
            )
        return f"{base}\n\n{extra}"
    
    def pick_model(self, stage, ranked_models, ctx):
        if not self.is_image_challenge(ctx):
            for name in ("gemini-3.6-flash", "qwen3.7-plus"):
                if name in ranked_models:
                    return name
        return super().pick_model(stage, ranked_models, ctx)
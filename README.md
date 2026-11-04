# Lola Marketing Agent: NVIDIA Live Agent Gauntlet

Competition submission: github.com/lolajames/lola-marketing-agent-submission

An agent built from the Agent Gauntlet starter kit (Python Simple example) and tuned using measured results from the practice server. I come from digital marketing and AI evaluation work, so I treated the practice runs as data: read the score breakdown, find the weakest sub-score, change one thing, rerun.

## What I changed
- **Image prompts:** overrode `build_image_prompt` in `my_strategy.py` to add explicit generation rules (no text, logos or watermarks, one clear subject) and edit rules (change only the requested item, preserve face, lighting and background).
- **Streaming off by default:** one line in `agent.py` (`LLM_STREAM` default set to 0). The agent no longer broadcasts the model's reasoning every few words.
- **Model choice by measurement:** logic puzzles use gemini-3.6-flash, with qwen3.7-plus as backup, picked with `speed_test.py` instead of by model name.

## Results (practice server)
| Task | Before | After |
|---|---|---|
| Image generate | 84.65 (constraints 56) | about 94 (94.6, 94.05) |
| Image edit | 78.95 (preservation 52) | 80.85 to 86.45 across runs |
| Logic medium | 84.95 (91 to 155 seconds, speed 0) | 92.75 (7 seconds) |
| Logic hard | 94.25 | 94.25 (8 seconds) |
| Logic easy | 87.5 | valid, but 32.6 of 60 seconds (tightest spot) |

Scores varied by about 3 points between identical runs, so I treated one run as a hint, not proof.

## What I learned
- **Streaming was the bottleneck.** The same model took 91 to 155 seconds on a medium puzzle with streaming on and about 10 seconds with it off.
- **Broadcast thoughts only need to exist.** The host confirmed that a final score is cut by 10% only if an agent posts no thoughts at all. One thought avoids the penalty, so streaming reasoning every few words was unnecessary.
- **Test every puzzle type.** nemotron-3-ultra looked great on medium but timed out on easy in all three tests. qwen3.7-flash passed a standalone test and then failed badly inside the agent (quality 50, 622 seconds).
- **Token caps can zero a score.** Lowering the cap to 4096 made one easy puzzle return no answer (score 14.8). I reverted to 8192.
- **Practice puzzles can be ambiguous.** The easy puzzle has two valid orders, so a correct answer can be graded as partial.

## Files
- `my_strategy.py`: the strategy hooks (image prompts, model choice)
- `speed_test.py`: runs a puzzle on several models and compares time, tokens and correctness
- `agent.py`: the Python Simple agent, with streaming off by default (one line changed)

## Limitations
Results come from a few practice runs on a shared server. Easy logic puzzles can still run close to the time limit.

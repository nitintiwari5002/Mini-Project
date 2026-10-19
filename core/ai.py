import os
import re
from typing import Optional

import requests
import streamlit as st

# Cloud version: the Phi-3 model runs on your Mac through Ollama + FastAPI.
# Configure these in Streamlit Community Cloud -> App -> Settings -> Secrets:
# AI_GATEWAY_URL = "https://your-tunnel-address.trycloudflare.com"
# AI_GATEWAY_KEY = "your-private-secret-key"
#
# For local testing, environment variables with the same names are also supported.

DEFAULT_MAX_NEW_TOKENS = 512
REQUEST_TIMEOUT_SECONDS = 200

MODE_CONFIG = {
    "general": {
        "system": (
            "You are an expert resume writer and career coach. "
            "Give practical, concise, ATS-friendly advice."
        ),
    },
    "questions": {
        "system": (
            "You are an expert interviewer. Follow the user's requested "
            "output format carefully. Generate clear, relevant interview "
            "questions and answers when requested."
        ),
    },
    "analysis": {
        "system": (
            "You are an expert resume reviewer and career coach. "
            "Give structured, concise, actionable feedback."
        ),
    },
}

THINK_BLOCK_PATTERN = re.compile(
    r"<think>.*?</think>",
    flags=re.DOTALL | re.IGNORECASE,
)


def remove_think_blocks(text: str) -> str:
    """Remove reasoning blocks if the model produces them."""
    if not text:
        return ""
    return THINK_BLOCK_PATTERN.sub("", text).strip()


def clean_prompt(text: str) -> str:
    """Normalize input text."""
    if not text:
        return ""
    return str(text).strip()


def _get_gateway_settings():
    """Read gateway URL and key from Streamlit Secrets or environment."""
    try:
        gateway_url = st.secrets.get("AI_GATEWAY_URL", "")
        api_key = st.secrets.get("AI_GATEWAY_KEY", "")
    except Exception:
        # Allows local development when no Streamlit secrets file exists.
        gateway_url = ""
        api_key = ""

    gateway_url = gateway_url or os.getenv("AI_GATEWAY_URL", "")
    api_key = api_key or os.getenv("AI_GATEWAY_KEY", "")

    if not gateway_url or not api_key:
        raise RuntimeError(
            "AI gateway is not configured. Set AI_GATEWAY_URL and "
            "AI_GATEWAY_KEY in Streamlit Community Cloud Secrets."
        )

    return gateway_url.rstrip("/"), api_key


def local_chat(
    user_prompt: str,
    mode: str = "general",
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
) -> str:
    """
    Keep the old function name so existing app pages keep working.
    In this cloud version, prompts are sent to the protected FastAPI gateway.
    """
    user_prompt = clean_prompt(user_prompt)
    if not user_prompt:
        return ""

    config = MODE_CONFIG.get(mode, MODE_CONFIG["general"])
    combined_prompt = (
        f"Instructions:\n{config['system']}\n\n"
        f"User request:\n{user_prompt}"
    )

    gateway_url, api_key = _get_gateway_settings()

    response = requests.post(
        f"{gateway_url}/generate",
        json={"prompt": combined_prompt},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    result = response.json()
    answer = result.get("response", "")
    return remove_think_blocks(answer)


def _safe_chat(
    user_prompt: str,
    mode: str = "general",
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
):
    """Run the remote request and return (text, error), as existing callers expect."""
    try:
        return local_chat(
            user_prompt,
            mode=mode,
            max_new_tokens=max_new_tokens,
        ), None
    except Exception as exc:
        return None, str(exc)


def improve_summary(summary: str):
    summary = clean_prompt(summary)
    if not summary:
        return "", None

    prompt_text = f"""
Improve the following resume summary.

Make it:
- ATS-friendly
- Concise
- Impactful
- Keyword-rich
- Professional
- Specific to the candidate's experience

Do not invent qualifications or experience.

Current summary:
{summary}
"""
    return _safe_chat(prompt_text, mode="general", max_new_tokens=256)


def generate_bullets(role: str, text: str):
    role = clean_prompt(role)
    text = clean_prompt(text)
    if not text:
        return "", None

    prompt_text = f"""
Convert the following experience into strong resume bullet points.

Target role:
{role}

Original experience:
{text}

Rules:
- Start each bullet with a strong action verb.
- Focus on accomplishments rather than responsibilities.
- Quantify impact only when the provided information supports it.
- Never invent metrics.
- Keep bullets concise.
- Make them ATS-friendly.
- Do not number the bullets.
"""
    return _safe_chat(prompt_text, mode="general", max_new_tokens=384)


def resume_score(resume_text: str):
    resume_text = clean_prompt(resume_text)
    if not resume_text:
        return "", None

    prompt_text = f"""
Evaluate the following resume.

Resume:
{resume_text}

Provide:

ATS Score: X/100

Strengths:
- ...

Weaknesses:
- ...

Improvements:
- ...

Evaluate:
- Keyword relevance
- Skills
- Experience
- Achievements
- Formatting and content quality
- ATS compatibility

Do not invent information.
"""
    return _safe_chat(prompt_text, mode="analysis", max_new_tokens=512)


def match_keywords(resume: str, job_desc: str) -> str:
    resume = clean_prompt(resume)
    job_desc = clean_prompt(job_desc)
    if not resume or not job_desc:
        return "", None

    prompt_text = f"""
Compare this resume against this job description.

RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}

Provide:

Missing Keywords:
- ...

Matching Keywords:
- ...

Skills Missing From Resume:
- ...

Suggestions:
- ...

Only recommend keywords that are genuinely relevant to the job.
Do not suggest falsely claiming experience.
"""
    return _safe_chat(prompt_text, mode="analysis", max_new_tokens=512)


def prompt(
    text: str,
    mode: str = "general",
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
):
    """Generic interface used by the rest of InterviewAce; returns (response, error)."""
    return _safe_chat(text, mode=mode, max_new_tokens=max_new_tokens)


def get_model_info() -> dict:
    """Return remote-model details without loading Transformers on Streamlit Cloud."""
    try:
        gateway_url, _ = _get_gateway_settings()
        configured = True
    except Exception:
        gateway_url = ""
        configured = False

    return {
        "device": "Remote Mac via Ollama",
        "dtype": "Managed by Ollama",
        "model_path": "phi3:mini via FastAPI gateway",
        "parameters": "Managed by Ollama",
        "gateway_configured": configured,
        "gateway_url": gateway_url,
    }

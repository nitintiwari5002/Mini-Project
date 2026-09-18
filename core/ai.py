import re
from pathlib import Path
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = Path("./models/phi3")

MAX_INPUT_TOKENS = 4096
DEFAULT_MAX_NEW_TOKENS = 512

DEVICE = (
    torch.device("mps")
    if torch.backends.mps.is_available()
    else torch.device("cuda")
    if torch.cuda.is_available()
    else torch.device("cpu")
)
DTYPE = torch.float16 if DEVICE.type in ("mps", "cuda") else torch.float32

@st.cache_resource(show_spinner="Loading AI model...")
def load_model():
    """
    Load tokenizer and model once per Streamlit process.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model directory not found: {MODEL_PATH.resolve()}"
        )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        local_files_only=True,
        trust_remote_code=False,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        local_files_only=True,
        trust_remote_code=False,
        torch_dtype=DTYPE,
        low_cpu_mem_usage=True,
    )

    model.to(DEVICE)
    model.eval()

    return tokenizer, model


tokenizer, model = load_model()

MODE_CONFIG = {
    "general": {
        "system": (
            "You are an expert resume writer and career coach. "
            "Give practical, concise, ATS-friendly advice."
        ),
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
    },

    "questions": {
        "system": (
            "You are an expert interviewer.\n"
            "ONLY output interview questions.\n"
            "Do not provide answers, explanations, headings, numbering, "
            "or additional commentary."
        ),
        "temperature": 0.0,
        "top_p": 1.0,
        "do_sample": False,
    },

    "analysis": {
        "system": (
            "You are an expert resume reviewer and career coach. "
            "Give structured, concise, actionable feedback."
        ),
        "temperature": 0.4,
        "top_p": 0.9,
        "do_sample": True,
    },
}

THINK_BLOCK_PATTERN = re.compile(
    r"<think>.*?</think>",
    flags=re.DOTALL | re.IGNORECASE,
)

def remove_think_blocks(text: str) -> str:
    """
    Remove reasoning blocks if the model produces them.
    """

    if not text:
        return ""

    text = THINK_BLOCK_PATTERN.sub("", text)

    # Remove common accidental whitespace.
    return text.strip()


def clean_prompt(text: str) -> str:
    """
    Normalize user-provided text before sending it to the model.
    """

    if not text:
        return ""

    return text.strip()

def local_chat(
    user_prompt: str,
    mode: str = "general",
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
):
    """
    Run local model inference.

    Returns:
        str: Generated response.
    """

    user_prompt = clean_prompt(user_prompt)

    if not user_prompt:
        return ""

    config = MODE_CONFIG.get(
        mode,
        MODE_CONFIG["general"],
    )

    messages = [
        {
            "role": "system",
            "content": config["system"],
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    prompt_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
        padding=False,
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    input_length = inputs["input_ids"].shape[-1]

    generation_kwargs = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "use_cache": True,
        "do_sample": config["do_sample"],
    }

    if config["do_sample"]:
        generation_kwargs.update(
            {
                "temperature": config["temperature"],
                "top_p": config["top_p"],
            }
        )

    with torch.inference_mode():

        outputs = model.generate(
            **inputs,
            **generation_kwargs,
        )

    generated_tokens = outputs[0, input_length:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    response = remove_think_blocks(response)

    # MPS memory cleanup can help with repeated large requests.
    if DEVICE.type == "mps":
        try:
            torch.mps.empty_cache()
        except Exception:
            pass

    return response


def _safe_chat(
    user_prompt: str,
    mode: str = "general",
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
):
    """
    Run inference and always return (text, error).
    Callers unpack two values.
    """

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

    return _safe_chat(
        prompt_text,
        mode="general",
        max_new_tokens=256,
    )


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
- Quantify impact when the provided information supports it.
- Never invent metrics.
- Keep bullets concise.
- Make them ATS-friendly.
- Do not number the bullets.
"""

    return _safe_chat(
        prompt_text,
        mode="general",
        max_new_tokens=384,
    )


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
- Formatting/content quality
- ATS compatibility

Do not invent information.
"""

    return _safe_chat(
        prompt_text,
        mode="analysis",
        max_new_tokens=512,
    )


def match_keywords(
    resume: str,
    job_desc: str,
) -> str:

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

    return _safe_chat(
        prompt_text,
        mode="analysis",
        max_new_tokens=512,
    )


def prompt(
    text: str,
    mode: str = "general",
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
):
    """
    Generic interface for other parts of the application.

    Returns:
        (response, error)
    """

    return _safe_chat(
        text,
        mode=mode,
        max_new_tokens=max_new_tokens,
    )

def get_model_info() -> dict:
    """
    Useful for displaying model/runtime information in Streamlit.
    """

    return {
        "device": str(DEVICE),
        "dtype": str(DTYPE),
        "model_path": str(MODEL_PATH),
        "parameters": sum(
            p.numel()
            for p in model.parameters()
        ),
    }

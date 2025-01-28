import os
from pathlib import Path
from typing import Any

import jinja2
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

DEFAULT_MODEL_NAME = "gpt-4o-mini"
PROJECT_ROOT = Path(__file__).parents[2]
PROMPTS_DIR = PROJECT_ROOT.joinpath("prompt_templates")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None
)

jinja_env = jinja2.Environment()

PathLike = Path | str


def render_jinja_template(template_str: str, **kwargs: Any) -> str:
    return jinja_env.from_string(template_str).render(**kwargs)


def load_text(file_path: PathLike, encoding: str = "utf-8") -> str:
    return Path(file_path).read_text(encoding=encoding)


def load_prompts(prompts_dir: PathLike = PROMPTS_DIR) -> dict[str, str]:
    prompts_dir = Path(prompts_dir)
    return {
        path.relative_to(prompts_dir).as_posix(): load_text(path)
        for path in prompts_dir.rglob("*.md")
    }


def llm(
    content: str, model_name: str | None = DEFAULT_MODEL_NAME, max_tokens: int = 1024
) -> ChatCompletion:
    model_name = model_name or DEFAULT_MODEL_NAME
    return client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": content}],
        max_tokens=max_tokens,
    )

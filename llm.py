from pathlib import Path
from typing import TypeVar, cast

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.messages.base import BaseMessage
from pydantic import BaseModel

from schema import JobSpec
from schema.resume import Resume
from util.scraper import getPage

PROMPT_DIR = Path(__file__).parent / "assets" / "prompts"
EXTRACT_JOB_SPEC_PROMPT = PROMPT_DIR / "extract_job_spec.txt"
OPTIMIZE_RESUME_FROM_JOB_SPEC_PROMPT = PROMPT_DIR / "optimize_resume_from_job_spec.txt"
COMPRESS_RESUME_TO_ONE_PAGE_PROMPT = PROMPT_DIR / "compress_resume_to_one_page.txt"
MODEL = "gemini-2.5-flash-lite"
SchemaT = TypeVar("SchemaT", bound=BaseModel)


def gemini_model(model: str = MODEL):
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=1.0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )


def load_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8")


def gemini(messages: list[BaseMessage]) -> str:
    llm = gemini_model()

    response = llm.invoke(messages)
    messages.append(response)

    return response.content


def gemini_structured(
    messages: list[BaseMessage],
    schema: type[SchemaT],
) -> SchemaT:
    llm = gemini_model().with_structured_output(
        schema,
        method="json_schema",
    )

    return cast(SchemaT, llm.invoke(messages))


def extract_job_spec(job_page: str) -> JobSpec:
    messages = [
        SystemMessage(load_prompt(EXTRACT_JOB_SPEC_PROMPT)),
        HumanMessage(job_page),
    ]

    return gemini_structured(messages, JobSpec)


def optimize_resume_from_job_spec(resume: Resume, job_spec: JobSpec) -> Resume:
    messages = [
        SystemMessage(load_prompt(OPTIMIZE_RESUME_FROM_JOB_SPEC_PROMPT)),
        HumanMessage(resume.model_dump_json()),
        HumanMessage(job_spec.model_dump_json()),
    ]

    return gemini_structured(messages, Resume)


def compress_resume_to_one_page(resume: Resume, job_spec: JobSpec) -> Resume:
    messages = [
        SystemMessage(load_prompt(COMPRESS_RESUME_TO_ONE_PAGE_PROMPT)),
        HumanMessage(resume.model_dump_json()),
        HumanMessage(job_spec.model_dump_json()),
    ]

    return gemini_structured(messages, Resume)


def main():
    try:
        # page = getPage(
        #     "https://jobs.ashbyhq.com/linqapp/a80957d5-94b1-4be4-9d1b-f396ec3b36eb?utm_source=5W61yBO2K0"
        # )

        page = getPage(
            "https://uszoom.freshteam.com/jobs/xa1WQfaZ3S74/contract-junior-developer-montebello-ny"
        )

        job_spec = extract_job_spec(page)
        print(job_spec.model_dump_json(indent=2))

    except Exception as e:
        print(e.args)


if __name__ == "__main__":
    main()

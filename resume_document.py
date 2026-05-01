import re
from pathlib import Path

from config import BUILD_DIR, DATA_PATH, SCHEMA_PATH, TEMPLATE_PATH
from schema import JobSpec, Resume
from util.fill_resume import (
    build_replacements,
    compile_pdf,
    load_schema,
    render_resume,
    validate_data_shape,
)


def load_resume(path: Path = DATA_PATH) -> Resume:
    return Resume.model_validate_json(path.read_text(encoding="utf-8"))


def snake_case(value: str | None, fallback: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value or fallback).strip("_").lower()
    return normalized or fallback


def resume_pdf_path(job_spec: JobSpec) -> Path:
    company = snake_case(job_spec.company, "unknown_company")
    job_title = snake_case(job_spec.job_title, "unknown_role")
    return BUILD_DIR / f"resume_{company}_{job_title}.pdf"


def write_resume_pdf(resume: Resume, output_path: Path) -> Path:
    resume_data = resume.model_dump(mode="json")
    schema = load_schema(SCHEMA_PATH)
    validate_data_shape(resume_data, schema)

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered = render_resume(template, build_replacements(resume_data, schema))

    tex_output_path = output_path.with_suffix(".tex")
    tex_output_path.parent.mkdir(parents=True, exist_ok=True)
    tex_output_path.write_text(rendered, encoding="utf-8")
    return compile_pdf(tex_output_path, output_path)


def page_count(pdf_path: Path) -> int:
    log_path = pdf_path.with_suffix(".log")
    if log_path.exists():
        match = re.search(
            r"Output written on .*?\(\s*(\d+) pages?,",
            log_path.read_text(encoding="utf-8", errors="ignore"),
            re.DOTALL,
        )
        if match:
            return int(match.group(1))

    pdf_bytes = pdf_path.read_bytes()
    count = len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))
    if count == 0:
        raise RuntimeError(f"Could not determine page count for {pdf_path}")
    return count

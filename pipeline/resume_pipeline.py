from pathlib import Path

from config import MAX_COMPRESSION_ATTEMPTS, DATA_PATH, SCHEMA_PATH, TEMPLATE_PATH
from llm import (
    compress_resume_to_one_page,
    optimize_resume_from_job_spec,
)
from pipeline.base_pipeline import (
    load_document,
    page_count,
    pdf_path_builder,
    write_document_pdf,
)
from pipeline.job_spec_pipeline import get_job_spec_from_url
from schema import Resume
from util.fill_resume import ResumeFiller


def resume_pdf_path(resume: Resume, job_spec) -> Path:
    return pdf_path_builder(
        "resume",
        company=job_spec.company,
        job_title=job_spec.job_title,
    )


def write_resume_pdf(resume: Resume, output_path: Path) -> Path:
    resume_data = resume.model_dump(mode="json")
    return write_document_pdf(
        resume_data,
        ResumeFiller,
        SCHEMA_PATH,
        TEMPLATE_PATH,
        output_path,
    )


def render_resume_for_job_url(job_url: str) -> Path:
    resume = load_document(DATA_PATH, Resume)
    job_spec = get_job_spec_from_url(job_url)
    output_path = resume_pdf_path(resume, job_spec)

    resume = optimize_resume_from_job_spec(resume, job_spec)
    pdf_path = write_resume_pdf(resume, output_path)

    compression_attempts = 0
    while page_count(pdf_path) > 1 and compression_attempts < MAX_COMPRESSION_ATTEMPTS:
        compression_attempts += 1
        resume = compress_resume_to_one_page(resume, job_spec)
        pdf_path = write_resume_pdf(resume, output_path)

    pages = page_count(pdf_path)
    if pages > 1:
        raise RuntimeError(
            f"Resume still renders to {pages} pages after "
            f"{MAX_COMPRESSION_ATTEMPTS} compression attempts."
        )

    return pdf_path

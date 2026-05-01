from pathlib import Path

from config import MAX_COMPRESSION_ATTEMPTS
from llm import (
    compress_resume_to_one_page,
    extract_job_spec,
    optimize_resume_from_job_spec,
)
from resume_document import load_resume, page_count, resume_pdf_path, write_resume_pdf
from util.scraper import getPage


def render_resume_for_job_url(job_url: str) -> Path:
    resume = load_resume()
    page = getPage(job_url)
    job_spec = extract_job_spec(page)
    output_path = resume_pdf_path(job_spec)

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

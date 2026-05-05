from pathlib import Path

from config import (
    COVER_LETTER_SCHEMA_PATH,
    COVER_LETTER_TEMPLATE_PATH,
    DATA_PATH,
)
from llm import create_cover_letter_from_job_spec
from pipeline.base_pipeline import (
    load_document,
    pdf_path_builder,
    write_document_pdf,
)
from pipeline.job_spec_pipeline import get_job_spec_from_url
from schema import CoverLetter, Resume
from util.fill_cover_letter import CoverLetterFiller


def cover_letter_pdf_path(job_spec) -> Path:
    return pdf_path_builder(
        "cover_letter",
        company=job_spec.company,
        job_title=job_spec.job_title,
    )


def write_cover_letter_pdf(cover_letter: CoverLetter, output_path: Path) -> Path:
    cover_letter_data = cover_letter.model_dump(mode="json")
    return write_document_pdf(
        cover_letter_data,
        CoverLetterFiller,
        COVER_LETTER_SCHEMA_PATH,
        COVER_LETTER_TEMPLATE_PATH,
        output_path,
    )


def render_cover_letter_for_job_url(job_url: str) -> Path:
    resume = load_document(DATA_PATH, Resume)
    job_spec = get_job_spec_from_url(job_url)

    cover_letter_content = create_cover_letter_from_job_spec(resume, job_spec)

    cover_letter = CoverLetter(
        basics=resume.basics,
        cover_letter=cover_letter_content,
    )

    output_path = cover_letter_pdf_path(job_spec)
    pdf_path = write_cover_letter_pdf(cover_letter, output_path)

    return pdf_path
import re
import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from config import BUILD_DIR
from util.fill_latex import LatexUtils

T = TypeVar("T", bound=BaseModel)


def snake_case(value: str | None, fallback: str) -> str:
    """Convert a string to snake_case with fallback option."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value or fallback).strip("_").lower()
    return normalized or fallback


def load_document(path: Path, schema: type[T]) -> T:
    """Load and validate a JSON document using a Pydantic schema."""
    return schema.model_validate_json(path.read_text(encoding="utf-8"))


def page_count(pdf_path: Path) -> int:
    """Count the number of pages in a PDF file."""
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


def write_document_pdf(
    document_data: dict,
    filler_class,
    schema_path: Path,
    template_path: Path,
    output_path: Path,
) -> Path:
    """Generic LaTeX-based document writer.
    
    Args:
        document_data: The document data dict (e.g., from model_dump)
        filler_class: The filler class to use (ResumeFiller or CoverLetterFiller)
        schema_path: Path to the JSON schema file
        template_path: Path to the LaTeX template file
        output_path: Path where the PDF should be saved
    
    Returns:
        Path to the generated PDF file
    """
    filler = filler_class()
    schema = LatexUtils.load_schema(schema_path)
    filler.validate_data_shape(document_data, schema)

    template = template_path.read_text(encoding="utf-8")
    rendered = filler.render_resume(template, filler.build_replacements(document_data, schema))

    tex_output_path = output_path.with_suffix(".tex")
    tex_output_path.parent.mkdir(parents=True, exist_ok=True)
    tex_output_path.write_text(rendered, encoding="utf-8")
    return LatexUtils.compile_pdf(tex_output_path, output_path)


def pdf_path_builder(document_type: str, **name_parts) -> Path:
    """Build output PDF path with snake_cased components.
    
    Args:
        document_type: Type of document (e.g., 'resume', 'cover_letter')
        **name_parts: Key-value pairs to include in filename
    
    Returns:
        Path to output PDF
    
    Example:
        pdf_path_builder('resume', company='Acme Corp', role='Engineer')
        -> /path/to/build/resume_acme_corp_engineer.pdf
    """
    parts = [document_type]
    for key in sorted(name_parts.keys()):  # Sort for consistent naming
        value = name_parts[key]
        parts.append(snake_case(value, "unknown"))
    
    filename = "_".join(parts) + ".pdf"
    return BUILD_DIR / filename

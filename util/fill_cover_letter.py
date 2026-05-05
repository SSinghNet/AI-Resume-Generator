from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema.cover_letter import CoverLetter

from util.fill_latex import LatexUtils


class CoverLetterFiller:
    DEFAULT_TEMPLATE_PATH = ROOT / "assets" / "templates" / "cover_letter_template.tex"
    DEFAULT_DATA_PATH = ROOT / "assets" / "data" / "resume_example.json"
    DEFAULT_SCHEMA_PATH = ROOT / "assets" / "schema" / "cover_letter_schema.json"
    DEFAULT_OUTPUT_PATH = ROOT / "build" / "cover_letter.tex"

    def __init__(self, template_path=None, data_path=None, schema_path=None, output_path=None):
        self.template_path = template_path or self.DEFAULT_TEMPLATE_PATH
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self.schema_path = schema_path or self.DEFAULT_SCHEMA_PATH
        self.output_path = output_path or self.DEFAULT_OUTPUT_PATH


    def load_cover_letter_data(self) -> dict:
        with self.data_path.open(encoding="utf-8") as data_file:
            return json.load(data_file)


    @staticmethod
    def validate_cover_letter_data(data: dict) -> CoverLetter:
        return CoverLetter.model_validate(data)

    @staticmethod
    def validate_data_shape(data: dict, schema: dict) -> None:
        """Validate that required top-level keys exist in data."""
        expected_keys = [key for key in schema.keys() if key != "template"]
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise ValueError(f"Cover letter data is missing required top-level keys: {missing}")


    @staticmethod
    def render_letter_date(value: str) -> str:
        if value == "\\today":
            return value
        return LatexUtils.escape_latex_text(value)


    @staticmethod
    def default_opening(role: str, company: str) -> str:
        return (
            f"I am excited to apply for the {role} role at {company}. My background in "
            "software engineering, systems work, and full-stack product development has "
            "prepared me to contribute quickly to teams building reliable, useful software."
        )


    @staticmethod
    def default_experience(role: str) -> str:
        return (
            f"In my recent work, I have built production features, internal APIs, "
            f"authentication flows, and cloud-backed services that map closely to the "
            f"expectations of a {role}. I enjoy turning ambiguous requirements into "
            "maintainable implementations that are easy for users and teammates to trust."
        )


    @staticmethod
    def default_fit(company: str) -> str:
        return (
            f"I am especially interested in {company} because the role calls for a mix "
            "of practical engineering judgment, ownership, and collaboration. I would "
            "bring a steady learning posture, strong implementation habits, and care for "
            "the details that make software dependable."
        )


    def render_cover_letter_fields(
        self, data: dict, placeholders: dict[str, str]
    ) -> dict[str, str]:
        cover_letter = data["cover_letter"]
        role = cover_letter["role"]
        company = cover_letter["company"]

        opening = cover_letter["opening_paragraph"] or self.default_opening(role, company)
        experience = cover_letter["experience_paragraph"] or self.default_experience(role)
        fit = cover_letter["fit_paragraph"] or self.default_fit(company)

        return {
            placeholders["letter_date"]: self.render_letter_date(cover_letter["letter_date"]),
            placeholders["hiring_manager"]: LatexUtils.escape_latex_text(
                cover_letter["hiring_manager"]
            ),
            placeholders["opening_paragraph"]: LatexUtils.escape_latex_text(opening),
            placeholders["experience_paragraph"]: LatexUtils.escape_latex_text(experience),
            placeholders["fit_paragraph"]: LatexUtils.escape_latex_text(fit),
            placeholders["closing_paragraph"]: LatexUtils.escape_latex_text(
                cover_letter["closing_paragraph"]
            ),
        }


    def build_replacements(self, data: dict, schema: dict) -> dict[str, str]:
        model = self.validate_cover_letter_data(data)
        normalized_data = model.model_dump(mode="json")
        placeholders = schema["template"]["placeholders"]

        replacements = LatexUtils.render_heading(normalized_data, placeholders)
        replacements.update(self.render_cover_letter_fields(normalized_data, placeholders))
        return replacements

    @staticmethod
    def render_resume(template: str, replacements: dict[str, str]) -> str:
        """Render template with replacements (generic method name for compatibility)."""
        return LatexUtils.render_resume(template, replacements)


    def render_cover_letter_from_paths(self) -> str:
        data = self.load_cover_letter_data()
        schema = LatexUtils.load_schema(self.schema_path)
        template = self.template_path.read_text(encoding="utf-8")
        return LatexUtils.render_resume(template, self.build_replacements(data, schema))


    def write_rendered_cover_letter(self) -> Path:
        rendered = self.render_cover_letter_from_paths()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(rendered, encoding="utf-8")
        return self.output_path



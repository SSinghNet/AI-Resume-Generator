from __future__ import annotations

import json
from pathlib import Path

from util.fill_latex import LatexUtils

ROOT = Path(__file__).resolve().parent.parent


class ResumeFiller:
    DEFAULT_TEMPLATE_PATH = ROOT / "assets" / "templates" / "resume_template.tex"
    DEFAULT_DATA_PATH = ROOT / "assets" / "data" / "resume_example.json"
    DEFAULT_SCHEMA_PATH = ROOT / "assets" / "schema" / "resume_schema.json"
    DEFAULT_OUTPUT_PATH = ROOT / "build" / "resume.tex"

    def __init__(self, template_path=None, data_path=None, schema_path=None, output_path=None):
        self.template_path = template_path or self.DEFAULT_TEMPLATE_PATH
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self.schema_path = schema_path or self.DEFAULT_SCHEMA_PATH
        self.output_path = output_path or self.DEFAULT_OUTPUT_PATH

    @staticmethod
    def latex_href(url: str, display: str) -> str:
        return f"\\href{{{url}}}{{\\underline{{{display}}}}}"


    @staticmethod
    def latex_href(url: str, display: str) -> str:
        return LatexUtils.latex_href(url, display)


    @staticmethod
    def strip_latex_emphasis(value: str) -> str:
        return LatexUtils.strip_latex_emphasis(value)


    @staticmethod
    def render_skill_text(value: str) -> str:
        return LatexUtils.render_skill_text(value)


    def load_resume_data(self) -> dict:
        with self.data_path.open(encoding="utf-8") as data_file:
            return json.load(data_file)


    @staticmethod
    def validate_data_shape(data: dict, schema: dict) -> None:
        expected_keys = [key for key in schema.keys() if key != "template"]
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise ValueError(f"Resume data is missing required top-level keys: {missing}")


    @staticmethod
    def render_heading(data: dict, placeholders: dict[str, str]) -> dict[str, str]:
        return LatexUtils.render_heading(data, placeholders)


    @staticmethod
    def render_subheading_with_details(entries: list[dict]) -> str:
        blocks = ["\\resumeSubHeadingListStart"]
        for entry in entries:
            blocks.extend(
                [
                    "    \\resumeSubheading",
                    f"      {{{entry['institution']}}}{{{entry['location']}}}",
                    f"      {{{entry['degree']}}} {{{entry['date_range']}}}",
                ]
            )
            if entry.get("details"):
                blocks.extend(
                    [
                        # "      \\vspace{-8mm}",
                        "      \\small{\\item{",
                        "          " + " \\\\ ".join(entry["details"]),
                        "    }}",
                    ]
                )
        blocks.append("\\resumeSubHeadingListEnd")
        return "\n".join(blocks)


    @staticmethod
    def render_certifications(entries: list[dict]) -> str:
        blocks = ["\\resumeSubHeadingListStart"]
        for entry in entries:
            verification_link = ResumeFiller.latex_href(
                entry["verification_url"], entry["verification_display"]
            )
            blocks.extend(
                [
                    "    \\resumeSubheading",
                    f"      {{{entry['name']}}}{{\\footnotesize{{{verification_link}}}}}{{}}{{}}",
                    "      \\vspace{-5mm}",
                ]
            )
        blocks.append("\\resumeSubHeadingListEnd")
        return "\n".join(blocks)


    @staticmethod
    def render_bullets(bullets: list[str], indent: str = "        ") -> list[str]:
        lines = [f"{indent}\\resumeItemListStart"]
        lines.extend(f"{indent}    \\resumeItem{{{bullet}}}" for bullet in bullets)
        lines.append(f"{indent}\\resumeItemListEnd")
        return lines


    @staticmethod
    def render_experience(entries: list[dict]) -> str:
        blocks = ["\\resumeSubHeadingListStart"]
        for entry in entries:
            blocks.extend(
                [
                    "    \\resumeSubheading",
                    f"        {{{entry['title']}}}{{{entry['date_range']}}}",
                    f"        {{{entry['organization']}}}{{{entry['location']}}}",
                ]
            )
            blocks.extend(ResumeFiller.render_bullets(entry["bullets"]))
            blocks.append("")
        if blocks[-1] == "":
            blocks.pop()
        blocks.append("\\resumeSubHeadingListEnd")
        return "\n".join(blocks)


    @staticmethod
    def render_projects(entries: list[dict]) -> str:
        blocks = ["\\resumeSubHeadingListStart"]
        for entry in entries:
            tech_list = ", ".join(entry["technologies"])
            project_link = ResumeFiller.latex_href(
                entry["link"]["url"], f"\\textit{{{entry['link']['display']}}}"
            )
            blocks.extend(
                [
                    "    \\resumeProjectHeading",
                    f"      {{\\textbf{{{entry['name']}}} $|$ \\emph{{{tech_list}}}}}{{{project_link}}}",
                ]
            )
            blocks.extend(ResumeFiller.render_bullets(entry["bullets"], indent="      "))
            blocks.append("")
        if blocks[-1] == "":
            blocks.pop()
        blocks.append("\\resumeSubHeadingListEnd")
        return "\n".join(blocks)


    @staticmethod
    def render_technical_skills(skills: dict[str, list[str]]) -> str:
        lines = [
            "\\begin{itemize}[leftmargin=0.15in, label={}]",
            "    \\small{\\item{",
        ]
        skill_lines = []
        for category, values in skills.items():
            rendered_values = ", ".join(ResumeFiller.render_skill_text(value) for value in values)
            skill_lines.append(
                f"     \\textbf{{{ResumeFiller.render_skill_text(category)}}}{{: {rendered_values}}}"
            )
        lines.append(" \\\\\n".join(skill_lines))
        lines.extend(
            [
                "    }}",
                " \\end{itemize}",
            ]
        )
        return "\n".join(lines)


    SECTION_RENDERERS = {
        "subheading_with_details": render_subheading_with_details,
        "certifications": render_certifications,
        "experience": render_experience,
        "projects": render_projects,
        "technical_skills": render_technical_skills,
    }


    def build_replacements(self, data: dict, schema: dict) -> dict[str, str]:
        replacements = {}
        template_config = schema["template"]
        replacements.update(self.render_heading(data, template_config["placeholders"]))

        for section in template_config["sections"]:
            renderer_name = section["renderer"]
            renderer = self.SECTION_RENDERERS.get(renderer_name)
            if renderer is None:
                raise ValueError(f"Unknown renderer configured in schema: {renderer_name}")
            replacements[section["placeholder"]] = renderer(data[section["data_key"]])

        return replacements


    @staticmethod
    def render_resume(template: str, replacements: dict[str, str]) -> str:
        return LatexUtils.render_resume(template, replacements)


    def render_resume_from_paths(self) -> str:
        data = self.load_resume_data()
        schema = LatexUtils.load_schema(self.schema_path)
        self.validate_data_shape(data, schema)
        template = self.template_path.read_text(encoding="utf-8")
        return self.render_resume(template, self.build_replacements(data, schema))


    def write_rendered_resume(self) -> Path:
        rendered = self.render_resume_from_paths()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(rendered, encoding="utf-8")
        return self.output_path


    def main(self) -> None:
        pass


if __name__ == "__main__":
    filler = ResumeFiller()
    filler.main()

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LOCAL_TEXMF = ROOT / ".texmf"
DEFAULT_SCHEMA_PATH = ROOT / "assets" / "schema" / "resume_schema.json"

PDFLATEX_CANDIDATES = [
    "pdflatex",
    "/Library/TeX/texbin/pdflatex",
]


def latex_href(url: str, display: str) -> str:
    return f"\\href{{{url}}}{{\\underline{{{display}}}}}"


def escape_latex_text(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
        .replace("_", "\\_")
    )


def strip_latex_emphasis(value: str) -> str:
    previous = None
    stripped = value
    while stripped != previous:
        previous = stripped
        stripped = re.sub(r"\\{1,2}(?:textbf|emph|textit)\{([^{}]*)\}", r"\1", stripped)
    return stripped.replace("**", "").replace("__", "").strip()


def render_skill_text(value: str) -> str:
    return escape_latex_text(strip_latex_emphasis(value))


def load_resume_data(path: Path) -> dict:
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def load_schema(path: Path | None = None) -> dict:
    schema_path = path or DEFAULT_SCHEMA_PATH
    with schema_path.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def validate_data_shape(data: dict, schema: dict) -> None:
    expected_keys = [key for key in schema.keys() if key != "template"]
    missing_keys = [key for key in expected_keys if key not in data]
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise ValueError(f"Resume data is missing required top-level keys: {missing}")


def render_heading(data: dict, placeholders: dict[str, str]) -> dict[str, str]:
    basics = data["basics"]
    profile_links = " $|$\n    ".join(
        latex_href(profile["url"], profile["display"]) for profile in basics["profiles"]
    )
    return {
        placeholders["name"]: basics["name"],
        placeholders["location"]: basics["location"],
        placeholders["phone"]: basics["phone"],
        placeholders["email_link"]: latex_href(
            f"mailto:{basics['email']}", basics["email"]
        ),
        placeholders["profile_links"]: profile_links,
    }


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


def render_certifications(entries: list[dict]) -> str:
    blocks = ["\\resumeSubHeadingListStart"]
    for entry in entries:
        verification_link = latex_href(
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


def render_bullets(bullets: list[str], indent: str = "        ") -> list[str]:
    lines = [f"{indent}\\resumeItemListStart"]
    lines.extend(f"{indent}    \\resumeItem{{{bullet}}}" for bullet in bullets)
    lines.append(f"{indent}\\resumeItemListEnd")
    return lines


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
        blocks.extend(render_bullets(entry["bullets"]))
        blocks.append("")
    if blocks[-1] == "":
        blocks.pop()
    blocks.append("\\resumeSubHeadingListEnd")
    return "\n".join(blocks)


def render_projects(entries: list[dict]) -> str:
    blocks = ["\\resumeSubHeadingListStart"]
    for entry in entries:
        tech_list = ", ".join(entry["technologies"])
        project_link = latex_href(
            entry["link"]["url"], f"\\textit{{{entry['link']['display']}}}"
        )
        blocks.extend(
            [
                "    \\resumeProjectHeading",
                f"      {{\\textbf{{{entry['name']}}} $|$ \\emph{{{tech_list}}}}}{{{project_link}}}",
            ]
        )
        blocks.extend(render_bullets(entry["bullets"], indent="      "))
        blocks.append("")
    if blocks[-1] == "":
        blocks.pop()
    blocks.append("\\resumeSubHeadingListEnd")
    return "\n".join(blocks)


def render_technical_skills(skills: dict[str, list[str]]) -> str:
    lines = [
        "\\begin{itemize}[leftmargin=0.15in, label={}]",
        "    \\small{\\item{",
    ]
    skill_lines = []
    for category, values in skills.items():
        rendered_values = ", ".join(render_skill_text(value) for value in values)
        skill_lines.append(
            f"     \\textbf{{{render_skill_text(category)}}}{{: {rendered_values}}}"
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


def build_replacements(data: dict, schema: dict) -> dict[str, str]:
    replacements = {}
    template_config = schema["template"]
    replacements.update(render_heading(data, template_config["placeholders"]))

    for section in template_config["sections"]:
        renderer_name = section["renderer"]
        renderer = SECTION_RENDERERS.get(renderer_name)
        if renderer is None:
            raise ValueError(f"Unknown renderer configured in schema: {renderer_name}")
        replacements[section["placeholder"]] = renderer(data[section["data_key"]])

    return replacements


def render_resume(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def render_resume_from_paths(
    template_path: Path, data_path: Path, schema_path: Path | None = None
) -> str:
    data = load_resume_data(data_path)
    schema = load_schema(schema_path)
    validate_data_shape(data, schema)
    template = template_path.read_text(encoding="utf-8")
    return render_resume(template, build_replacements(data, schema))


def write_rendered_resume(
    template_path: Path,
    data_path: Path,
    output_path: Path,
    schema_path: Path | None = None,
) -> Path:
    rendered = render_resume_from_paths(template_path, data_path, schema_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def compile_pdf(tex_path: Path, output_path: Path) -> Path:
    pdflatex = None
    for candidate in PDFLATEX_CANDIDATES:
        resolved = shutil.which(candidate)
        if resolved:
            pdflatex = resolved
            break
    if not pdflatex:
        raise RuntimeError(
            "pdflatex is not installed or not on PATH. Render to a .tex file or install a TeX distribution."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_path.parent}",
        tex_path.name,
    ]
    env = dict(os.environ)
    env["PATH"] = f"/Library/TeX/texbin:{env.get('PATH', '')}"
    if LOCAL_TEXMF.exists():
        env["TEXMFHOME"] = str(LOCAL_TEXMF)

    try:
        subprocess.run(
            command,
            cwd=tex_path.parent,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
    except subprocess.CalledProcessError as exc:
        output = exc.stdout.strip() if exc.stdout else ""
        raise RuntimeError(f"pdflatex failed:\n{output}") from exc

    compiled_pdf = output_path.parent / f"{tex_path.stem}.pdf"
    if compiled_pdf != output_path:
        compiled_pdf.replace(output_path)
    return output_path

def main() -> None:
    pass
    # write_rendered_resume()
    # compile_pdf()


if __name__ == "__main__":
    main()

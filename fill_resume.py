from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCAL_TEXMF = ROOT / ".texmf"

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


def load_resume_data(path: Path) -> dict:
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def render_heading(data: dict) -> dict[str, str]:
    basics = data["basics"]
    profile_links = " $|$\n    ".join(
        latex_href(profile["url"], profile["display"]) for profile in basics["profiles"]
    )
    return {
        "%%NAME%%": basics["name"],
        "%%LOCATION%%": basics["location"],
        "%%PHONE%%": basics["phone"],
        "%%EMAIL_LINK%%": latex_href(f"mailto:{basics['email']}", basics["email"]),
        "%%PROFILE_LINKS%%": profile_links,
    }


def render_education(entries: list[dict]) -> str:
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
        skill_lines.append(
            f"     \\textbf{{{escape_latex_text(category)}}}{{: {', '.join(values)}}}"
        )
    lines.append(" \\\\\n".join(skill_lines))
    lines.extend(
        [
            "    }}",
            " \\end{itemize}",
        ]
    )
    return "\n".join(lines)


def build_replacements(data: dict) -> dict[str, str]:
    replacements = {}
    replacements.update(render_heading(data))
    replacements["%%EDUCATION_SECTION%%"] = render_education(data["education"])
    replacements["%%CERTIFICATIONS_SECTION%%"] = render_certifications(
        data["certifications"]
    )
    replacements["%%EXPERIENCE_SECTION%%"] = render_experience(data["experience"])
    replacements["%%PROJECTS_SECTION%%"] = render_projects(data["projects"])
    replacements["%%TECHNICAL_SKILLS_SECTION%%"] = render_technical_skills(
        data["technical_skills"]
    )
    return replacements


def render_resume(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def render_resume_from_paths(template_path: Path, data_path: Path) -> str:
    data = load_resume_data(data_path)
    template = template_path.read_text(encoding="utf-8")
    return render_resume(template, build_replacements(data))


def write_rendered_resume(template_path: Path, data_path: Path, output_path: Path) -> Path:
    rendered = render_resume_from_paths(template_path, data_path)
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

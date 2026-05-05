import shutil, subprocess, os, json, re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

PDFLATEX_CANDIDATES = [
    "pdflatex",
    "/Library/TeX/texbin/pdflatex",
]

LOCAL_TEXMF = ROOT / ".texmf"

DEFAULT_SCHEMA_PATH = ROOT / "assets" / "schema" / "resume_schema.json"


class LatexUtils:
    @staticmethod
    def load_schema(path: Path | None = None) -> dict:
        schema_path = path or DEFAULT_SCHEMA_PATH
        with schema_path.open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    @staticmethod
    def escape_latex_text(value: str) -> str:
        return (
            value.replace("\\", "\\textbackslash{}")
            .replace("&", "\\&")
            .replace("%", "\\%")
            .replace("#", "\\#")
            .replace("_", "\\_")
        )

    @staticmethod
    def escape_latex_preserve_formatting(value: str) -> str:
        """Escape special characters while preserving LaTeX formatting like \\textbf{}, \\emph{}, etc."""
        # Pattern to match LaTeX commands like \textbf{...}, \emph{...}, etc.
        pattern = r'(\\(?:textbf|emph|textit|underline|texttt)\{[^}]*\})'
        parts = re.split(pattern, value)
        
        # Escape non-LaTeX parts, keep LaTeX parts as-is
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Non-LaTeX part
                result.append(LatexUtils.escape_latex_text(part))
            else:  # LaTeX command part - don't escape
                result.append(part)
        return ''.join(result)

    @staticmethod
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
            f"-output-directory={output_path.parent.resolve()}",
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

    @staticmethod
    def latex_href(url: str, display: str) -> str:
        # Escape URL for LaTeX to handle special characters like underscores
        escaped_url = LatexUtils.escape_latex_text(url)
        return f"\\href{{{escaped_url}}}{{\\underline{{{display}}}}}"


    @staticmethod
    def strip_latex_emphasis(value: str) -> str:
        previous = None
        stripped = value
        while stripped != previous:
            previous = stripped
            stripped = re.sub(r"\\{1,2}(?:textbf|emph|textit)\{([^{}]*)\}", r"\1", stripped)
        return stripped.replace("**", "").replace("__", "").strip()


    @staticmethod
    def render_skill_text(value: str) -> str:
        return LatexUtils.escape_latex_text(LatexUtils.strip_latex_emphasis(value))


    @staticmethod
    def render_heading(data: dict, placeholders: dict[str, str]) -> dict[str, str]:
        basics = data["basics"]
        profile_links = " $|$\n    ".join(
            LatexUtils.latex_href(profile["url"], LatexUtils.escape_latex_text(profile["display"])) for profile in basics["profiles"]
        )
        return {
            placeholders["name"]: LatexUtils.escape_latex_text(basics["name"]),
            placeholders["location"]: LatexUtils.escape_latex_text(basics["location"]),
            placeholders["phone"]: LatexUtils.escape_latex_text(basics["phone"]),
            placeholders["email_link"]: LatexUtils.latex_href(
                f"mailto:{basics['email']}", LatexUtils.escape_latex_text(basics["email"])
            ),
            placeholders["profile_links"]: profile_links,
        }


    @staticmethod
    def render_resume(template: str, replacements: dict[str, str]) -> str:
        rendered = template
        for placeholder, value in replacements.items():
            rendered = rendered.replace(placeholder, value)
        return rendered
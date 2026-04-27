import argparse
from pathlib import Path

from fill_resume import compile_pdf, write_rendered_resume

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "assets" / "templates" / "resume.tex"
DATA_PATH = ROOT / "assets" / "data" / "resume.json"
OUTPUT_PATH = ROOT / "build" / "resume.tex"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the resume LaTeX from JSON data.")
    parser.add_argument(
        "--template",
        type=Path,
        default=TEMPLATE_PATH,
        help="Path to the LaTeX template.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_PATH,
        help="Path to the resume JSON data.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Path to write the rendered LaTeX file.",
    )
    args = parser.parse_args()

    output_path = args.output.resolve()
    if output_path.suffix.lower() == ".pdf":
        tex_output = output_path.with_suffix(".tex")
        write_rendered_resume(args.template, args.data, tex_output)
        compile_pdf(tex_output, output_path)
    else:
        write_rendered_resume(args.template, args.data, output_path)


if __name__ == "__main__":
    main()

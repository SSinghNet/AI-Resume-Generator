import argparse
from typing import Tuple

from pipeline.cover_letter_pipeline import render_cover_letter_for_job_url
from pipeline.resume_pipeline import render_resume_for_job_url

import gradio as gr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a tailored resume and cover letter PDF."
    )
    parser.add_argument(
        "job_url",
        nargs="?",
        help="Job posting URL to tailor the resume against.",
    )
    parser.add_argument(
        "--gradio",
        action="store_true",
        help="Launch a Gradio web UI for entering a job URL.",
    )
    return parser.parse_args()


def generate_pdfs(job_url: str) -> Tuple[str, str]:
    if not job_url:
        raise ValueError("Please provide a job URL to generate PDFs.")

    resume_pdf_path = render_resume_for_job_url(job_url)
    cover_letter_pdf_path = render_cover_letter_for_job_url(job_url)

    return str(resume_pdf_path), str(cover_letter_pdf_path)


def launch_gradio() -> None:

    demo = gr.Interface(
        fn=generate_pdfs,
        inputs=gr.Textbox(
            label="Job URL",
            placeholder="https://example.com/job-posting",
            lines=1,
        ),
        outputs=[
            gr.File(label="Resume PDF"),
            gr.File(label="Cover Letter PDF"),
        ],
        title="Resume + Cover Letter Generator",
        description="Enter a job posting URL to generate tailored resume and cover letter PDFs.",
    )

    demo.launch()


def main() -> None:
    args = parse_args()

    if args.gradio or args.job_url is None:
        launch_gradio()
        return

    resume_pdf_path = render_resume_for_job_url(args.job_url)
    print(f"Rendered resume PDF: {resume_pdf_path}")

    cover_letter_pdf_path = render_cover_letter_for_job_url(args.job_url)
    print(f"Rendered cover letter PDF: {cover_letter_pdf_path}")


if __name__ == "__main__":
    main()

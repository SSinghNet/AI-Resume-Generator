import argparse

from resume_pipeline import render_resume_for_job_url

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a tailored resume PDF.")
    parser.add_argument(
        "job_url",
        nargs="?",
        help="Job posting URL to tailor the resume against.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pdf_path = render_resume_for_job_url(args.job_url)
    print(f"Rendered resume PDF: {pdf_path}")


if __name__ == "__main__":
    main()

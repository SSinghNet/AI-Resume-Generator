from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "assets" / "data" / "resume_example.json"
TEMPLATE_PATH = ROOT / "assets" / "templates" / "resume_template.tex"
SCHEMA_PATH = ROOT / "assets" / "schema" / "resume_schema.json"

COVER_LETTER_TEMPLATE_PATH = ROOT / "assets" / "templates" / "cover_letter_template.tex"
COVER_LETTER_SCHEMA_PATH = ROOT / "assets" / "schema" / "cover_letter_schema.json"

BUILD_DIR = ROOT / "build"

MAX_COMPRESSION_ATTEMPTS = 3


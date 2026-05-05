from pydantic import BaseModel, Field

from schema.resume import Basics


class CoverLetterContent(BaseModel):
    letter_date: str = "\\today"
    hiring_manager: str = "Hiring Manager"
    role: str = "Software Engineer"
    company: str = "the company"
    opening_paragraph: str = ""
    experience_paragraph: str = ""
    fit_paragraph: str = ""
    closing_paragraph: str = ""

class CoverLetter(BaseModel):
    basics: Basics
    cover_letter: CoverLetterContent = Field(default_factory=CoverLetterContent)

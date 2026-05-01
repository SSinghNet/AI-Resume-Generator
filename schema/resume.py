from pydantic import BaseModel


class Profile(BaseModel):
    label: str
    display: str
    url: str


class Basics(BaseModel):
    name: str
    location: str
    phone: str
    email: str
    profiles: list[Profile]


class Education(BaseModel):
    institution: str
    location: str
    degree: str
    date_range: str
    details: list[str]


class Certification(BaseModel):
    name: str
    verification_display: str
    verification_url: str


class Experience(BaseModel):
    title: str
    date_range: str
    organization: str
    location: str
    bullets: list[str]


class Link(BaseModel):
    display: str
    url: str


class Project(BaseModel):
    name: str
    technologies: list[str]
    link: Link
    bullets: list[str]


class Resume(BaseModel):
    basics: Basics
    education: list[Education]
    certifications: list[Certification]
    experience: list[Experience]
    projects: list[Project]
    technical_skills: dict[str, list[str]]

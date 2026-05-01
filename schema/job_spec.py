from enum import StrEnum

from pydantic import BaseModel


class EmploymentType(StrEnum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class LocationType(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class ExperienceLevel(StrEnum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    LEAD = "lead"
    MANAGER = "manager"
    UNKNOWN = "unknown"


class SalaryPeriod(StrEnum):
    ANNUAL = "annual"
    HOURLY = "hourly"
    MONTHLY = "monthly"
    UNKNOWN = "unknown"


class JobLocation(BaseModel):
    type: LocationType
    place: str | None


class JobExperience(BaseModel):
    min_years: float | None
    max_years: float | None
    level: ExperienceLevel


class JobEducation(BaseModel):
    required: bool
    degrees: list[str]
    fields: list[str]


class JobSalary(BaseModel):
    min: float | None
    max: float | None
    currency: str | None
    period: SalaryPeriod


class JobSpec(BaseModel):
    job_title: str | None
    company: str | None
    employment_type: EmploymentType
    location: JobLocation
    required_skills: list[str]
    preferred_skills: list[str]
    tools_and_technologies: list[str]
    keywords: list[str]
    experience: JobExperience
    education: JobEducation
    company_summary: str | None
    responsibilities: list[str]
    soft_skills: list[str]
    salary: JobSalary
    benefits: list[str]
    domain: str | None
    seniority_signals: list[str]

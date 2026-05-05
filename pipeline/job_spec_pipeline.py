from functools import cache

from llm import extract_job_spec
from schema.job_spec import JobSpec
from util.scraper import getPage

@cache
def get_job_spec_from_url(job_url: str) -> JobSpec:
    page = getPage(job_url)
    return extract_job_spec(page)

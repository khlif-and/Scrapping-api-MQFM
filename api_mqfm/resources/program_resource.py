from pydantic import BaseModel
from typing import List

class ProgramItemResource(BaseModel):
    title: str
    image_url: str

class ProgramResource(BaseModel):
    programs: List[ProgramItemResource]

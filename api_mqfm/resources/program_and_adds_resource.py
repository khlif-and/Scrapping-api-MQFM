from pydantic import BaseModel
from typing import List

class ProgramAndAddsItemResource(BaseModel):
    title: str
    image_url: str

class ProgramAndAddsResource(BaseModel):
    programs: List[ProgramAndAddsItemResource]

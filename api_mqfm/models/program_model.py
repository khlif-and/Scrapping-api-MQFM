from pydantic import BaseModel
from typing import List

class ProgramOnAirModel(BaseModel):
    title: str
    image_url: str

class ProgramOnAirResponse(BaseModel):
    programs: List[ProgramOnAirModel]

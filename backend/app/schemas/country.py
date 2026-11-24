from typing import Optional
from pydantic import BaseModel


class CountryOut(BaseModel):
    iso_code: str
    continent: str
    location: str
    income_group: str
    is_aggregate: bool
    is_active: bool
    data_source: str

    class Config:
        from_attributes = True

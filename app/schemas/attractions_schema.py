from pydantic import BaseModel, Field
from typing import Optional


class TouristAttractionResponse(BaseModel):
    id: int
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    thumbnail: Optional[str] = None
    link_to_website: Optional[str] = Field(alias="linktowebsite", default=None)
    link_to_wikipedia: Optional[str] = Field(alias="linktowikipedia", default=None)
    comment: str
    description: str
    country_id: Optional[int] = None
    city_id: Optional[int] = None

    class Config:
        from_attributes = True



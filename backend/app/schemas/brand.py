from pydantic import BaseModel, ConfigDict


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str

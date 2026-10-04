from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_tr: str = ""
    slug: str

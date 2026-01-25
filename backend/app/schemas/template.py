from pydantic import BaseModel


class TemplateColumn(BaseModel):
    title: str
    color: str


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    columns: list[TemplateColumn]

    class Config:
        from_attributes = True

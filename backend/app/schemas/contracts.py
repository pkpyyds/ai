from pydantic import BaseModel, Field


class ProductItem(BaseModel):
    id: int
    title: str
    category: str
    platform_product_id: str
    status: str
    task_id: int | None = None


class ReviewDecision(BaseModel):
    comment: str = Field(default='', max_length=1000)


class Envelope(BaseModel):
    code: str | int = 0
    message: str = 'ok'
    data: object = None

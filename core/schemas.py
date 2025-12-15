from pydantic import BaseModel, Field, field_validator
from typing import Annotated
import re


class BaseCostSchema(BaseModel):
    amount: Annotated[float, Field(..., description="amount in dollar")]
    description: Annotated[str | None, Field()] = None

    @field_validator("amount")
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError("value of amount must be greater than zero!")
        return value

    @field_validator("description")
    def validate_desc(cls, value):

        if value is not None:
            pattern = r"^[a-zA-Z\d\s]*$"
            if not re.match(pattern, value):
                raise ValueError("description can only contain letters and numbers!")
        return value


class CostCreateSchema(BaseCostSchema):
    pass


class CostResponseSchema(BaseCostSchema):
    id: int


class CostUpdateSchema(BaseCostSchema):
    pass

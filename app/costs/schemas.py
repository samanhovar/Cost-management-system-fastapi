from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Annotated
from datetime import datetime
import re


class BaseCostSchema(BaseModel):
    title: Annotated[
        str, Field(..., max_length=128, min_length=3, description="Title of the cost")
    ]
    amount: Annotated[float, Field(..., description="amount in dollar")]
    description: Annotated[str | None, Field()] = None

    @field_validator("amount")
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError("value of amount must be greater than zero!")
        return value

    @field_validator("title", "description")
    def validate_text(cls, value, info: ValidationInfo):
        if value is not None:
            pattern = r"^[a-zA-Z\d\s.,!?'-]*$"
            if not re.match(pattern, value):
                raise ValueError(
                    f"{info.field_name} can only contain letters and numbers!"
                )
        return value


class CostCreateSchema(BaseCostSchema):
    pass


class CostUpdateSchema(BaseCostSchema):
    pass


class CostResponseSchema(BaseCostSchema):
    id: Annotated[int, Field(..., description="Unique identifier of the object")]

    created_date: Annotated[
        datetime, Field(..., description="Creation date and time of the object")
    ]
    updated_date: Annotated[
        datetime, Field(..., description="Updating date and time of the object")
    ]

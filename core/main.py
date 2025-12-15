from typing import Annotated

from fastapi import FastAPI, status, Path, Query, Body, HTTPException

from schemas import CostCreateSchema, CostResponseSchema, CostUpdateSchema

app = FastAPI()

fake_db = []


# read all cost data
@app.get(
    "/costs", status_code=status.HTTP_200_OK, response_model=list[CostResponseSchema]
)
async def read_costs(
    lower_than: Annotated[float | None, Query(alias="lower-bound")] = None,
    higher_than: Annotated[float | None, Query(alias="higher-bound")] = None,
):
    if lower_than and higher_than:
        return [
            item
            for item in fake_db
            if (item["amount"] <= lower_than and item["amount"] >= higher_than)
        ]
    elif lower_than:
        return [item for item in fake_db if item["amount"] <= lower_than]
    elif higher_than:
        return [item for item in fake_db if item["amount"] >= higher_than]
    return fake_db


# added new cost data
@app.post(
    "/costs", status_code=status.HTTP_201_CREATED, response_model=CostResponseSchema
)
async def add_cost(cost: CostCreateSchema):
    if fake_db:
        unique_id = fake_db[-1]["id"] + 1
        new_object = {
            "id": unique_id,
            "amount": cost.amount,
            "description": cost.description,
        }
    else:
        new_object = {
            "id": 1,
            "amount": cost.amount,
            "description": cost.description,
        }
    fake_db.append(new_object)
    return new_object


# read cost data by id
@app.get(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(cost_id: Annotated[int, Path()]):
    for cost in fake_db:
        if cost["id"] == cost_id:
            return cost
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# replace cost data by id
@app.put(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(cost: CostUpdateSchema, cost_id: Annotated[int, Path()]):
    for item in fake_db:
        if item["id"] == cost_id:
            item["amount"] = cost.amount
            item["description"] = cost.description
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# delete cost data by id
@app.delete(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(cost_id: Annotated[int, Path()]):
    for item in fake_db:
        if item["id"] == cost_id:
            fake_db.remove(item)
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# root page
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": "welcome to this service"}

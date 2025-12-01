from typing import Annotated

from fastapi import FastAPI, status, Path, Query, Body, HTTPException

app = FastAPI()

fake_db = []


# read all cost data
@app.get("/costs/", status_code=status.HTTP_200_OK)
async def read_costs():
    return fake_db


# added new cost data
@app.post("/costs/", status_code=status.HTTP_201_CREATED)
async def add_cost(
    amount: Annotated[float, Body()], description: Annotated[str | None, Body()] = None
):
    if fake_db:
        unique_id = fake_db[-1]["id"] + 1
        new_object = {"id": unique_id, "description": description, "amount": amount}
    else:
        new_object = {"id": 1, "description": description, "amount": amount}
    fake_db.append(new_object)
    return {"message": "new data saved successfully"}


# read cost data by id
@app.get("/costs/{cost_id}", status_code=status.HTTP_200_OK)
async def read_cost_by_id(cost_id: Annotated[int, Path()]):
    for cost in fake_db:
        if cost["id"] == cost_id:
            return cost
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# replace cost data by id
@app.put("/costs/{cost_id}", status_code=status.HTTP_200_OK)
async def read_cost_by_id(
    cost_id: Annotated[int, Path()],
    amount: Annotated[float, Body()],
    description: Annotated[str | None, Body()] = None,
):
    for cost in fake_db:
        if cost["id"] == cost_id:
            cost["amount"] = amount
            cost["description"] = description
            return {"message": "cost data updated successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# delete cost data by id
@app.delete("/costs/{cost_id}", status_code=status.HTTP_200_OK)
async def read_cost_by_id(cost_id: Annotated[int, Path()]):
    for cost in fake_db:
        if cost["id"] == cost_id:
            fake_db.remove(cost)
            return {"message": "cost data deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")

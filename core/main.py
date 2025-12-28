from typing import Annotated

from fastapi import FastAPI, status, Path, Query, Body, HTTPException, Depends
from fastapi.responses import JSONResponse

from database import get_db, Cost
from sqlalchemy.orm import Session

from schemas import CostCreateSchema, CostResponseSchema, CostUpdateSchema

from contextlib import asynccontextmanager


# adding life span
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan)


# read all cost data
@app.get(
    "/costs", status_code=status.HTTP_200_OK, response_model=list[CostResponseSchema]
)
async def read_costs(
        lower_than: Annotated[float | None, Query(alias="lower-bound")] = None,
        higher_than: Annotated[float | None, Query(alias="higher-bound")] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Cost)

    if lower_than and higher_than:
        query = query.filter(Cost.amount >= higher_than, Cost.amount <= lower_than)
    elif lower_than:
        query = query.filter(Cost.amount <= lower_than)
    elif higher_than:
        query = query.filter(Cost.amount >= higher_than)

    result = query.all()

    return result


# added new cost data
@app.post(
    "/costs", status_code=status.HTTP_201_CREATED, response_model=CostResponseSchema
)
async def add_cost(request: CostCreateSchema, db: Session = Depends(get_db)):
    
    new_cost = Cost(amount=request.amount, description=request.description)
    db.add(new_cost)
    db.commit()
    return new_cost
    

# read cost data by id
@app.get(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(cost_id: Annotated[int, Path()], db: Session = Depends(get_db)):
    cost = db.query(Cost).filter_by(id=cost_id).one_or_none()
    if cost:
        return cost
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# replace cost data by id
@app.put(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(request: CostUpdateSchema, cost_id: Annotated[int, Path()], db: Session = Depends(get_db)):
    cost = db.query(Cost).filter_by(id=cost_id).one_or_none()
    if cost:
        cost.amount = request.amount
        if request.description:
            cost.description = request.description
        db.commit()
        db.refresh(cost)
        return cost
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# delete cost data by id
@app.delete(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(cost_id: Annotated[int, Path()], db: Session = Depends(get_db)):
    cost = db.query(Cost).filter_by(id=cost_id).one_or_none()
    if cost:
        db.delete(cost)
        db.commit()
        return JSONResponse(content={"detail": "object removed successfully"}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found error")


# root page
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": "welcome to this service"}

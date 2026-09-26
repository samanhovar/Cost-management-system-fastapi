from typing import Annotated

from fastapi import APIRouter, status, Path, Query, Body, HTTPException, Depends
from fastapi.responses import JSONResponse

from costs.models import Cost
from costs.schemas import CostCreateSchema, CostResponseSchema, CostUpdateSchema

# sqlalchemy imports
from sqlalchemy.orm import Session
from core.database import get_db

# Authentication for costs routes
from auth.jwt_auth import get_authenticated_user
from users.models import UserModel

router = APIRouter(tags=["costs"], prefix="/costs")


# read all cost data
@router.get(
    "/costs", status_code=status.HTTP_200_OK, response_model=list[CostResponseSchema]
)
async def read_costs(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(get_authenticated_user)],
    lower_than: Annotated[float | None, Query(alias="lower-bound")] = None,
    higher_than: Annotated[float | None, Query(alias="higher-bound")] = None,
):
    query = db.query(Cost).filter_by(user_id=user.id)

    if lower_than and higher_than:
        query = query.filter(Cost.amount >= higher_than, Cost.amount <= lower_than)
    elif lower_than:
        query = query.filter(Cost.amount <= lower_than)
    elif higher_than:
        query = query.filter(Cost.amount >= higher_than)

    result = query.all()

    return result


# add new cost data
@router.post(
    "/costs",
    status_code=status.HTTP_201_CREATED,
    response_model=CostResponseSchema,
)
async def add_cost(
    request: CostCreateSchema,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(get_authenticated_user)],
):
    data = request.model_dump()
    data.update({"user_id": user.id})
    new_cost = Cost(**data)
    db.add(new_cost)
    db.commit()
    db.refresh(new_cost)
    return new_cost


# read cost data by id
@router.get(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def read_cost_by_id(
    cost_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(get_authenticated_user)],
):
    cost = db.query(Cost).filter_by(user_id=user.id, id=cost_id).one_or_none()
    if not cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not found error"
        )
    return cost


# replace cost data by id
@router.put(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def replace_cost_by_id(
    request: CostUpdateSchema,
    cost_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(get_authenticated_user)],
):
    cost = db.query(Cost).filter_by(user_id=user.id, id=cost_id).one_or_none()
    if not cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not found error"
        )

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(cost, field, value)

    db.commit()
    db.refresh(cost)

    return cost


# delete cost data by id
@router.delete(
    "/costs/{cost_id}",
    status_code=status.HTTP_200_OK,
    response_model=CostResponseSchema,
)
async def delete_cost_by_id(
    cost_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[UserModel, Depends(get_authenticated_user)],
):
    cost = db.query(Cost).filter_by(user_id=user.id, id=cost_id).one_or_none()

    if not cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not found error"
        )

    db.delete(cost)
    db.commit()

    return JSONResponse(
        content={"detail": "object removed successfully"},
        status_code=status.HTTP_200_OK,
    )

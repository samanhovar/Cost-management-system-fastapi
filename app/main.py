from fastapi import FastAPI, status

from contextlib import asynccontextmanager

from costs.routes import router as costs_router
from users.routes import router as users_router


target_metadata = [
    {
        "name": "costs",
        "description": "reading and managing list of costs",
        "externalDocs": {
            "description": "more about this project",
            "url": "https://example.com/docs",
        },
    }
]


# adding life span
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")


app = FastAPI(
    title="Costs management app",
    version="0.0.2",
    contact={
        "name": "Saman Ghasemi",
        "url": "https://github.com/samanhovar",
        "email": "samanghasemidesk@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    openapi_tags=target_metadata,
)


# root page
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    response = {
        "message": "welcome to this service",
        
    }
    return response


app.include_router(costs_router)
app.include_router(users_router)

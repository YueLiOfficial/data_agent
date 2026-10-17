
import uuid

from fastapi import FastAPI, Request
import uvicorn

from app.api.query_router import query_router
from app.core.context import set_req_id
from app.core.lifespan import lifespan


app = FastAPI(lifespan=lifespan)

app.include_router(query_router)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = uuid.uuid4()
    set_req_id(str(req_id))

    response = await call_next(request)

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
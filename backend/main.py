from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Returned Message: {data} From Server")
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        await websocket.close(code=1000)


def check_token(token: str):
    if token != "my-secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token


router = APIRouter(dependencies=[Depends(check_token)])


@router.get("/items/")
def ge_items():
    return {"message": "Access granted, you can view the items."}


@app.get("/public/")
def read_public():
    return {"message": "Thisis a public endpoint."}


app.include_router(router, prefix="/api")

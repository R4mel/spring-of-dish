from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return "Hello FastAPI!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
    # host 무조건 작성, 작성안하면 외부에서 접속 X
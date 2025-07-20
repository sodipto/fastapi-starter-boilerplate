from fastapi import FastAPI

app = FastAPI(
    title="Python FastAPI Boilerplate",
    docs_url="/swagger",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

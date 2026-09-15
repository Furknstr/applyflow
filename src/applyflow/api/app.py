from fastapi import FastAPI

app = FastAPI(title="ApplyFlow", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

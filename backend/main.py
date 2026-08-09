from fastapi import FastAPI

app = FastAPI(title="Mini Business Inventory Backend")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "healthy"}

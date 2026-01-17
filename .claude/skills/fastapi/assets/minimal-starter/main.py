"""
Minimal FastAPI Starter
A simple hello world FastAPI application.
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Minimal FastAPI App",
    description="A simple starter FastAPI application",
    version="1.0.0"
)


class Message(BaseModel):
    """Simple message model."""
    message: str


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    """
    Example endpoint with path and query parameters.

    - **item_id**: ID of the item (path parameter)
    - **q**: Optional query parameter
    """
    return {"item_id": item_id, "q": q}


@app.post("/echo")
async def echo_message(message: Message):
    """
    Echo endpoint that returns the received message.

    Example request body:
    {
        "message": "Hello FastAPI"
    }
    """
    return {"received": message.message}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

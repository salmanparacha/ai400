from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the agent", examples=["Hello, how are you?"])
    session_id: str = Field(default="default-session", description="Session ID for conversation history", examples=["test-session-1"])
    model_provider: str = Field("nova-lite", description="Model provider to use (nova-lite or anthropic)", examples=["nova-lite"])

class ChatResponse(BaseModel):
    response: str
    session_id: str

"""Pydantic schemas for ML API."""
from pydantic import BaseModel


class TextInput(BaseModel):
    """Input schema for text classification."""
    text: str


class SentimentPrediction(BaseModel):
    """Output schema for sentiment analysis."""
    text: str
    sentiment: str
    confidence: float


class ImageInput(BaseModel):
    """Input schema for image classification."""
    image_base64: str


class ImagePrediction(BaseModel):
    """Output schema for image classification."""
    predictions: list[dict[str, float]]
    top_prediction: str
    confidence: float


class BatchTextInput(BaseModel):
    """Input schema for batch text processing."""
    texts: list[str]


class BatchPrediction(BaseModel):
    """Output schema for batch predictions."""
    predictions: list[SentimentPrediction]

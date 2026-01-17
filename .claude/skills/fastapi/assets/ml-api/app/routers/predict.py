"""Prediction endpoints."""
from fastapi import APIRouter, HTTPException

from app.schemas import (
    TextInput,
    SentimentPrediction,
    BatchTextInput,
    BatchPrediction
)
from app.models.model_loader import get_model

router = APIRouter()


@router.post("/predict/sentiment", response_model=SentimentPrediction)
async def predict_sentiment(input_data: TextInput):
    """
    Predict sentiment of input text.

    Returns sentiment classification (positive/negative/neutral) with confidence score.
    """
    model = get_model("sentiment")
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    sentiment, confidence = model.predict(input_data.text)

    return SentimentPrediction(
        text=input_data.text,
        sentiment=sentiment,
        confidence=confidence
    )


@router.post("/predict/sentiment/batch", response_model=BatchPrediction)
async def predict_sentiment_batch(input_data: BatchTextInput):
    """
    Predict sentiment for multiple texts in batch.

    More efficient than making individual requests for multiple texts.
    """
    model = get_model("sentiment")
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    results = model.predict_batch(input_data.texts)

    predictions = [
        SentimentPrediction(
            text=text,
            sentiment=sentiment,
            confidence=confidence
        )
        for text, (sentiment, confidence) in zip(input_data.texts, results)
    ]

    return BatchPrediction(predictions=predictions)

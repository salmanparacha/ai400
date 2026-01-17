# FastAPI ML API Template

A template for serving machine learning models with FastAPI.

## Features

- Model loading on startup with lifecycle management
- Batch prediction support
- Mock sentiment analysis model (replace with your own)
- Easy to extend for different model types
- Proper error handling for model unavailability

## Project Structure

```
.
├── main.py                      # Application entry point
├── app/
│   ├── routers/
│   │   └── predict.py          # Prediction endpoints
│   ├── models/
│   │   └── model_loader.py     # Model loading logic
│   └── schemas.py              # Pydantic schemas
└── requirements.txt
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Add your ML models to a `models/` directory

3. Update `app/models/model_loader.py` to load your actual models

## Running

```bash
fastapi dev main.py
```

## API Endpoints

- `POST /api/v1/predict/sentiment` - Predict sentiment for single text
- `POST /api/v1/predict/sentiment/batch` - Batch prediction for multiple texts
- `GET /models` - List all loaded models

## Example Requests

### Single Prediction

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is great!"}'
```

Response:
```json
{
  "text": "This product is great!",
  "sentiment": "positive",
  "confidence": 0.92
}
```

### Batch Prediction

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "This is amazing!",
      "I hate this product",
      "It works okay"
    ]
  }'
```

## Adding Your Own Models

1. Save your trained model to `models/` directory
2. Update `app/models/model_loader.py`:

```python
def load_models() -> dict[str, Any]:
    models = {}

    # Example: scikit-learn
    import joblib
    models["my_model"] = joblib.load("models/my_model.pkl")

    # Example: PyTorch
    import torch
    model = torch.load("models/pytorch_model.pth")
    model.eval()
    models["pytorch_model"] = model

    return models
```

3. Add prediction endpoints in `app/routers/predict.py`
4. Define input/output schemas in `app/schemas.py`

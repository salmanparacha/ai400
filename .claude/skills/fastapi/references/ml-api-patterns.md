# FastAPI ML API Patterns

Best practices for serving machine learning models with FastAPI.

## Table of Contents

- Model Loading
- Prediction Endpoints
- Batch Processing
- Model Versioning
- Input Validation
- Performance Optimization
- Error Handling

## Model Loading

### Loading on Startup

Load models during application startup to avoid loading on every request:

```python
from contextlib import asynccontextmanager
import joblib
import torch

models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    models["sklearn_model"] = joblib.load("models/model.pkl")

    # PyTorch model
    model = torch.load("models/pytorch_model.pth")
    model.eval()  # Set to evaluation mode
    models["pytorch_model"] = model

    yield
    # Shutdown: cleanup
    models.clear()

app = FastAPI(lifespan=lifespan)
```

### Lazy Loading

For large models, load on first use:

```python
class ModelManager:
    def __init__(self):
        self._models = {}

    def get_model(self, model_name: str):
        if model_name not in self._models:
            self._models[model_name] = self._load_model(model_name)
        return self._models[model_name]

    def _load_model(self, model_name: str):
        # Load model from disk
        return joblib.load(f"models/{model_name}.pkl")

model_manager = ModelManager()
```

## Prediction Endpoints

### Single Prediction

```python
from pydantic import BaseModel

class PredictionInput(BaseModel):
    features: list[float]

class PredictionOutput(BaseModel):
    prediction: float
    confidence: float | None = None

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    model = models["sklearn_model"]

    # Make prediction
    features = np.array(input_data.features).reshape(1, -1)
    prediction = model.predict(features)[0]

    # Get confidence if available
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        confidence = float(max(proba))

    return PredictionOutput(
        prediction=float(prediction),
        confidence=confidence
    )
```

### Batch Prediction

More efficient for multiple inputs:

```python
class BatchPredictionInput(BaseModel):
    inputs: list[list[float]]

class BatchPredictionOutput(BaseModel):
    predictions: list[float]

@app.post("/predict/batch", response_model=BatchPredictionOutput)
async def predict_batch(input_data: BatchPredictionInput):
    model = models["sklearn_model"]

    # Convert to numpy array
    features = np.array(input_data.inputs)

    # Batch prediction
    predictions = model.predict(features)

    return BatchPredictionOutput(
        predictions=predictions.tolist()
    )
```

## Input Validation

### Feature Validation

```python
from pydantic import BaseModel, field_validator

class ModelInput(BaseModel):
    age: int
    income: float
    credit_score: int

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if not 18 <= v <= 100:
            raise ValueError("Age must be between 18 and 100")
        return v

    @field_validator("credit_score")
    @classmethod
    def validate_credit_score(cls, v):
        if not 300 <= v <= 850:
            raise ValueError("Credit score must be between 300 and 850")
        return v
```

### Image Input

```python
import base64
from PIL import Image
from io import BytesIO

class ImageInput(BaseModel):
    image_base64: str

def decode_image(base64_string: str) -> Image.Image:
    """Decode base64 image string to PIL Image."""
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))
    return image

@app.post("/predict/image")
async def predict_image(input_data: ImageInput):
    # Decode image
    image = decode_image(input_data.image_base64)

    # Preprocess
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0

    # Predict
    model = models["image_model"]
    prediction = model.predict(np.expand_dims(image_array, 0))

    return {"prediction": prediction.tolist()}
```

## Model Versioning

### Multiple Model Versions

```python
models = {
    "v1": None,
    "v2": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    models["v1"] = joblib.load("models/model_v1.pkl")
    models["v2"] = joblib.load("models/model_v2.pkl")
    yield
    models.clear()

@app.post("/v1/predict")
async def predict_v1(input_data: PredictionInput):
    model = models["v1"]
    prediction = model.predict([input_data.features])
    return {"prediction": float(prediction[0]), "version": "v1"}

@app.post("/v2/predict")
async def predict_v2(input_data: PredictionInput):
    model = models["v2"]
    prediction = model.predict([input_data.features])
    return {"prediction": float(prediction[0]), "version": "v2"}
```

## Performance Optimization

### GPU Support for PyTorch

```python
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@asynccontextmanager
async def lifespan(app: FastAPI):
    model = torch.load("models/model.pth")
    model = model.to(device)
    model.eval()
    models["pytorch_model"] = model
    yield

@app.post("/predict/pytorch")
async def predict_pytorch(input_data: PredictionInput):
    model = models["pytorch_model"]

    with torch.no_grad():
        features = torch.tensor([input_data.features]).to(device)
        prediction = model(features)

    return {"prediction": prediction.cpu().numpy().tolist()}
```

### Async Preprocessing

For CPU-intensive preprocessing, use background tasks:

```python
from fastapi import BackgroundTasks
import asyncio

async def preprocess_data(data: list) -> np.ndarray:
    # Run in thread pool for CPU-intensive work
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: np.array(data)
    )

@app.post("/predict/async")
async def predict_async(input_data: PredictionInput):
    features = await preprocess_data(input_data.features)
    model = models["sklearn_model"]
    prediction = model.predict(features.reshape(1, -1))
    return {"prediction": float(prediction[0])}
```

## Error Handling

### Model Not Loaded

```python
def get_model(model_name: str):
    model = models.get(model_name)
    if model is None:
        raise HTTPException(503, f"Model '{model_name}' not loaded")
    return model

@app.post("/predict")
async def predict(input_data: PredictionInput):
    model = get_model("sklearn_model")
    # ... prediction logic
```

### Invalid Input Shape

```python
@app.post("/predict")
async def predict(input_data: PredictionInput):
    model = models["sklearn_model"]

    try:
        features = np.array(input_data.features).reshape(1, -1)
        prediction = model.predict(features)
        return {"prediction": float(prediction[0])}
    except ValueError as e:
        raise HTTPException(
            400,
            f"Invalid input shape: {str(e)}"
        )
```

## Monitoring

### Prediction Logging

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(input_data: PredictionInput):
    start_time = datetime.utcnow()

    model = models["sklearn_model"]
    prediction = model.predict([input_data.features])

    latency = (datetime.utcnow() - start_time).total_seconds()

    logger.info(
        f"Prediction made: latency={latency:.3f}s, "
        f"input_shape={len(input_data.features)}"
    )

    return {"prediction": float(prediction[0])}
```

### Model Metadata Endpoint

```python
@app.get("/model/info")
async def model_info():
    """Get information about loaded models."""
    return {
        "models": list(models.keys()),
        "device": str(device) if "device" in globals() else "cpu",
        "framework_versions": {
            "pytorch": torch.__version__ if "torch" in globals() else None,
            "sklearn": sklearn.__version__ if "sklearn" in globals() else None
        }
    }
```

## Text Classification Example

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model and tokenizer
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    models["tokenizer"] = AutoTokenizer.from_pretrained(model_name)
    models["classifier"] = AutoModelForSequenceClassification.from_pretrained(model_name)
    yield

class TextInput(BaseModel):
    text: str

@app.post("/classify")
async def classify_text(input_data: TextInput):
    tokenizer = models["tokenizer"]
    model = models["classifier"]

    # Tokenize
    inputs = tokenizer(
        input_data.text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # Get label
    label_id = predictions.argmax().item()
    confidence = predictions[0][label_id].item()

    labels = ["negative", "positive"]
    return {
        "text": input_data.text,
        "label": labels[label_id],
        "confidence": confidence
    }
```

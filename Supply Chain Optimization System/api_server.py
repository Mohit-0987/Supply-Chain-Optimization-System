from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

# Initialize the FastAPI app
app = FastAPI(title="Supply Chain API")


# Define the request model for prediction
class PredictionRequest(BaseModel):
    product_id: str
    days_ahead: int = 7


@app.get("/health")
def health_check():
    """Health check endpoint to confirm the API is running."""
    return {"status": "healthy"}


@app.post("/predict-demand")
def predict_demand(request: PredictionRequest):
    """
    Predicts demand for a given product.
    Note: This is a simplified example using random data.
    """
    try:
        # For this example, we'll return a random prediction.
        prediction = random.randint(50, 200) * request.days_ahead

        return {
            "product_id": request.product_id,
            "predicted_demand_for_next_days": request.days_ahead,
            "predicted_demand": prediction,
            "confidence": 0.85
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load artifacts
model = joblib.load("phishing_model.pkl")
selected_features = joblib.load("selected_features.pkl")

class FeaturesPayload(BaseModel):
    features: dict

@app.post("/predict")
def predict(payload: FeaturesPayload):
    try:
        # Create input DataFrame
        input_data = payload.features
        
        # Ensure ALL required model features exist; fill missing with default 0
        for feat in selected_features:
            if feat not in input_data:
                input_data[feat] = 0

        # Filter and reorder exactly according to selected_features.pkl
        df_input = pd.DataFrame([input_data])[selected_features]

        # Run inference
        prediction = model.predict(df_input)[0]
        probs = model.predict_proba(df_input)[0]

        return {
            "prediction": int(prediction),
            "label": "Phishing" if prediction == 1 else "Legitimate",
            "confidence": float(max(probs))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI, FileResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from funcs import *
import joblib
import os
import pickle

app = FastAPI()


class Item(BaseModel):
    name: str
    year: int
    selling_price: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


class Items(BaseModel):
    objects: List[Item]

@app.get("/")
def read_root():
    return {"message": "Welcome to the car price prediction service!"}

@app.post("/predict_item")
def predict_item(item: Item) -> float:
    input_data = pd.DataFrame([item.dict()])
    input_features = preprocess_input_data(input_data)

    model = load_model(MODEL_NAME)
    prediction = model.predict(input_features)
    fin_predictions = np.round(np.exp(prediction), 2)

    return float(fin_predictions[0])


@app.post("/predict_items")
def predict_items(items: Items) -> List[float]:
    data_result = items.copy()
    input_data = pd.DataFrame([item.dict() for item in items.objects])
    input_features = preprocess_input_data(input_data)
    # remove selling_price
    # elastig regression
    model = load_model(MODEL_NAME)
    predictions = model.predict(input_features)
    fin_predictions = np.round(np.exp(predictions), 2)

    data_result['predictions'] = fin_predictions
    data_result.to_csv(index=False)
    return FileResponse(path='prediction.csv', media_type='text/csv', filename='predictions_for_items.csv')


def preprocess_input_data(data: pd.DataFrame) -> pd.DataFrame:
    # Implement your preprocessing steps here (e.g., handle categorical variables, scaling, etc.)
    # ...
    data.drop('selling_price', axis=1, inplace=True)
    convert_to_numeric(data)
    data['seats'] = data['seats'].astype('cateogory')
    data[['torque', 'max_torque_rpm']] = data['torque'].apply(lambda x: pd.Series(split_torque_column(x)))
    fill_with_median() # надо медианы из трейна загрузить


    # add features
    data['year_sq'] = data['year'] ** 2
    data['per_l']
    cat_cols = list(data.describe(include='object').columns)
    
    ohe = load_model(OHE_NAME)
    scaler = load_model(SCALER_NAME)

    cat_data = one_hot_enc(data, cat_cols, ohe)
    processed_data = scaler.transform(cat_data)

    return processed_data


def load_model(file_name: str , directory='models') -> LinearRegression:

    file_path = os.path.join(os.getcwd(), directory, file_name)
    with open(file_path, 'rb') as file:
        model = pickle.load(file)
    return model    
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import io
import pandas as pd
import numpy as np
from utils.funcs import *
import joblib
import os

model = joblib.load(MODEL_NAME)
scaler = joblib.load(SCALER_NAME)
ohe = joblib.load(OHE_NAME)

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

class ItemFile(BaseModel):
    file: UploadFile

@app.get("/")
def read_root():
    return {"message": "Welcome to the car price prediction service!"}

@app.post("/predict_item")
def predict_item(item: Item) -> float:
    input_data = pd.DataFrame.from_dict(item.model_dump())
    input_features = preprocess_input_data(input_data)

    prediction = model.predict(input_features)
    fin_predictions = np.round(np.exp(prediction), 2)

    return float(fin_predictions[0])


@app.post("/predict_items")
def predict_items(file: UploadFile) -> FileResponse:
    content = file.file.read()
    data = pd.read_csv(io.BytesIO(content))
    file.file.close()

    data_result = data.copy()
    input_features = preprocess_input_data(data)

    predictions = model.predict(input_features)
    fin_predictions = np.round(np.exp(predictions), 2)

    data_result['predictions'] = fin_predictions
    data_result.to_csv(index=False)
    return FileResponse(path='test_sample.csv',
                        media_type='text/csv',
                        filename='predictions_for_test.csv')


def preprocess_input_data(data: pd.DataFrame) -> pd.DataFrame:
    data.drop(['selling_price', 'name'], axis=1, inplace=True)
    convert_to_numeric(data)
    data[['torque', 'max_torque_rpm']] = data['torque'].apply(lambda x: pd.Series(split_torque_column(x)))

    # add features
    data['year_sq'] = data['year'] ** 2
    data['power_per_l'] = data['max_power'] / data['engine']

    cat_cols = list(data.describe(include='object').columns)
    cat_cols.append('seats')

    for col in cat_cols:
        data[col] = data[col].astype('category')

    cat_data = one_hot_enc(data, cat_cols, ohe)
    processed_data = scaler.transform(cat_data)

    return processed_data


# def load_model(file_name: str, directory='models'):
#
#     file_path = os.path.join(os.getcwd(), directory, file_name)
#     print(file_path)
#     with open(file_path, 'rb') as file:
#         model = pickle.load(file)
#     return model

import pandas as pd 
import numpy as np
import re
import joblib


MODEL_NAME = 'best_model.pkl'
SCALER_NAME = ''
OHE_NAME = ''

def convert_to_kmpl(mileage):
    """
    Convert mileage column with units to float with values
    """
    mil = float(str(mileage).split()[0])
    if 'km/kg' in str(mileage):
        return mil * 0.75
    else:
        return mil
    
def convert_to_numeric(df):
    df['engine'] = df['engine'].apply(lambda x: str(x).split()[0])
    df['mileage'] = df['mileage'].apply(convert_to_kmpl)
    df['max_power'] = df['max_power'].replace('0', np.nan)
    df['max_power'] = df['max_power'].apply(lambda x: str(x)[:-4])
    numeric_cols = ['engine', 'max_power']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

def fill_with_median(df_train, df_test, cols=['engine', 'max_power','mileage','torque','max_torque_rpm']):
    medians = df_train[cols].median()
    seat_mode = df_train['seats'].mode()[0]
    df_train[cols] = df_train[cols].fillna(medians)
    df_train['seats'] = df_train['seats'].fillna(seat_mode)
    df_test[cols] = df_test[cols].fillna(medians)    
    df_test['seats'] = df_test['seats'].fillna(seat_mode)

def split_torque_column(row: str):
    if pd.isna(row):
        return np.nan, np.nan
    
    lower_str = row.lower()
    
    numbers_pattern = re.findall(r'\d+(?:[.,]\d+)?', lower_str)
    numbers = [number.replace(',', '') for number in numbers_pattern]
    units = re.findall(r'nm|kgm|rpm', lower_str)

    torque_value = float(numbers[0])

    torque = torque_value if 'nm' in units else round(torque_value * 9.8066, 2)

    max_torque_rpm = float(numbers[-1]) if not '+/-' in row else float(numbers[-2])

    return torque, max_torque_rpm

def one_hot_enc(df, cat_cols, ohe=None, model_path='ohe_model.pkl'):
    if ohe is None:
        ohe = joblib.load(model_path)

    cat_features = df[cat_cols]
    num_features = df.drop(columns=cat_cols)

    if not cat_features.empty:
        values = ohe.transform(cat_features)
        labels = ohe.get_feature_names_out()
        df_encoded = pd.DataFrame(values, columns=labels, index=df.index)
    else:
        df_encoded = pd.DataFrame()

    df_result = pd.concat([num_features, df_encoded], axis=1)

    return df_result


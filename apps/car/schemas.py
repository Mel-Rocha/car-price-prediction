from typing import List
from pydantic import BaseModel, validator
from fastapi import  UploadFile


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

    @validator("mileage")
    def validate_mileage(cls, value):
        try:
            parts = value.split()
            if len(parts) != 2 or not parts[0].replace(".", "", 1).isdigit() or not parts[1].isalpha():
                raise ValueError("Mileage deve estar no formato 'valor unidade', como '23.4 kmpl'.")
        except Exception as e:
            raise ValueError(f"Mileage inválido: {value}. {str(e)}")
        return value


class Items(BaseModel):
    objects: List[Item]

class ItemFile(BaseModel):
    file: UploadFile

import re
from typing import List
from pydantic import BaseModel, validator
from fastapi import  UploadFile

from apps.car.utils import validate_torque


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

    @validator("torque")
    def validate_torque_format(cls, value):
        if not validate_torque(value):
            raise ValueError("O torque deve estar no formato '250Nm@4500rpm', '190Nm@ 2000rpm', '350Nm@1750-2500rpm', "
                             "'51Nm@4000+/-500rpm', '350Nm', or '4500rpm'")
        return value

    @validator("max_power")
    def validate_max_power(cls, value):
        if not re.match(r'^\d+(\.\d+)? bhp$', value):
            raise ValueError("max_power deve estar no formato 'numero bhp', como '75 bhp'.")
        return value

    @validator("km_driven")
    def validate_km_driven(cls, value):
        if len(str(value)) > 19:
            raise ValueError("km_driven deve ter no máximo 19 dígitos. Dica: use uma média de 5 digitos"
                             "para obter um resultado mais preciso.")
        return value

    @validator("year")
    def validate_year(cls, value):
        if value < 1900 or value > 2100:  # Assuming cars are not older than 1886 and not from the future
            raise ValueError("Ano fora do intervalo permitido: 1900 à 2100.")
        return value

    #  validation on categorical data
    @validator("fuel")
    def validate_fuel(cls, value):
        allowed_fuels = {'Diesel', 'Petrol', 'LPG', 'CNG'}
        if value not in allowed_fuels:
            raise ValueError(f"O combustível deve ser um dos: {allowed_fuels}")
        return value

    @validator("transmission")
    def validate_transmission(cls, value):
        allowed_transmissions = {'Manual', 'Automatic'}
        if value not in allowed_transmissions:
            raise ValueError(f"A transmissão deve ser uma das: {allowed_transmissions}")
        return value

    @validator("seller_type")
    def validate_seller_type(cls, value):
        allowed_seller_types = {'Individual', 'Dealer', 'Trustmark Dealer'}
        if value not in allowed_seller_types:
            raise ValueError(f"O tipo de vendedor deve ser um dos: {allowed_seller_types}")
        return value

    @validator("owner")
    def validate_owner(cls, value):
        allowed_owners = {'First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner', 'Test Drive Car'}
        if value not in allowed_owners:
            raise ValueError(f"O proprietário deve ser um dos: {allowed_owners}")
        return value

    @validator("seats")
    def validate_seats(cls, value):
        allowed_seats = {5.0, 4.0, 7.0, 8.0, 6.0, 9.0, 10.0, 14.0, 2.0}
        if value not in allowed_seats:
            raise ValueError(f"O número de assentos deve ser um dos: {allowed_seats}")
        return value


class Items(BaseModel):
    objects: List[Item]

class ItemFile(BaseModel):
    file: UploadFile

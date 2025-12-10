from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.data_classes.http import ResponseSuccess

PhoneNumber.phone_format = "E164"


class AddressData(BaseModel):
    phone_number: PhoneNumber
    address: str


class AddressResponse(ResponseSuccess):
    result: AddressData


class CreateAddressRequest(BaseModel):
    phone_number: PhoneNumber
    address: str


class UpdateAddressRequest(BaseModel):
    address: str

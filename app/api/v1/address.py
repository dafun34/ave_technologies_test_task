from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette import status

from app.containers import Container
from app.data_classes.address import (
    AddressResponse,
    AddressData,
    CreateAddressRequest,
    UpdateAddressRequest,
)
from app.services.clients.redis import RedisClient

router = APIRouter(prefix="/v1/address", tags=["addresses"])


@router.get("/{phone_number}", response_model=AddressResponse)
@inject
async def get_address_by_phone(
    phone_number: PhoneNumber,
    redis_client: RedisClient = Depends(Provide[Container.redis_client]),
):
    """Получить адрес по номеру телефона."""
    address = await redis_client.get_address_by_phone(phone_number)
    if address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return AddressResponse(result=AddressData(address=address, phone_number=phone_number))


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_address(
    request_data: CreateAddressRequest,
    redis_client: RedisClient = Depends(Provide[Container.redis_client]),
):
    """Создать новую запись телефон -> адрес."""
    exists = await redis_client.get_address_by_phone(request_data.phone_number)
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already exists")

    await redis_client.set_address_by_phone(request_data.phone_number, request_data.address)
    return AddressResponse(result=AddressData(address=request_data.address, phone_number=request_data.phone_number))


@router.put("/{phone_number}", response_model=AddressResponse)
@inject
async def update_address(
    phone_number: PhoneNumber,
    request_data: UpdateAddressRequest,
    redis_client: RedisClient = Depends(Provide[Container.redis_client]),
):
    """Обновить адрес по телефону."""
    exists = await redis_client.get_address_by_phone(phone_number)
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found")
    await redis_client.set_address_by_phone(phone_number, request_data.address)
    return AddressResponse(result=AddressData(address=request_data.address, phone_number=phone_number))


@router.delete("/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_address(
    phone_number: PhoneNumber,
    redis_client: RedisClient = Depends(Provide[Container.redis_client]),
):
    """Удалить адрес по телефону."""
    deleted = await redis_client.delete_address_by_phone(phone_number)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return

import pytest

from app.data_classes.address import AddressResponse, AddressData

PHONE_NUMBER = "+79061112233"
ADDRESS = "Лавочкина"
NEW_ADDRESS = "Советская"
NON_EXISTENT_PHONE = "+79990001122"


def test_create_address(client):
    payload = {"phone_number": PHONE_NUMBER, "address": ADDRESS}
    expected_response = AddressResponse(result=AddressData(address=ADDRESS, phone_number=PHONE_NUMBER))
    response = client.post("/api/v1/address", json=payload)
    assert response.status_code == 201
    assert response.json() == expected_response.model_dump(mode="json")


def test_get_address(client):
    # сначала создадим адрес
    payload = {"phone_number": PHONE_NUMBER, "address": ADDRESS}
    response = client.post("/api/v1/address", json=payload)
    assert response.status_code == 201
    # теперь получим адрес
    response = client.get(f"/api/v1/address/{PHONE_NUMBER}")
    assert response.status_code == 200
    expected_response = AddressResponse(result=AddressData(address=ADDRESS, phone_number=PHONE_NUMBER))
    assert response.json() == expected_response.model_dump(mode="json")


def test_update_address(client):
    # сначала создадим адрес
    payload = {"phone_number": PHONE_NUMBER, "address": ADDRESS}
    response = client.post("/api/v1/address", json=payload)
    assert response.status_code == 201
    # обновим адрес
    response = client.put(f"/api/v1/address/{PHONE_NUMBER}", json={"address": NEW_ADDRESS})
    assert response.status_code == 200
    expected_response = AddressResponse(result=AddressData(address=NEW_ADDRESS, phone_number=PHONE_NUMBER))
    assert response.json() == expected_response.model_dump(mode="json")


def test_delete_address(client):
    # сначала создадим адрес
    payload = {"phone_number": PHONE_NUMBER, "address": ADDRESS}
    response = client.post("/api/v1/address", json=payload)
    assert response.status_code == 201
    # удалим адрес
    response = client.delete(f"/api/v1/address/{PHONE_NUMBER}")
    assert response.status_code == 204


def test_create_duplicate(client):
    payload = {"phone_number": PHONE_NUMBER, "address": ADDRESS}
    # первый запрос должен пройти успешно
    resp1 = client.post("/api/v1/address", json=payload)
    assert resp1.status_code == 201
    # второй запрос с тем же номером должен вернуть ошибку (400 или 409)
    resp2 = client.post("/api/v1/address", json=payload)
    assert resp2.status_code == 409


def test_create_missing_phone(client):
    # пропущено обязательное поле phone_number -> валидация FastAPI: 422
    payload = {"address": ADDRESS}
    resp = client.post("/api/v1/address", json=payload)
    assert resp.status_code == 422


def test_get_update_delete_nonexistent(client):
    # получение несуществующей записи -> 404
    resp = client.get(f"/api/v1/address/{NON_EXISTENT_PHONE}")
    assert resp.status_code == 404

    # обновление несуществующей записи -> 404
    resp = client.put(f"/api/v1/address/{NON_EXISTENT_PHONE}", json={"address": "Новый"})
    assert resp.status_code == 404

    # удаление несуществующей записи -> 404 (или 204/200 в зависимости от реализации, тут ожидаем 404)
    resp = client.delete(f"/api/v1/address/{NON_EXISTENT_PHONE}")
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "invalid_phone",
    [
        "12345",
        "phone123",
        "79061112233abc",
        "96061112233",
    ],
)
def test_create_invalid_phone(client, invalid_phone):
    payload = {"phone_number": invalid_phone, "address": ADDRESS}
    resp = client.post("/api/v1/address", json=payload)
    assert resp.status_code == 422


@pytest.mark.parametrize(
    "valid_phone",
    [
        "+79061112233",
        "+7(906)111-22-33",
        "+7 906 111 22 33",
        "+7-906-111-22-33",
    ],
)
def test_create_valid_phone(client, valid_phone):
    payload = {"phone_number": valid_phone, "address": ADDRESS}
    resp = client.post("/api/v1/address", json=payload)
    assert resp.status_code == 201

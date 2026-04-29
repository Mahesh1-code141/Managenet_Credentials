import pytest Mahesh@
from unittest.mock import patch
from app import app, create_user, fetch_user_by_id, remove_user_by_id, show_all_data
from services.user_service import hash_password
from repositories.user_repository import row_to_dict


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_user_data():
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'address': '123 Main St',
        'phonenumber': '555-1234',
        'password': 'securepass123'
    }


class TestUserService:

    def test_hash_password_creates_different_hashes(self):
        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_hash_password_not_plain_text(self):
        password = "test123"
        hashed = hash_password(password)

        assert hashed != password

    def test_hash_password_returns_string(self):
        hashed = hash_password("abc123")
        assert isinstance(hashed, str)


class TestRepository:

    def test_row_to_dict(self):
        row = (1, "John", "john@gmail.com", "Hyderabad", "9999999999")

        result = row_to_dict(row)

        assert result["id"] == 1
        assert result["name"] == "John"
        assert result["email"] == "john@gmail.com"
        assert result["address"] == "Hyderabad"
        assert result["phonenumber"] == "9999999999"


class TestRoutes:

    def test_home_page(self, client):
        response = client.get('/')
        assert response.status_code == 200

    @patch("app.create_user")
    def test_submit_valid(self, mock_create, client, sample_user_data):
        mock_create.return_value = {"id": 1}

        response = client.post("/submit", data=sample_user_data)

        assert response.status_code == 200
        mock_create.assert_called_once()

    def test_get_data_page(self, client):
        response = client.get("/get-data")
        assert response.status_code == 200

    @patch("app.fetch_user_by_id")
    def test_fetch_by_id(self, mock_fetch, client):
        mock_fetch.return_value = [{
            "id": 1,
            "name": "John",
            "email": "john@gmail.com",
            "address": "Hyd",
            "phonenumber": "9999999999"
        }]

        response = client.post("/get-data", data={"input_id": "1"})

        assert response.status_code == 200
        mock_fetch.assert_called_once_with(1)

    @patch("app.remove_user_by_id")
    def test_delete_user(self, mock_delete, client):
        response = client.post("/delete/1")

        assert response.status_code == 302
        mock_delete.assert_called_once_with(1)

    # ✅ NEW TEST FOR SHOW ALL DATA
    @patch("app.show_all_data")
    def test_show_all_users(self, mock_show, client):
        mock_show.return_value = [
            {
                "id": 1,
                "name": "John",
                "email": "john@gmail.com",
                "address": "Hyd",
                "phonenumber": "9999999999"
            },
            {
                "id": 2,
                "name": "Mahesh",
                "email": "mahesh@gmail.com",
                "address": "Vijayawada",
                "phonenumber": "8888888888"
            }
        ]

        response = client.get("/show-all")

        assert response.status_code == 200
        mock_show.assert_called_once()


class TestValidation:

    def test_empty_name(self, client):
        with patch("app.create_user") as mock_create:
            response = client.post("/submit", data={
                "name": "",
                "email": "john@gmail.com",
                "address": "Hyd",
                "phonenumber": "9999999999",
                "password": "123"
            })

            assert response.status_code == 302
            mock_create.assert_not_called()


if __name__ == "__main__":
    pytest.main(["-v"])

import json

from .BaseCase import BaseCase


class TestSignUp(BaseCase):
    def test_succesful_signup(self):
        # Given
        payload = json.dumps(
            {
                "name": "Haniel Nishimura",
                "email": "hello.haniel@gmail.com",
                "password": "haniel01",
            }
        )

        # When
        response = self.app.post(
            "/api/auth/signup",
            headers={"Content-Type": "application/json"},
            data=payload,
        )

        # Then
        self.assertEqual(str, type(response.json["id"]))
        self.assertEqual(200, response.status_code)

    def test_signup_with_non_existing_field(self):
        # Given
        payload = json.dumps(
            {
                "username": "arch.hanieru",
                "name": "Haniel Nishimura",
                "email": "hello.haniel@gmail.com",
                "password": "haniel01",
            }
        )

        # When
        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )

        # Then
        self.assertEqual("Request is missing required fields", response.json["message"])
        self.assertEqual(400, response.status_code)

    def test_signup_without_name(self):
        # Given
        payload = json.dumps(
            {
                "email": "hello.haniel@gmail.com",
                "password": "haniel01",
            }
        )

        # When
        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )

        # Then
        self.assertEqual("Something went wrong", response.json["message"])
        self.assertEqual(500, response.status_code)

    def test_signup_without_email(self):
        # Given
        payload = json.dumps(
            {
                "name": "Haniel Nishimura",
                "password": "haniel01",
            }
        )

        # When
        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )

        # Then
        self.assertEqual("Something went wrong", response.json["message"])
        self.assertEqual(500, response.status_code)

    def test_signup_without_password(self):
        # Given
        payload = json.dumps(
            {
                "name": "Haniel Nishimura",
                "email": "hello.haniel@gmail.com",
            }
        )

        # When
        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )

        # Then
        self.assertEqual("Something went wrong", response.json["message"])
        self.assertEqual(500, response.status_code)

    def test_creating_already_existing_user(self):
        # Given
        payload = json.dumps(
            {
                "name": "Haniel Nishimura",
                "email": "hello.haniel@gmail.com",
                "password": "haniel01",
            }
        )

        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )

        # When
        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )

        # Then
        self.assertEqual("Data already exists", response.json["message"])
        self.assertEqual(400, response.status_code)

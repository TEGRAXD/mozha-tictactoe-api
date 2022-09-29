import json

from .BaseCase import BaseCase

class TestSignIn(BaseCase):
    def test_succesful_signin(self):
        # Given
        # Sign up process
        name = "Tegar Suganda"
        email = "hello.tegar@gmail.com"
        password = "tegar01"

        payloadData = json.dumps(
            {
                "name": name,
                "email": email,
                "password": password,
            }
        )

        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=payloadData,
        )

        # When
        # Sign in process
        response = self.app.post(
            "/api/auth/signin",
            headers={
                "Content-Type": "application/json",
            },
            data=payloadData,
        )

        # Then
        self.assertEqual(str, type(response.json["token"]))
        self.assertEqual(200, response.status_code)

    def test_signin_with_invalid_email(self):
        # Given
        # Sign up process
        name = "Tegar Suganda"
        email = "hello.tegar@gmail.com"
        password = "tegar01"

        payloadData = {
            "name": name,
            "email": email,
            "password": password,
        }

        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(payloadData),
        )

        # When
        # Sign in process
        payloadData["email"] = "hi.tegar@gmail.com"

        response = self.app.post(
            "/api/auth/signin",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(payloadData),
        )

        # Then
        self.assertEqual("Invalid email or password", response.json["message"])
        self.assertEqual(401, response.status_code)

    def test_signin_with_invalid_password(self):
        name = "Tegar Suganda"
        email = "hello.tegar@gmail.com"
        password = "tegar01"

        payloadData = {
            "name": name,
            "email": email,
            "password": password,
        }

        response = self.app.post(
            "/api/auth/signup",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(payloadData),
        )

        # When
        # Sign in process
        payloadData["password"] = "tegar02"

        response = self.app.post(
            "/api/auth/signin",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(payloadData),
        )

        # Then
        self.assertEqual("Invalid email or password", response.json["message"])
        self.assertEqual(401, response.status_code)

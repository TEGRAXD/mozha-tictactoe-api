import json
import copy
import typing as t
from flask import Response
from werkzeug.exceptions import HTTPException

from web.config.response import getResponse

class CustomHTTPException(HTTPException):
    def __init__(self, code: t.Optional[int] = 500, description: t.Optional[str] = None, opt_description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["HTTPException"])
        # error["message"] = error["message"] + (" - " + description if description is not None else "")
        error["status"] = code
        error["message"] = description + ( " - " + opt_description if opt_description != None else "")
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=code))
    pass

class InternalServerError(HTTPException):
    def __init__(self, description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["InternalServerError"])
        error["message"] = error["message"] + (" - " + description if description is not None else "")
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=500))
    pass

class SchemaValidationError(HTTPException):
    def __init__(self, description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["SchemaValidationError"])
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=400))

class BadRequestError(HTTPException):
    pass

class ExistError(HTTPException):
    pass

class UpdateError(HTTPException):
    def __init__(self, description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["UpdateError"])
        error["message"] = error["message"] + (" - " + description if description is not None else "")
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=403))

    pass

class DeleteError(HTTPException):
    def __init__(self, description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["DeleteError"])
        error["message"] = error["message"] + (" - " + description if description is not None else "")
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=403))

class NotExistError(HTTPException):
    def __init__(self, description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["NotExistError"])
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=400))

class UnauthorizedError(HTTPException):
    def __init__(self, description: t.Optional[str] = None, response: t.Optional["Response"] = None):
        error = copy.deepcopy(errors["UnauthorizedError"])
        super().__init__(description, Response(json.dumps(error), mimetype="application/json", status=401))

class EmailDoesNotExistsError(HTTPException):
    pass

class BadTokenError(HTTPException):
    pass

class ExpiredTokenError(HTTPException):
    pass

errors = {
    "HTTPException": json.loads(getResponse(500, "Something went wrong")),
    "InternalServerError": json.loads(getResponse(500, "Something went wrong")),
    "SchemaValidationError": json.loads(getResponse(400, "Request is missing required fields")),
    "BadRequestError": json.loads(getResponse(400, "Bad request")),
    "ExistError": json.loads(getResponse(400, "Data already exist")),
    "UpdateError": json.loads(getResponse(403, "Update data error")),
    "DeleteError": json.loads(getResponse(403, "Delete data error")),
    "NotExistError": json.loads(getResponse(400, "Data does not exist")),
    "UnauthorizedError": json.loads(getResponse(401, "Invalid email or password")),
    "EmailDoesNotExistsError": json.loads(getResponse(400, "Could not find the given email address")),
    "BadTokenError": json.loads(getResponse(403, "Invalid token")),
    "ExpiredTokenError": json.loads(getResponse(403, "Token expired")),
}
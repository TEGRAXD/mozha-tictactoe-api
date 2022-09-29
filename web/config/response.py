import json

def getResponse(status=200, message="OK", result=None):
    if result is not None:
        result = json.loads(result)
    else:
        result = []

    if not isinstance(result, list):
        result = [result]

    return json.dumps({
        "status": status,
        "message": message,
        "result": result,
    })
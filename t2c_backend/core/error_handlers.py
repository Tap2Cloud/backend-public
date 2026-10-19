from fastapi import Request
from fastapi.responses import JSONResponse


async def application_exception_handler(request: Request, exc):
    content = {"msg": exc.msg, "errorCode": exc.error_code}
    if exc.errors:
        content["errors"] = exc.errors
    return JSONResponse(status_code=exc.status_code, content=content)

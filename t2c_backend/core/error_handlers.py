from fastapi import Request
from fastapi.responses import JSONResponse


async def application_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"msg": exc.msg, "errorCode": exc.error_code},
    )

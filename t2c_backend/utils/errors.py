from .enums import ErrorMessageCodes


class ApplicationError(Exception):
    def __init__(self, msg: str, error_code: ErrorMessageCodes, status_code: int) -> None:
        self.msg = msg
        self.error_code = error_code
        self.status_code = status_code


class BadRequestError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.BAD_REQUEST, status_code=400)


class NotFoundError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.NOT_FOUND, status_code=404)


class AlreadyExistsError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.ALREADY_EXIST, status_code=409)


class UnAuthorizedError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.NOT_AUTHORIZED, status_code=401)


class UnAuthenticatedError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.NOT_AUTHENTICATED, status_code=403)


class TokenError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.SERVER_ERROR, status_code=500)


class TokenBackendError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.SERVER_ERROR, status_code=500)


class InvitationTokenExpiredError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, error_code=ErrorMessageCodes.TOKEN_EXPIRED, status_code=498)

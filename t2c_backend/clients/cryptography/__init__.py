from .config import Config


class Cryptography:
    CUSTOM_KEY = Config().CRYPTOGRAPHY_KEY

    def __init__(self, app) -> None:
        self.app = app

    def decode(self, encoded_string: str):
        result = 0
        base = len(self.CUSTOM_KEY)

        for char in encoded_string:
            result = result * base + self.CUSTOM_KEY.index(char)

        decoded = result.to_bytes((result.bit_length() + 7) // 8, byteorder="big")

        return decoded.decode()

    def encode(self, string: str):
        result = int.from_bytes(string.encode(), byteorder="big")
        base = len(self.CUSTOM_KEY)
        encoded = ""

        while result > 0:
            result, remainder = divmod(result, base)
            encoded = self.CUSTOM_KEY[remainder] + encoded

        return encoded


async def setup(app):
    return app.add_client(Cryptography(app))

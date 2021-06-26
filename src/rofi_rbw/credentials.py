
class Credentials:

    def __init__(self, data: str) -> None:
        self.username = ""
        self.totp = ""

        for line in data.strip().split('\n'):
            try:
                key, value = line.split(": ", 1)
                if key == "Username":
                    self.username = value
                elif key == "TOTP Secret":
                    try:
                        import pyotp
                        self.totp = pyotp.parse_uri(value).now()
                    except ModuleNotFoundError:
                        pass
            except ValueError:
                self.password = line


class Credentials:

    def __init__(self, data: str) -> None:
        # Set default values
        self.username = ""
        self.totp = ""

        # Parse rbw output
        self.password, *rest = data.strip().split('\n')
        for line in rest:
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
                pass

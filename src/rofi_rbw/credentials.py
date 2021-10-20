from typing import Union


class Credentials:

    def __init__(self, data: str) -> None:
        self.username = ''
        self.password = ''
        self.totp = ''
        self.uris = []
        self.further = {}

        line, *rest = data.strip().split('\n')
        if len(line.split(": ", 1)) == 2:
            # First line contains ': ' and thus is probably a key-value pair
            # This means there is no password for this entry
            rest = [line] + rest
        else:
            self.password = line

        for line in rest:
            try:
                key, value = line.split(": ", 1)
                if key == "Username":
                    self.username = value
                elif key == "URI":
                    self.uris.append(value)
                elif key == "TOTP Secret":
                    try:
                        import pyotp
                        self.totp = pyotp.parse_uri(value).now()
                    except ModuleNotFoundError:
                        pass
                else:
                    self.further[key] = value
            except ValueError:
                # Non-key-value-pairs (i.e. notes) are ignored
                pass

    def __getitem__(self, item: str) -> Union[str, None]:
        if item.lower() == 'username':
            return self.username
        elif item.lower() == 'password':
            return self.password
        elif item.lower() == 'totp':
            return self.totp
        elif item.lower() == 'uris':
            return self.uris
        else:
            return self.further.get(item, None)

from typing import Union


class Credentials:

    def __init__(self, data: str) -> None:
        self.username = ''
        self.password = ''
        self.totp = ''
        self.further = {}

        first = True
        uri = 1
        for line in data.strip().split('\n'):
            fields = line.split(": ", 1)
            if len(fields) == 2:
                if fields[0] == "Username":
                    self.username = fields[1]
                elif fields[0] == "TOTP Secret":
                    try:
                        import pyotp
                        self.totp = pyotp.parse_uri(fields[1]).now()
                    except ModuleNotFoundError:
                        pass
                elif fields[0] == "URI":
                    self.further[f'URI {uri}'] = fields[1]
                    uri += 1
                else:
                    self.further[fields[0]] = fields[1]
            elif first:
                self.password = line
            else:
                pass
            first = False

    def __getitem__(self, item: str) -> Union[str, None]:
        if item.lower() == 'username':
            return self.username
        elif item.lower() == 'password':
            return self.password
        elif item.lower() == 'totp':
            return self.totp
        else:
            try:
                return self.further[item]
            except KeyError:
                return None

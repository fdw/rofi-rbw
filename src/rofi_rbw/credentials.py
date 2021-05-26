
class Credentials:

    def __init__(self) -> None:
        self.password = ""
        self.username = ""

    @staticmethod
    def from_rbw(data: str) -> 'Credentials':
        result = Credentials()
        result.password, *rest = data.split('\n')
        for line in rest:
            key, value = line.rsplit(": ", 1)
            if key == "Username":
                result.username = value

        return result

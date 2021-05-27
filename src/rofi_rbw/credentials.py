
class Credentials:

    def __init__(self, data: str) -> None:
        # Set default values
        self.username = ""

        # Parse rbw output
        result.password, *rest = data.split('\n')
        for line in rest:
            key, value = line.rsplit(": ", 1)
            if key == "Username":
                result.username = value

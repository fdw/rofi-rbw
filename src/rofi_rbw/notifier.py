from subprocess import run


class Notifier:
    def notify(self, message: str) -> None:
        run(
            [
                "notify-send",
                "-u",
                "normal",
                "rofi-rbw",
                message,
            ],
        )

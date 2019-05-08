class IntervalNotSupported(Exception):
    """Zgłaszany gdy podana nazwa interwału jest niepoprawna"""

    def __init__(self, interval: str):
        super().__init__()
        self.message = f'Interval <{interval}> is not supported'

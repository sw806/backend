from datetime import datetime, timedelta


class DatetimeInterval:
    def __init__(self, start: datetime, duration: timedelta = timedelta()) -> None:
        self.start = start
        self.duration = duration

    @property
    def end(self) -> datetime:
        return self.start + self.duration

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else: return False
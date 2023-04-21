from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional

class EdsUrlBuilder:
    # https://www.energidataservice.dk/guides/api-guides
    def __init__(
        self,
        dataset: str,
    ) -> None:
        self.dataset: str = dataset
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
        self.filter: Dict[str, List[str]] = dict()
        self.start: Optional[datetime] = None
        self.end: Optional[datetime] = None
        self.timezone: Optional[str] = None
        self.sort: Optional[str] = None

    @property
    def get_root(self) -> str:
        return "https://api.energidataservice.dk/dataset"

    def set_limit(self, limit: int) -> EdsUrlBuilder:
        self.limit = limit
        return self

    def set_offset(self, offset: int) -> EdsUrlBuilder:
        self.offset = offset
        return self

    def set_start(self, start: datetime) -> EdsUrlBuilder:
        self.start = start
        return self

    def set_end(self, end: datetime) -> EdsUrlBuilder:
        self.end = end
        return self
    
    def set_timezone(self, timezone: str) -> EdsUrlBuilder:
        self.timezone = timezone
        return self

    def set_sort_on_key(self, key: str, ascending: bool) -> EdsUrlBuilder:
        self.sort = f'{key} {"ASC" if ascending else "DESC"}'
        return self

    def add_to_filter(self, key: str, value: str) -> EdsUrlBuilder:
        if key in self.filter:
            self.filter[key].append(value)
        else: self.filter[key] = [value]
        return self

    def _format_datetime(self, time: datetime) -> str:
        # isoformat includes seconds but EDS interprets it as an invalid format.
        # Eg. "2023-03-07T00:00:00" should be "2023-03-07T00:00"
        # For this reason we remove all unnecessary information by creating a new datetime.
        corrected: datetime = datetime(
            time.year, time.month, time.day,
            time.hour, time.minute
        )
        return corrected.isoformat()[:-3]

    def _quote(self, list: List[Any], seperator: str, quote: str = '"') -> str:
        quoted: List[str] = [quote + str(elem) + quote for elem in list]
        return seperator.join(quoted)

    def build(self) -> str:
        base = f'{self.get_root}/{self.dataset}'

        parameters: List[str] = []
        if not self.limit is None:
            parameters.append(f'limit={self.limit}')
        if not self.offset is None:
            parameters.append(f'offset={self.offset}')
        if not self.start is None:
            parameters.append(f'start={self._format_datetime(self.start)}')
        if not self.end is None:
            parameters.append(f'end={self._format_datetime(self.end)}')
        if not self.timezone is None:
            parameters.append(f'timezone={self.timezone}')
        if not self.sort is None:
            parameters.append(f'sort={self.sort}')
        if len(self.filter) > 0:
            quoted_filter = [f'"{x}":[{self._quote(self.filter[x], ",")}]' for x in self.filter]
            parameters.append(
                'filter={' + ','.join(quoted_filter) + "}"
            )

        parameters.append("timezone=utc")
        
        if len(parameters) > 0:
            base += '?' + '&'.join(parameters)

        return base
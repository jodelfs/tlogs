from typing import Protocol, List, Tuple

from tlFields import Fields
from tlresult import Result
from tllogdata import LogData
import pandas as pd

class Approximation(Protocol):
    def __init__(self, result: Result, log_data: LogData):
        pass

    def set_fields(self, fields: Fields) -> None:
        pass

    def get_depth_range(self) ->  Tuple[float, float]:
        pass

    def get_result(self) -> List[float]:
        pass

    def update_for_borehole(self, borehole_id: str) -> None:
        pass

    def execute(self, profile: pd.DataFraeme) -> None:
        pass



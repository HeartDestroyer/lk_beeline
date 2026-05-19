# enums.py

#region imports

from enum import Enum

#endregion

class Source(str, Enum):
    LK_FINANCE = "lk_finance"
    LK_ITSK = "lk_itsk"
    LK_TECHNOLOGY = "lk_technology"

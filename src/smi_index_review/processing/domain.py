from datetime import date
from enum import Enum

import pandas as pd
from pydantic import BaseModel, ConfigDict


class SpiUniverseConfig(BaseModel):
    file_path: str
    date_column: str
    id_column: str
    separator: str


class SecDataConfig(BaseModel):
    file_path: str
    date_column: str
    price_column: str
    id_column: str
    free_float_column: str
    shares_column: str
    separator: str


class CompConfig(BaseModel):
    file_path: str
    id_column: str


class ConfigModel(BaseModel):
    spi_universe: SpiUniverseConfig
    sec_data: SecDataConfig
    comp: CompConfig
    review_date: date
    cutoff_date: date
    output_path: str


class ReviewStatus(Enum):
    promoted = "1-18"
    buffer_seats = "Buffer (19-22)"
    out_of_smi = "Out of SMI"


class ChangeStatus(Enum):
    leaver = "Leaver"
    joiner = "Joiner"
    na = "NaN"
    current_member = "Current Member"


class SmiReviewResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    smi_list: pd.DataFrame
    joiners: pd.DataFrame
    leavers: pd.DataFrame


class ResultDFColumns(BaseModel):
    fmcap: str = "FMCAP"
    is_current_member: str = "is_current_member"
    smi: str = "smi"
    review_status: str = "review_status"
    change_status: str = "change_status"
    initial_weight: str = "initial_weight"
    fmcap_rank: str = "FFMCAP_Rank"
    capped_weight: str = "capped_weight"

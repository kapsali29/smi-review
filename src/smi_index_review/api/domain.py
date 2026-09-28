from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ReviewStatusFilter(Enum):
    promoted = "1-18"
    buffer_seats = "Buffer (19-22)"


class StockDetails(BaseModel):
    id: int
    price: float
    free_float: float
    shares: int
    FMCAP: float
    is_current_member: bool
    review_status: str
    change_status: str


class JoinersResponse(BaseModel):
    joiners: list[StockDetails]


class LeaversResponse(BaseModel):
    leavers: list[StockDetails]


class SMI(BaseModel):
    id: int
    price: float
    free_float: float
    shares: int
    FMCAP: float
    FFMCAP_Rank: int
    review_status: str
    change_status: str
    initial_weight: float
    capped_weight: float


class ResultsModel(BaseModel):
    smi_list: list[SMI]
    leavers: list[StockDetails]
    joiners: list[StockDetails]


class Weights(BaseModel):
    initial_weight: float
    capped_weight: float


class ConstituentsResponse(BaseModel):
    id: int
    FFMCAP_Rank: float
    review_status: str
    weights: Weights

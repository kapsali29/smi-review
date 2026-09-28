import json
from pathlib import Path
from typing import cast

import pandas as pd

from smi_index_review.processing.comp import Composition
from smi_index_review.processing.domain import (
    ChangeStatus,
    ResultDFColumns,
    ReviewStatus,
    SmiReviewResult,
)
from smi_index_review.processing.sec_data import SecData
from smi_index_review.processing.settings import CAP
from smi_index_review.processing.spi_universe import SpiUniverse


class SmiReview:
    def __init__(self):
        self.spi_universe = SpiUniverse()
        self.composition = Composition()
        self.sec_data = SecData()
        self.config = self.sec_data.config
        self.cols = ResultDFColumns()

    @staticmethod
    def calculate_smi_status(row: pd.Series) -> tuple[bool, str, str]:
        change_status = ChangeStatus.na
        review_status = ReviewStatus.out_of_smi
        smi_status = False
        current_index = cast(int, row.name)

        if current_index >= 0 and current_index <= 17:
            smi_status = True
            review_status = ReviewStatus.promoted
            if not row.is_current_member:
                change_status = ChangeStatus.joiner
            else:
                change_status = ChangeStatus.current_member
        elif current_index >= 18 and current_index <= 21:
            review_status = ReviewStatus.buffer_seats
            if row.is_current_member:
                smi_status = True
                change_status = ChangeStatus.current_member
            else:
                change_status = ChangeStatus.na
        else:
            review_status = ReviewStatus.out_of_smi
            if row.is_current_member:
                change_status = ChangeStatus.leaver
        return smi_status, review_status.value, change_status.value

    @staticmethod
    def calculate_capped_weight(row: pd.Series, capping_factor: float) -> float:
        if row.initial_weight > CAP:
            capped_weight = CAP
        else:
            capped_weight = row.initial_weight * capping_factor
        return capped_weight

    def review(self) -> SmiReviewResult:
        sec_data_df = self.sec_data.load_transform()
        comp_df = self.composition.load()
        sec_data_df[self.cols.fmcap] = (
            sec_data_df[self.config.sec_data.price_column]
            * sec_data_df[self.config.sec_data.free_float_column]
            * sec_data_df[self.config.sec_data.shares_column]
        )
        sec_data_df[self.cols.is_current_member] = sec_data_df[
            self.config.sec_data.id_column
        ].isin(comp_df[self.config.comp.id_column])
        sec_data_df = sec_data_df.sort_values(
            self.cols.fmcap, ascending=False
        ).reset_index()
        sec_data_df[
            [self.cols.smi, self.cols.review_status, self.cols.change_status]
        ] = sec_data_df.apply(self.calculate_smi_status, axis=1, result_type="expand")
        smi_list = sec_data_df.loc[sec_data_df[self.cols.smi] == True]
        smi_list[self.cols.initial_weight] = (
            smi_list[self.cols.fmcap] / smi_list[self.cols.fmcap].sum()
        )
        smi_list[self.cols.fmcap_rank] = smi_list.index + 1
        joiners = sec_data_df.loc[
            sec_data_df[self.cols.change_status] == ChangeStatus.joiner.value
        ]
        leavers = sec_data_df.loc[
            sec_data_df[self.cols.change_status] == ChangeStatus.leaver.value
        ]
        stocks_over_cap = smi_list.loc[smi_list[self.cols.initial_weight] > CAP]
        residual = sum(
            [x - CAP for x in stocks_over_cap[self.cols.initial_weight].to_list()]
        )
        weight_of_remaining_stocks = sum(
            smi_list.loc[
                ~smi_list[self.config.sec_data.id_column].isin(
                    stocks_over_cap[self.config.sec_data.id_column]
                )
            ][self.cols.initial_weight].to_list()
        )
        capping_factor = (
            residual + weight_of_remaining_stocks
        ) / weight_of_remaining_stocks
        smi_list[self.cols.capped_weight] = smi_list.apply(
            lambda row: self.calculate_capped_weight(row, capping_factor), axis=1
        )
        smi_list = smi_list.drop(
            columns=[
                "index",
                f"{self.config.sec_data.date_column}_review",
                f"{self.config.sec_data.date_column}_cutoff",
            ]
        )
        return SmiReviewResult(smi_list=smi_list, joiners=joiners, leavers=leavers)

    def to_json(self) -> None:
        smi_review_result = self.review()
        path = Path(self.config.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config.output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "smi_list": json.loads(
                        smi_review_result.smi_list.to_json(orient="records")
                    ),
                    "joiners": json.loads(
                        smi_review_result.joiners.to_json(orient="records")
                    ),
                    "leavers": json.loads(
                        smi_review_result.leavers.to_json(orient="records")
                    ),
                },
                f,
                indent=2,
            )

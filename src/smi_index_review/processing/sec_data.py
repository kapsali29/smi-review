from pathlib import Path

import pandas as pd

from smi_index_review.processing.config_loader import ConfigLoader
from smi_index_review.processing.exceptions import SecDataFileDoesNotExists


class SecData(ConfigLoader):
    def __init__(self) -> None:
        super().__init__()
        self.config = self.load_config()

    def filter_values(self, df: pd.DataFrame) -> pd.DataFrame:
        review = df.loc[
            df[self.config.sec_data.date_column]
            == pd.to_datetime(self.config.review_date)
        ]
        cutoff = review = df.loc[
            df[self.config.sec_data.date_column]
            == pd.to_datetime(self.config.cutoff_date)
        ]
        merged = review.merge(
            cutoff, on=self.config.sec_data.id_column, suffixes=("_review", "_cutoff")
        )[
            [
                self.config.sec_data.id_column,
                f"{self.config.sec_data.date_column}_review",
                f"{self.config.sec_data.date_column}_cutoff",
                f"{self.config.sec_data.price_column}_cutoff",
                f"{self.config.sec_data.free_float_column}_review",
                f"{self.config.sec_data.shares_column}_review",
            ]
        ].rename(
            columns={
                f"{self.config.sec_data.price_column}_cutoff": self.config.sec_data.price_column,
                f"{self.config.sec_data.free_float_column}_review": self.config.sec_data.free_float_column,
                f"{self.config.sec_data.shares_column}_review": self.config.sec_data.shares_column,
            }
        )
        return merged

    def load_transform(self) -> pd.DataFrame:
        if Path(self.config.sec_data.file_path).exists():
            df = pd.read_csv(
                self.config.sec_data.file_path,
                parse_dates=[self.config.sec_data.date_column],
                sep=self.config.sec_data.separator,
            )
            df = df.loc[
                (
                    df[self.config.sec_data.date_column].isin(
                        [
                            pd.to_datetime(self.config.review_date),
                            pd.to_datetime(self.config.cutoff_date),
                        ]
                    )
                )
                & (df[self.config.sec_data.shares_column] > 0)
                & (
                    df[self.config.sec_data.free_float_column].between(
                        0, 1, inclusive="right"
                    )
                )
            ].drop_duplicates(
                subset=[
                    self.config.sec_data.id_column,
                    self.config.sec_data.date_column,
                ]
            )
            return self.filter_values(df=df)
        else:
            raise SecDataFileDoesNotExists(
                f"File: {self.config.sec_data.file_path} does not exists"
            )

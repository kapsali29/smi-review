from pathlib import Path

import pandas as pd

from smi_index_review.processing.config_loader import ConfigLoader
from smi_index_review.processing.exceptions import SpiUniverseFileDoesNotExists


class SpiUniverse(ConfigLoader):
    def __init__(self) -> None:
        super().__init__()
        self.config = self.load_config()

    def load_transform(self) -> pd.DataFrame:
        if Path(self.config.spi_universe.file_path).exists():
            df = pd.read_csv(
                self.config.spi_universe.file_path,
                sep=self.config.spi_universe.separator,
                parse_dates=[self.config.spi_universe.date_column],
            )
            df = df.loc[
                df[self.config.spi_universe.date_column]
                == pd.to_datetime(self.config.review_date)
            ].drop_duplicates(subset=[self.config.spi_universe.id_column])
            return df
        else:
            raise SpiUniverseFileDoesNotExists(
                f"File: {self.config.spi_universe.file_path} does not exists"
            )

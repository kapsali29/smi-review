from pathlib import Path

import pandas as pd

from smi_index_review.processing.config_loader import ConfigLoader
from smi_index_review.processing.exceptions import CompositionFileError
from smi_index_review.processing.settings import SMI_MEMBERS


class Composition(ConfigLoader):
    def __init__(self) -> None:
        super().__init__()
        self.config = self.load_config()

    def load(self) -> pd.DataFrame:
        if Path(self.config.comp.file_path).exists():
            df = pd.read_csv(self.config.comp.file_path).dropna().drop_duplicates()
            if len(df) != SMI_MEMBERS:
                raise CompositionFileError(
                    f"SMI members must be {SMI_MEMBERS}. {len(df)} valid members recorded in provided file"
                )
            return df
        else:
            raise CompositionFileError(
                f"File {self.config.comp.file_path} does not exists"
            )

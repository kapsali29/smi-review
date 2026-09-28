from pathlib import Path

import yaml

from smi_index_review.processing.domain import ConfigModel
from smi_index_review.processing.exceptions import ConfigFileDoesNotExists
from smi_index_review.processing.settings import CONFIG_FILE


class ConfigLoader:
    def __init__(self) -> None:
        self.config_path = CONFIG_FILE

    def load_config(self) -> ConfigModel:
        if Path(self.config_path).exists():
            raw_config = yaml.safe_load(
                Path(self.config_path).read_text(encoding="utf-8")
            )
            return ConfigModel.model_validate(raw_config)
        else:
            raise ConfigFileDoesNotExists(
                f"Config File: {self.config_path} does not exists"
            )

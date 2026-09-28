import logging

from smi_index_review.processing.exceptions import (
    CompositionFileError,
    ConfigFileDoesNotExists,
    SecDataFileDoesNotExists,
    SpiUniverseFileDoesNotExists,
)
from smi_index_review.processing.smi_review import SmiReview

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        smi = SmiReview()
        smi.to_json()
        logger.info("Dataset created successfully")
    except (
        CompositionFileError,
        ConfigFileDoesNotExists,
        SecDataFileDoesNotExists,
        SpiUniverseFileDoesNotExists,
    ) as custom_ex:
        logger.error(custom_ex)

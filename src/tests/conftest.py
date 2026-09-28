import pandas as pd
import pytest
import yaml

REVIEW_DATE = "2026-09-21"
CUTOFF_DATE = "2026-09-10"

ALL_IDS = list(range(1, 26))
CURRENT_MEMBERS = list(range(1, 17)) + [19, 20, 23, 24]


def price(sec_id):
    return 500.0 if sec_id == 1 else 100.0 - sec_id


def write_test_files(folder):
    data = folder / "data"
    data.mkdir()

    sec_rows = []
    for sec_id in ALL_IDS:
        sec_rows.append([sec_id, REVIEW_DATE, None, 1.0, 1000])
        sec_rows.append([sec_id, CUTOFF_DATE, price(sec_id), 1.0, 1000])
    pd.DataFrame(
        sec_rows, columns=["id", "date", "price", "free_float", "shares"]
    ).to_csv(data / "sec_data.csv", sep=";", index=False)

    pd.DataFrame({"date": REVIEW_DATE, "id": ALL_IDS}).to_csv(
        data / "spi_universe.csv", sep=";", index=False
    )

    pd.DataFrame({"id": CURRENT_MEMBERS}).to_csv(data / "composition.csv", index=False)

    config = {
        "review_date": REVIEW_DATE,
        "cutoff_date": CUTOFF_DATE,
        "output_path": "output/smi_review.json",
        "spi_universe": {
            "file_path": "data/spi_universe.csv",
            "date_column": "date",
            "id_column": "id",
            "separator": ";",
        },
        "sec_data": {
            "file_path": "data/sec_data.csv",
            "id_column": "id",
            "date_column": "date",
            "price_column": "price",
            "free_float_column": "free_float",
            "shares_column": "shares",
            "separator": ";",
        },
        "comp": {"file_path": "data/composition.csv", "id_column": "id"},
    }
    (folder / "config.yaml").write_text(yaml.safe_dump(config))


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project folder that the code reads from."""
    write_test_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "smi_index_review.processing.config_loader.CONFIG_FILE", "config.yaml"
    )
    return tmp_path

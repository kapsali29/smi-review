import json

import pandas as pd
import pytest

from smi_index_review.processing.smi_review import SmiReview


def row(rank, is_member):
    return pd.Series({"is_current_member": is_member}, name=rank - 1)


def test_top_18_non_member_is_a_joiner():
    assert SmiReview.calculate_smi_status(row(5, False)) == (True, "1-18", "Joiner")


def test_buffer_member_stays_in_smi():
    result = SmiReview.calculate_smi_status(row(20, True))
    assert result == (True, "Buffer (19-22)", "Current Member")


def test_buffer_non_member_does_not_join():
    result = SmiReview.calculate_smi_status(row(20, False))
    assert result == (False, "Buffer (19-22)", "NaN")


def test_member_below_rank_22_is_a_leaver():
    result = SmiReview.calculate_smi_status(row(23, True))
    assert result == (False, "Out of SMI", "Leaver")


def test_weight_above_cap_is_set_to_cap():
    weight = SmiReview.calculate_capped_weight(pd.Series({"initial_weight": 0.3}), 1.5)
    assert weight == 0.18


def test_weight_below_cap_is_scaled_up():
    weight = SmiReview.calculate_capped_weight(pd.Series({"initial_weight": 0.1}), 1.5)
    assert weight == pytest.approx(0.15)


def test_review_selects_the_right_constituents(project):
    result = SmiReview().review()
    assert sorted(result.smi_list["id"]) == list(range(1, 21))


def test_review_finds_joiners_and_leavers(project):
    result = SmiReview().review()
    assert sorted(result.joiners["id"]) == [17, 18]
    assert sorted(result.leavers["id"]) == [23, 24]


def test_capped_weights_add_up_to_one(project):
    result = SmiReview().review()
    assert result.smi_list["capped_weight"].sum() == pytest.approx(1.0)


def test_largest_stock_is_capped_at_18_percent(project):
    result = SmiReview().review()
    top = result.smi_list[result.smi_list["id"] == 1]
    assert top["capped_weight"].item() == pytest.approx(0.18)


def test_to_json_writes_output_file(project):
    SmiReview().to_json()

    data = json.loads((project / "output" / "smi_review.json").read_text())

    assert list(data) == ["smi_list", "joiners", "leavers"]

from yarrow import rand_dataset
from yarrow.cli import check_default


def test_check_valid_ids():
    yar_example = rand_dataset(annotations=[], categories=[], contributors=[])

    expected_res = {"result": True, "detail": []}

    assert expected_res == check_default(yar_example)

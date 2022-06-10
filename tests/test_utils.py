from datetime import datetime

from yarrow import utils


def test_true_on_invalid_kwargs():
    test_data = {
        "source": "TEST",
        "width": 1000,
        "height": 1000,
        "file_name": "test.jpg",
        "date_captured": datetime.now(),
    }
    assert utils.from_image(**test_data)

    wrong_data = test_data.copy()
    wrong_data["invalid_param"] = "Bullshit"

    assert utils.from_image(**wrong_data)

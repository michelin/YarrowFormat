import os
from copy import deepcopy

import pytest
from pydantic import ValidationError

from yarrow import *


@pytest.fixture
def yar_dataset():
    return YarrowDataset.from_yarrow(rand_dataset())


@pytest.fixture
def yar_empty(yar_dataset):
    return YarrowDataset(info=yar_dataset.info, images=[])


def compare_yarrow_datasets_pydantic(
    dataset1: YarrowDataset_pydantic, dataset2: YarrowDataset_pydantic
):
    assert dataset1.info == dataset2.info
    assert dataset1.images == dataset2.images
    assert dataset1.annotations == dataset2.annotations
    assert dataset1.confidential == dataset2.confidential
    assert dataset1.contributors == dataset2.contributors
    assert dataset1.categories == dataset2.categories
    assert set(dataset1.multilayer_images) == set(dataset2.multilayer_images)


def test_append_same(yar_dataset: YarrowDataset):
    yarrow_dataset2 = deepcopy(yar_dataset)

    yarrow_dataset2.append(yar_dataset)

    assert yar_dataset == yarrow_dataset2


def test_append_empty(yar_dataset: YarrowDataset):
    yar_empty = YarrowDataset(info=yar_dataset.info, images=[])
    yar_empty.append(yar_dataset)

    assert yar_dataset == yar_empty


def test_save_and_load_file(yar_dataset: YarrowDataset, tmp_path):
    # We save the yarrow
    yar_path = os.path.join(tmp_path, "test.yarrow.json")
    yar_dataset.pydantic().save_to_file(yar_path, exclude_none=True)

    new_dataset = YarrowDataset.parse_file(yar_path)
    compare_yarrow_datasets_pydantic(yar_dataset, new_dataset)


def test_save_and_load_raw(yar_dataset: YarrowDataset, tmp_path):
    # We save the yarrow
    yar_path = os.path.join(tmp_path, "test.yarrow.json")
    yar_dataset.pydantic().save_to_file(yar_path, exclude_none=True)

    with open(yar_path, "rb") as jsf:
        new_dataset = YarrowDataset.parse_raw(jsf)
    compare_yarrow_datasets_pydantic(yar_dataset, new_dataset)


def test_pass_wrong_dict_to_metrics_should_raise():
    # Given
    excepted_error_msg = (
        "Input should be a valid number, unable to parse string as a number"
    )
    excepted_number_errors = 1

    # When
    with pytest.raises(ValidationError) as excinfo:
        YarrowDataset_pydantic(
            images=[],
            info=Info(source="common_flow", date_created="2021-01-01"),
            metrics={"key": "wrong_value"},
        )
    actual_error_msg = excinfo.value.errors()[0].get("msg")
    actual_number_errors = len(excinfo.value.errors())

    # Then
    assert len(excinfo.value.errors()) == excepted_number_errors == actual_number_errors
    assert excepted_error_msg == actual_error_msg


def test_pass_good_dict_to_metrics_should_create_YarrowDataset():
    # Given
    excepted_object = YarrowDataset_pydantic
    excepted_metrics = {"iou": 0.99}

    # When
    actual_yar_dataset = YarrowDataset_pydantic(
        images=[],
        info=Info(source="common_flow", date_created="2021-01-01"),
        metrics=excepted_metrics,
    )

    # Then
    assert type(actual_yar_dataset) == excepted_object
    assert actual_yar_dataset.metrics == excepted_metrics

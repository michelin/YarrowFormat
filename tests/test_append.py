from copy import deepcopy

import pytest

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

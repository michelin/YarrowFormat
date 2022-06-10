import pytest

from yarrow import *


@pytest.fixture
def yar_dataset():
    return rand_dataset()


@pytest.fixture
def yar_empty(yar_dataset):
    return YarrowDataset_pydantic(info=yar_dataset.info, images=[])


def compare_yarrow_datasets_pydantic(
    dataset1: YarrowDataset_pydantic, dataset2: YarrowDataset_pydantic
):
    assert dataset1.info == dataset2.info
    assert dataset1.images == dataset2.images
    assert dataset1.annotations == dataset2.annotations
    assert dataset1.confidential == dataset2.confidential
    assert dataset1.contributors == dataset2.contributors
    assert dataset1.categories == dataset2.categories
    assert dataset1.multilayer_images == dataset2.multilayer_images


def test_append_same(yar_dataset: YarrowDataset_pydantic):
    yarrow_dataset2 = yar_dataset.copy(deep=True)

    yarrow_dataset2.append(yar_dataset)

    compare_yarrow_datasets_pydantic(yar_dataset, yarrow_dataset2)


def test_append_empty(yar_dataset: YarrowDataset_pydantic):
    yar_empty = YarrowDataset_pydantic(info=yar_dataset.info, images=[])
    yar_empty.append(yar_dataset)

    compare_yarrow_datasets_pydantic(yar_dataset, yar_empty)


def test_subset_by_images_empty(
    yar_dataset: YarrowDataset_pydantic, yar_empty: YarrowDataset_pydantic
):
    yar_subset = yar_dataset._get_subset_data_by_images_ids([])

    compare_yarrow_datasets_pydantic(yar_empty, yar_subset)


def test_subset_by_images_filled(yar_dataset: YarrowDataset_pydantic):
    yar_merged = rand_dataset(info=yar_dataset.info)
    yar_merged.append(yar_dataset)
    yar_subset = yar_merged._get_subset_data_by_images_ids(
        [img.id for img in yar_dataset.images]
    )

    compare_yarrow_datasets_pydantic(yar_subset, yar_dataset)


def test_subset_by_annots_empty(
    yar_dataset: YarrowDataset_pydantic, yar_empty: YarrowDataset_pydantic
):
    yar_subset = yar_dataset._get_subset_by_annotation_ids([])

    compare_yarrow_datasets_pydantic(yar_subset, yar_empty)


def test_subset_by_annot_filled(yar_dataset: YarrowDataset_pydantic):
    yar_merged = rand_dataset(info=yar_dataset.info)
    yar_merged.append(yar_dataset)

    yar_subset = yar_merged._get_subset_by_annotation_ids(
        [annot.id for annot in yar_dataset.annotations]
    )
    yar_dataset_minimal = yar_dataset._get_subset_by_annotation_ids(
        [annot.id for annot in yar_dataset.annotations]
    )

    compare_yarrow_datasets_pydantic(yar_dataset_minimal, yar_subset)

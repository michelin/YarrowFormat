import pytest

from yarrow import *

from .test_append import compare_yarrow_datasets_pydantic


@pytest.fixture
def yar_dataset_pydantic():
    return rand_dataset()


@pytest.fixture
def yar_dataset(yar_dataset_pydantic: YarrowDataset_pydantic):
    return YarrowDataset.from_yarrow(yar_dataset_pydantic)


@pytest.fixture
def new_clearance():
    return rand_clearance()


@pytest.fixture
def new_category():
    return rand_category()


@pytest.fixture
def new_contributor():
    return rand_contrib()


@pytest.fixture
def new_image(new_clearance: Clearance):
    new_image_pydantic = rand_image(conf_id=new_clearance.id)
    return Image(confidential=new_clearance, **new_image_pydantic.dict())


@pytest.fixture
def new_annotation(
    new_image: Image, new_category: Category, new_contributor: Contributor
):
    new_annotation_pydantic = rand_annot(image_id=new_image.id, cat_id=new_category.id)
    return Annotation(
        images=[new_image],
        categories=[new_category],
        contributor=new_contributor,
        **new_annotation_pydantic.dict()
    )


def compare_yarrow_datasets(dataset1: YarrowDataset, dataset2: YarrowDataset):
    assert dataset1.info == dataset2.info
    assert len(set(dataset1.images).symmetric_difference(set(dataset2.images))) == 0
    assert (
        len(set(dataset1.annotations).symmetric_difference(set(dataset2.annotations)))
        == 0
    )
    assert (
        len(set(dataset1.contributors).symmetric_difference(set(dataset2.contributors)))
        == 0
    )
    assert (
        len(set(dataset1.categories).symmetric_difference(set(dataset2.categories)))
        == 0
    )
    assert (
        len(set(dataset1.confidential).symmetric_difference(set(dataset2.confidential)))
        == 0
    )
    assert (
        len(
            set(dataset1.multilayer_images).symmetric_difference(
                set(dataset2.multilayer_images)
            )
        )
        == 0
    )


def test_yar_2_cls(yar_dataset_pydantic: YarrowDataset_pydantic):
    yar_cls = YarrowDataset.from_yarrow(yar_dataset_pydantic)
    assert isinstance(yar_cls, YarrowDataset)

    assert yar_cls.info == yar_dataset_pydantic.info
    assert [img.pydantic() for img in yar_cls.images] == yar_dataset_pydantic.images
    assert [
        annot.pydantic() for annot in yar_cls.annotations
    ] == yar_dataset_pydantic.annotations
    assert yar_cls.categories == yar_dataset_pydantic.categories
    assert yar_cls.confidential == yar_dataset_pydantic.confidential
    assert yar_cls.contributors == yar_dataset_pydantic.contributors
    assert [
        multi.pydantic() for multi in yar_cls.multilayer_images
    ] == yar_dataset_pydantic.multilayer_images


def test_yar_2_cls_2_yar(
    yar_dataset_pydantic: YarrowDataset_pydantic, yar_dataset: YarrowDataset
):
    compare_yarrow_datasets_pydantic(yar_dataset.pydantic(), yar_dataset_pydantic)


def test_yar_cls_add_image(
    yar_dataset: YarrowDataset, new_image: Image, new_clearance: Clearance
):
    yar_dataset.add_image(new_image)

    assert new_image in yar_dataset.images
    assert new_clearance in yar_dataset.confidential

    yar_pydantic = yar_dataset.pydantic()

    assert new_image.pydantic() in yar_pydantic.images
    assert new_clearance in yar_pydantic.confidential


def test_yar_cls_add_annotation(
    yar_dataset: YarrowDataset,
    new_annotation: Annotation,
    new_image: Image,
    new_contributor: Contributor,
    new_category: Category,
    new_clearance: Clearance,
):
    yar_dataset.add_annotation(new_annotation)

    assert new_annotation in yar_dataset.annotations
    assert new_image in yar_dataset.images
    assert new_category in yar_dataset.categories
    assert new_contributor in yar_dataset.contributors
    assert new_clearance in yar_dataset.confidential

    yar_dataset_pydantic = yar_dataset.pydantic()

    assert new_annotation.pydantic() in yar_dataset_pydantic.annotations
    assert new_image.pydantic() in yar_dataset_pydantic.images
    assert new_category in yar_dataset_pydantic.categories
    assert new_contributor in yar_dataset_pydantic.contributors
    assert new_clearance in yar_dataset_pydantic.confidential


def test_poly_mask_validator(yar_dataset: YarrowDataset):
    annot = yar_dataset.annotations[0]

    annot_param = annot.pydantic().dict()
    polygon = [[0.1, 0.1], [0.2, 0.2], [0.3, 0.3]]

    annot_param["polygon"] = polygon

    assert Annotation(
        **annot_param, contributor=annot.contributor
    )._poly_mask_validator()

    annot_param.pop("polygon")
    annot_param["mask"] = RLE(counts=[0, 0], size=[0])
    assert Annotation(
        **annot_param, contributor=annot.contributor
    )._poly_mask_validator()

    annot_param["polygon"] = polygon
    with pytest.raises(ValueError):
        Annotation(**annot_param, contributor=annot.contributor)._poly_mask_validator()


def test_image_id(yar_dataset: YarrowDataset):
    img = yar_dataset.images[0]

    new_img = Image(**img.__dict__)

    assert new_img.id == img.id

    sec_img_params = img.__dict__.copy()
    sec_img_params.pop("id")

    sec_img = Image(**sec_img_params)

    assert sec_img.pydantic(id=img.id, reset=True).id == img.id


def test_serialize(yar_dataset: YarrowDataset):
    str_res = yar_dataset.pydantic().json(exclude_none=True)

    dict_res = json.loads(str_res)

    yar_res = YarrowDataset.parse_obj(dict_res)

    assert yar_dataset == yar_res


def test_non_list_category_insert(yar_dataset: YarrowDataset):
    with pytest.raises(AssertionError):
        Annotation(
            contributor=yar_dataset.contributors[0],
            images=[yar_dataset.images[0]],
            categories=yar_dataset.categories[0],  # Here we should have a list
        )

    with pytest.raises(AssertionError):
        Annotation(
            contributor=yar_dataset.contributors[0],
            images=yar_dataset.images[0],  # Here we should have a list
            categories=[yar_dataset.categories[0]],
        )


def test_parse_with_null_values(yar_dataset_pydantic: YarrowDataset_pydantic):
    """Idea behind this test is to check the pydantic behavior if we supply none \
        elements or don't supply the parameter at all, the prefered behaviour \
        being, we want the minimum tests but the maximum possible cases working \
        without raising errors
    """

    # First test is with keys completely removed
    primary_dict = yar_dataset_pydantic.dict()
    primary_dict.pop("annotations")
    primary_dict.pop("contributors")
    primary_dict.pop("categories")

    intermediate_set = YarrowDataset_pydantic.parse_obj(primary_dict)
    # intermediate_set has empty lists

    yar_dataset = YarrowDataset.from_yarrow(intermediate_set)
    assert isinstance(yar_dataset, YarrowDataset)

    # Second test if values set to None
    second_dict = yar_dataset_pydantic.dict()
    second_dict["annotations"] = None
    second_dict["contributors"] = None
    second_dict["categories"] = None

    intermediate_set = YarrowDataset_pydantic.parse_obj(second_dict)
    # Here intermediate_set has None values instead of empty lists

    yar_dataset = YarrowDataset.from_yarrow(intermediate_set)
    assert isinstance(yar_dataset, YarrowDataset)


def test_multi_spectral(new_contributor: Contributor, new_category: Category):
    uid = uuid_init()
    nb_image = 5

    images = [rand_image() for _ in range(nb_image)]
    for img in images:
        img.id = uid

    annot = Annotation_pydantic(
        image_id=uid,
        contributor_id=new_contributor.id,
        category_id=new_category.id,
        name="random_classif",
    )

    yar_dataset_pydantic = YarrowDataset_pydantic(
        info=rand_info(),
        images=images,
        contributors=[new_contributor],
        categories=[new_category],
        annotations=[annot],
    )

    yar_dataset = YarrowDataset.from_yarrow(yar_dataset_pydantic)

    assert len(yar_dataset.annotations[0].images) == nb_image

    # Now do with a list of image ids
    annot = Annotation_pydantic(
        image_id=[uid],
        contributor_id=new_contributor.id,
        category_id=new_category.id,
        name="random classif",
    )

    yar_dataset_pydantic = YarrowDataset_pydantic(
        info=rand_info(),
        images=images,
        contributors=[new_contributor],
        categories=[new_category],
        annotations=[annot],
    )

    yar_dataset = YarrowDataset.from_yarrow(yar_dataset_pydantic)

    assert len(yar_dataset.annotations[0].images) == nb_image


def test_multilayer_images_append(
    yar_dataset: YarrowDataset, yar_dataset_pydantic: YarrowDataset_pydantic
):
    new_multilayer = MultilayerImage(images=yar_dataset.images[:5], name=uuid4().hex)

    yar_dataset.add_multilayer_image(new_multilayer)

    yar_pydantic = yar_dataset.pydantic()

    # Images are taken from the set so no image should be added
    assert yar_dataset_pydantic.images == yar_pydantic.images

    # Pydantic objects should be equal and inserted last in the list
    assert new_multilayer.pydantic() in yar_pydantic.multilayer_images

    new_multilayer2 = MultilayerImage(
        images=yar_dataset.images[:5], name=new_multilayer.name
    )

    add_multi_result = yar_dataset.add_multilayer_image(new_multilayer2)

    assert add_multi_result is not new_multilayer2
    assert add_multi_result is new_multilayer
    assert add_multi_result.images == new_multilayer2.images


def test_same_elem_insertion_remap(yar_dataset: YarrowDataset):
    annot1 = yar_dataset.annotations[0]

    new_images = []
    for img in annot1.images:
        new_img = Image(**img.__dict__)
        new_img.confidential = img.confidential.copy()
        new_images.append(new_img)

    new_contrib = annot1.contributor.copy()

    new_categories = []
    for cat in annot1.categories:
        new_categories.append(cat.copy())

    annot2 = Annotation(**annot1.__dict__)
    annot2.images = new_images
    annot2.contributor = new_contrib
    annot2.categories = new_categories

    yar_dataset.add_annotation(annot2)

    for img1, img2 in zip(annot1.images, annot2.images):
        assert img1 is img2
    for cat1, cat2 in zip(annot1.categories, annot2.categories):
        assert cat1 is cat2
    assert annot2.contributor is annot1.contributor

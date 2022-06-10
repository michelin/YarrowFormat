import pytest
from pydantic import BaseModel, ValidationError

from yarrow import *


def test_info():
    info = rand_info()
    assert isinstance(info, Info)

    info2 = rand_info()

    assert not info == info2
    assert info == info


def test_contributor():
    contributor = rand_contrib()
    assert isinstance(contributor, Contributor)

    contributor2 = rand_contrib()

    assert not contributor == contributor2
    assert contributor == contributor


def test_category():
    category = rand_category()
    assert isinstance(category, Category)

    category2 = rand_category()

    assert not category == category2
    assert category == category


def test_clearance():
    clearance = rand_clearance()
    assert isinstance(clearance, Clearance)

    clearance2 = rand_clearance()

    assert not clearance == clearance2
    assert clearance == clearance


def test_image():
    image = rand_image()
    assert isinstance(image, Image_pydantic)

    image2 = rand_image()

    assert not image == image2
    assert image == image


def test_annotation():
    annotation = rand_annot()
    assert isinstance(annotation, Annotation_pydantic)

    annotation2 = rand_annot()

    assert not annotation == annotation2
    assert annotation == annotation


def test_dataset():
    dataset = rand_dataset()
    assert isinstance(dataset, YarrowDataset_pydantic)

    dataset2 = rand_dataset()

    assert not dataset == dataset2
    assert dataset == dataset


def test_Meta_Json_behaviour():
    """Test for a strange Pydantic behavior

    The goal is to be sure a json export of a pydantic model can be read
    by the meta key and outputed correctly.

    This boils down to testing if the Json type functions as we would like it to.
    The union of a dict type is a patch to this.
    """

    class MetaExample(BaseModel):
        test_var: str = uuid4().hex
        test_var2: float = random()
        test_var3: dict = {"test": "test"}

    meta_ex = MetaExample()

    image_base = rand_image().dict(exclude_unset=True)
    image_base["meta"] = meta_ex.json()
    image_meta = Image_pydantic(**image_base)
    assert image_meta.meta == meta_ex.dict()

    image_base2 = rand_image().dict(exclude_unset=True)
    image_base2["meta"] = meta_ex.dict()
    image_meta2 = Image_pydantic(**image_base2)
    assert image_meta2.meta == meta_ex.dict()

    image_base3 = rand_image().dict(exclude_unset=True)
    image_base3["meta"] = str(
        meta_ex.dict()
    )  # putting the dict output in a str should not be sufficient

    with pytest.raises(ValidationError):
        Image_pydantic(**image_base3)


def test_annot_list_init():
    annot = rand_annot()

    annot.category_id = [uuid4().hex for _ in range(5)]
    annot.image_id = [uuid4().hex for _ in range(5)]

    assert isinstance(
        Annotation_pydantic(**annot.dict(exclude_unset=True)), Annotation_pydantic
    )
    new_annot = Annotation_pydantic(**annot.dict(exclude_unset=True))
    assert new_annot.category_id == annot.category_id
    assert new_annot.image_id == annot.image_id

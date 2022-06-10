from datetime import datetime
from itertools import cycle
from random import randint, random
from typing import List
from uuid import uuid4

from .yarrow import *


def from_image(
    file_name: str,
    width: int,
    height: int,
    date_captured: datetime,
    source: str,
    date_created: datetime = None,
    **kwargs
):
    """Returns a minimal `YarrowDataset_pydantic` with the passed arguments, this is a helper function

    Args:
        file_name (str): Local image file name or path
        width (int): image width in pixel
        height (int): image height in pixel
        date_captured (datetime): datetime of the image acquisition
        source (str): a free string to describe the creator of this yarrow, can be a program name or a machine
        date_created (datetime, optional): Creation date of the yarrow, will default to datetime.now() if no value or None is provided. Defaults to None.

    Returns:
        YarrowDataset_pydantic: A YarrowDataset with 1 image and the `Info` class specified
    """

    return YarrowDataset_pydantic(
        info=Info(source=source, date_created=date_created or datetime.now()),
        images=[
            Image_pydantic(
                width=width,
                height=height,
                file_name=file_name,
                date_captured=date_captured,
                **kwargs
            )
        ],
    )


def rand_info() -> Info:
    return Info(source=uuid4().hex, date_created=datetime.now())


def rand_clearance() -> Clearance:
    return Clearance(level=randint(0, 10000), perimeter=uuid4().hex)


def rand_category() -> Category:
    return Category(name=uuid4().hex, super_category=uuid4().hex)


def rand_contrib() -> Contributor:
    return Contributor(human=randint(0, 1), name=uuid4().hex)


def rand_image(confid_list=None, conf_id=None) -> Image_pydantic:
    if confid_list and not conf_id:
        conf_id = confid_list[randint(0, len(confid_list) - 1)].id
    return Image_pydantic(
        width=randint(0, 10000),
        height=randint(0, 10000),
        file_name=uuid4().hex,
        azure_url=uuid4().hex,
        confidential_id=conf_id,
        date_captured=datetime.now(),
    )


def rand_annot(
    image_list=None,
    image_id=None,
    bbox=None,
    cat_list=None,
    cat_id=None,
    contrib_list=None,
    contrib_id=None,
) -> Annotation_pydantic:
    if not cat_id:
        if cat_list:
            cat_id = cat_list[randint(0, len(cat_list) - 1)].id
        else:
            cat_id = uuid4().hex
    if not image_id:
        if image_list:
            image_id = image_list[randint(0, len(image_list) - 1)].id
        else:
            image_id = uuid4().hex
    if not contrib_id:
        if contrib_list:
            contrib_id = contrib_list[randint(0, len(contrib_list) - 1)].id
        else:
            contrib_id = uuid4().hex
    if not bbox:
        bbox = [random() / 2, random() / 2, random() / 2 + 0.5, random() / 2 + 0.5]
    return Annotation_pydantic(
        image_id=image_id,
        category_id=cat_id,
        contributor_id=contrib_id,
        is_crowd=0,
        bbox=bbox or [],
        area=(bbox[2] - bbox[0]) * (bbox[3] - bbox[1]),
    )


def rand_multilayer_image(image_id_list: List[str] = None):
    if image_id_list is None:
        image_id_list = [uuid4().hex for _ in range(5)]
    return MultilayerImage_pydantic(image_id=image_id_list, name=uuid4().hex)


def rand_dataset(
    info: Info = None,
    images: List[Image_pydantic] = None,
    annotations: List[Annotation_pydantic] = None,
    categories: List[Category] = None,
    contributors: List[Contributor] = None,
    confidential: List[Clearance] = None,
    multilayer_images: List[MultilayerImage_pydantic] = None,
) -> YarrowDataset_pydantic:
    """Create a random dataset, unspecified parameters will be generated randomly and the
    result will be valid with respect to id matching except if an empty list is specified
    anywhere

    Args:
        info (Info, optional): Info to use, generated randomly if None. Defaults to None.
        images (List[Image_pydantic], optional): list of Image_pydantic to use, generated randomly if None. Defaults to None.
        annotations (List[Annotation_pydantic], optional): list of Annotation_pydantic to use, generated randomly if None. Defaults to None.
        categories (List[Category], optional): list of Category to use, generated randomly if None. Defaults to None.
        contributors (List[Contributor], optional): list of Contributor to use, generated randomly if None. Defaults to None.
        confidential (List[Clearance], optional): list of Clearance to use, generated randomly if None. Defaults to None.

    Returns:
        YarrowDataset_pydantic: A randomly generated dataset
    """

    if not info:
        info = rand_info()
    if not confidential and not isinstance(confidential, List):
        confidential = [rand_clearance() for _ in range(randint(2, 4))]
    if not categories and not isinstance(categories, List):
        categories = [rand_category() for _ in range(randint(10, 15))]
    if not contributors and not isinstance(contributors, List):
        contributors = [rand_contrib() for _ in range(randint(2, 8))]
    if not images and not isinstance(images, List):
        images = [rand_image(confidential) for _ in range(randint(50, 100))]
        for conf in confidential:
            images.append(rand_image(conf_id=conf.id))
    if not multilayer_images and not isinstance(multilayer_images, List):
        multilayer_images = [
            rand_multilayer_image(
                [img.id for img in images[id_start : id_start + randint(1, 4)]]
            )
            for id_start in range(0, 25, 5)
        ]
    if not annotations and not isinstance(annotations, List):
        annotations = [
            rand_annot(
                image_list=images, cat_list=categories, contrib_list=contributors
            )
            for _ in range(randint(25, 50))
        ]
        for img, cat, contrib in zip(cycle(images), categories, cycle(contributors)):
            annotations.append(
                rand_annot(image_id=img.id, cat_id=cat.id, contrib_id=contrib.id)
            )

    return YarrowDataset_pydantic(
        info=info,
        images=images,
        annotations=annotations,
        confidential=confidential,
        contributors=contributors,
        categories=categories,
        multilayer_images=multilayer_images,
    )

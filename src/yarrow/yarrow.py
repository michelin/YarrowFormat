import json
import uuid
from datetime import datetime
from typing import Any, List, Optional, Union
from warnings import warn

import numpy as np
from pydantic import BaseModel, Field, Json

from ._yarrow_version import _yarrow_version


def uuid_init():
    return uuid.uuid4().hex


class Info(BaseModel):
    # fmt: off
    version         : str = _yarrow_version
    source          : Union[str, dict]
    date_created    : datetime
    destination     : Optional[dict]
    meta            : Optional[dict]
    # fmt: on


class Layer(BaseModel):
    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    frame_id        : int
    width           : Optional[int]
    height          : Optional[int]
    name            : Optional[str] = ""
    meta            : Optional[dict]
    # fmt: on

    def __hash__(self) -> int:
        return hash((self.frame_id, self.width, self.height, self.name))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Layer):
            return all(
                (
                    self.name == other.name,
                    self.frame_id == other.frame_id,
                    self.width == other.width,
                    self.height == other.height,
                )
            )
        return NotImplemented


class Image_pydantic(BaseModel):
    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    width           : int
    height          : int
    file_name       : str
    date_captured   : datetime
    azure_url       : Optional[str]
    confidential_id : Optional[str]
    meta            : Optional[Union[dict, Json]]
    comment         : Optional[str]
    asset_id        : Optional[str]
    layers          : Optional[List[Layer]]
    split           : Optional[str]
    # fmt: on

    def __eq__(self, other) -> bool:
        if isinstance(other, Image_pydantic):
            return all(
                (
                    self.file_name == other.file_name,
                    self.width == other.width,
                    self.height == other.height,
                )
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.file_name, self.width, self.height))


class MultilayerImage_pydantic(BaseModel):
    """Multilayer or spectral image representation

    Be careful the hash and equality are well defined only inside a single
    YarrowDataset
    """

    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    image_id        : List[str] = Field(default_factory=list)
    name            : Optional[str] = ""
    meta            : Optional[dict]
    split           : Optional[str]
    # fmt: on

    def __hash__(self) -> int:
        warn("Multilayer_image.__hash__ is only well defined inside a YarrowDataset")
        return hash((*sorted(self.image_id), self.name))

    def __eq__(self, other: Any) -> bool:
        warn("Multilayer_image.__eq__ is only well defined inside a YarrowDataset")
        if isinstance(other, MultilayerImage_pydantic):
            return all(
                (
                    sorted(self.image_id) == sorted(other.image_id),
                    self.name == other.name,
                )
            )
        return NotImplemented

    def __repr__(self):
        return "MultilayerImage_pydantic(id={}, image_id={}, name={}, meta={})".format(
            self.id, list(set(self.image_id)), self.name, self.meta
        )


class Clearance(BaseModel):
    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    level           : int
    perimeter       : str
    # fmt: on

    def __eq__(self, other):
        if isinstance(other, Clearance):
            return all((self.level == other.level, self.perimeter == other.perimeter))
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.level, self.perimeter))


class Edge(BaseModel):
    # fmt: off
    start_idx       : int
    end_idx         : int
    # fmt: on

    def __eq__(self, other) -> bool:
        if isinstance(other, Edge):
            return self.start_idx == other.start_idx and self.end_idx == other.end_idx
        return NotImplemented


class Category(BaseModel):
    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    name            : str
    value           : Optional[str]
    super_category  : Optional[str]
    keypoints       : Optional[List[str]]
    skeleton        : Optional[List[Edge]]
    # fmt: on

    def __eq__(self, other) -> bool:
        if isinstance(other, Category):
            return all(
                (
                    self.name == other.name,
                    self.value == other.value,
                    self.super_category == other.super_category,
                )
            )
        return NotImplemented

    def __hash__(self):
        return hash((self.name, self.value, self.super_category))


class RLE(BaseModel):
    """Uncompressed binary Mask

    Args:
        counts  : List[int]
        size    : List[int]

    Can take "binary_mask" of type ndarray as an input, will have the normal attributes
    """

    # fmt: off
    counts          : List[int]
    size            : List[int]
    # fmt: on

    def _binary_mask_to_rle(self, binary_mask: np.ndarray):
        counts = []
        size = list(binary_mask.shape)

        last_elem = 0
        running_length = 0

        for _, elem in enumerate(binary_mask.ravel(order="C")):
            if elem != last_elem:
                counts.append(running_length)
                running_length = 0
                last_elem = elem
            running_length += 1

        counts.append(running_length)

        return counts, size

    @property
    def binary_mask(self):
        return self._rle_to_binary_mask()

    def _rle_to_binary_mask(self):
        bi_mask = np.zeros(shape=self.size[0] * self.size[1], dtype=np.uint8)

        last_elem = False
        cur_pos = 0
        for count in self.counts:
            if last_elem:
                bi_mask[cur_pos : cur_pos + count] = 1
            last_elem = not last_elem
            cur_pos += count

        return np.reshape(bi_mask, newshape=tuple(self.size), order="C")

    def __init__(self, **kwargs) -> None:
        if "binary_mask" in kwargs.keys():
            kwargs["counts"], kwargs["size"] = self._binary_mask_to_rle(
                kwargs["binary_mask"]
            )
        super().__init__(**kwargs)

    def __eq__(self, other) -> bool:
        if isinstance(other, RLE):
            return self.counts == other.counts and self.size == other.size
        return NotImplemented


class Annotation_pydantic(BaseModel):
    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    image_id        : Union[str, List[str]]
    category_id     : Union[str, List[str]]
    contributor_id  : str
    name            : Optional[str]
    comment         : Optional[str]
    segmentation    : Optional[Union[List[List[float]], RLE]] = Field(deprecated=True)
    is_crowd        : Optional[int] = Field(default=0, deprecated=True)
    mask            : Optional[RLE]
    polygon         : Optional[List[List[float]]]
    polyline        : Optional[List[List[float]]]
    area            : Optional[float]
    bbox            : Optional[List[float]]
    keypoints       : Optional[List[List[float]]]
    num_keypoints   : Optional[int]
    weight          : Optional[float]
    date_captured   : Optional[datetime]
    meta            : Optional[dict]
    # fmt: on

    def __eq__(self, other) -> bool:
        if isinstance(other, Annotation_pydantic):
            return all(
                (
                    self.name == other.name,
                    self.bbox == other.bbox,
                    self.segmentation == other.segmentation,
                    self.is_crowd == other.is_crowd,
                    self.polygon == other.polygon,
                    self.mask == other.mask,
                )
            )
        return NotImplemented


class Contributor(BaseModel):
    # fmt: off
    id              : str = Field(default_factory=uuid_init)
    human           : bool
    name            : str
    model_id        : Optional[str]
    human_id        : Optional[str]
    # fmt: on

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Contributor):
            return all((self.name == other.name, self.human == other.human))
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.human, self.name))


class YarrowDataset_pydantic(BaseModel):
    # fmt: off
    info             : Info
    images           : List[Image_pydantic]
    annotations      : Optional[List[Annotation_pydantic]] = Field(default_factory=list)
    confidential     : Optional[List[Clearance]] = Field(default_factory=list)
    contributors     : Optional[List[Contributor]] = Field(default_factory=list)
    categories       : Optional[List[Category]] = Field(default_factory=list)
    multilayer_images: Optional[List[MultilayerImage_pydantic]] = Field(default_factory=list)
    # fmt: on

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, YarrowDataset_pydantic):
            return False
        return NotImplemented

    def _clean_unused(self):
        return NotImplemented

    def save_to_file(
        self,
        fp: str,
        exclude_unset: bool = False,
        exclude_none: bool = True,
        indent: int = 4,
        default=str,
        **kwargs
    ):
        """Save this dataset to a file

        :param fp: File path to save the dataset to
        :type fp: _type_
        :param exclude_unset: Exclude unset keys you should not write what you don't use, defaults to True
        :type exclude_unset: bool, optional
        :param indent: Number of indents in the json file, defaults to 4
        :type indent: int, optional
        :param default: default(obj) is a function that should return a serializable version of obj or raise TypeError. The default simply raises TypeError, defaults to str
        :type default: obj, optional
        """
        with open(fp, "w") as fp:
            json.dump(
                self.dict(
                    exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs
                ),
                fp,
                default=default,
                indent=indent,
            )

    def _check_valid_ids(self):
        results = []
        cat_dict = {cat.id: 0 for cat in self.categories} if self.categories else {}
        contr_dict = (
            {contr.id: 0 for contr in self.contributors} if self.contributors else {}
        )
        confid_dict = (
            {confid.id: 0 for confid in self.confidential} if self.confidential else {}
        )

        img_dict = {}
        for img in self.images:
            if img.confidential_id in confid_dict.keys():
                confid_dict[img.confidential_id] += 1
            elif not img.confidential_id is None:
                results.append(
                    {
                        "key": "confidential_id",
                        "error": "confidential_id does not appear in the confidential list",
                        "image_id": img.id,
                        "confidential_id": img.confidential_id,
                    }
                )
            img_dict[img.id] = 0

        if self.annotations:
            for annot in self.annotations:
                if annot.image_id in img_dict.keys():
                    img_dict[annot.image_id] += 1
                else:
                    results.append(
                        {
                            "key": "image_id",
                            "error": "image_id in the annotation does not appear in the image list",
                            "annot_id": annot.id,
                            "image_id": annot.image_id,
                        }
                    )
                if annot.category_id in cat_dict.keys():
                    cat_dict[annot.category_id] += 1
                else:
                    results.append(
                        {
                            "key": "category_id",
                            "error": "image_id in the annotation does not appear in the category list",
                            "annot_id": annot.id,
                            "category_id": annot.category_id,
                        }
                    )
                if annot.contributor_id in contr_dict.keys():
                    contr_dict[annot.contributor_id] += 1
                else:
                    results.append(
                        {
                            "key": "contributor_id",
                            "error": "image_id in the annotation does not appear in the contributor list",
                            "annot_id": annot.id,
                            "contributor_id": annot.contributor_id,
                        }
                    )

        end_res = len(results) == 0

        def gen_warning_unused(input_dict, key_name):
            result = []
            for k, v in input_dict.items():
                if v == 0:
                    result.append(
                        {
                            "key": key_name,
                            "error": "warning, unused category",
                            key_name: k,
                        }
                    )
            return result

        results.extend(gen_warning_unused(cat_dict, "category_id"))
        results.extend(gen_warning_unused(contr_dict, "contributor_id"))
        results.extend(gen_warning_unused(confid_dict, "confidential_id"))

        return end_res, results

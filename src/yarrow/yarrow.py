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

    def append(self, other):
        """This appends another YarrowDataset_pydantic while avoiding duplicating \
        data (images, annotations, contributors, confidential, categories).
        
        info stays the same
        """
        if not isinstance(other, YarrowDataset_pydantic):
            raise ValueError("other is not instance of YarrowDataset_pydantic")

        def internal_append(self_list: List, other_list: List):
            mapping = {}
            for x in other_list:
                found = False
                for col in self_list:
                    if col == x:
                        mapping[x.id] = col.id
                        found = True
                        break
                if not found:
                    mapping[x.id] = x.id
                    self_list.append(x.copy())

            return mapping

        # Append categories and get id mapping
        cat_mapping = {None: None}
        self.categories = self.categories or []
        if other.categories:
            cat_mapping = internal_append(self.categories, other.categories)

        # Append contributors
        contrib_mapping = {None: None}
        self.contributors = self.contributors or []
        if other.contributors:
            contrib_mapping = internal_append(self.contributors, other.contributors)

        # Append confidential
        confid_mapping = {None: None}
        self.confidential = self.confidential or []
        if other.confidential:
            confid_mapping = internal_append(self.confidential, other.confidential)

        img_mapping = {None: None}
        for img in other.images:
            found = False
            for col in self.images:
                if col == img:
                    found = True
                    img_mapping[img.id] = col.id
                    break
            if not found:
                img_mapping[img.id] = img.id
                new_img = img.copy()
                new_img.confidential_id = confid_mapping[img.confidential_id]
                self.images.append(new_img)

        self.annotations = self.annotations or []
        if other.annotations:
            for annot in other.annotations:
                found = False
                for col in self.annotations:
                    if col == annot:
                        found = True
                if not found:
                    new_annot = annot.copy()
                    new_annot.image_id = img_mapping[annot.image_id]
                    new_annot.category_id = cat_mapping[annot.category_id]
                    new_annot.contributor_id = contrib_mapping[annot.contributor_id]
                    self.annotations.append(new_annot)

        self.multilayer_images = self.multilayer_images or []
        if other.multilayer_images:
            for multilayer in other.multilayer_images:
                if multilayer in self.multilayer_images:
                    continue
                temp_img_list = [
                    img_mapping[multi_img_id] for multi_img_id in multilayer.image_id
                ]
                new_multi = multilayer.copy()
                new_multi.image_id = temp_img_list
                self.multilayer_images.append(new_multi)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, YarrowDataset_pydantic):
            return False
        return NotImplemented

    def _delete_by_image_ids(self, image_ids: List[str]):
        self.images[:] = [img for img in self.images if not img.id in image_ids]
        self.annotations[:] = [
            annot for annot in self.annotations if not annot.image_id in image_ids
        ]

    def _get_subset_data_by_images_ids(
        self, images_ids: List[str]
    ) -> "YarrowDataset_pydantic":
        """Returns a subset of images based on a list of ids.
        This is experimental and does not work as expected

        :param images_ids: List of image ids
        :type images_ids: List[str]
        :return: A dataset containing all the objects *completely* related to the images
        :rtype: YarrowDataset_pydantic
        """
        images_ids_set = set(images_ids)

        images = []
        confidential_ids = set()
        for img in self.images:
            if img.id in images_ids_set:
                images.append(img)
                confidential_ids.add(img.confidential_id)

        multilayer_images = []
        for multi_img in self.multilayer_images:
            id_intersect = set(multi_img.image_id).intersection(images_ids_set)
            if len(id_intersect) > 0:
                temp_multi = multi_img.copy()
                temp_multi.image_id = list(id_intersect)
                multilayer_images.append(temp_multi)

        confidential = [
            confid for confid in self.confidential if confid.id in confidential_ids
        ]

        annotations = []
        annotations_ids = set()
        contributor_ids = set()
        category_ids = set()
        for annot in self.annotations:
            if not isinstance(annot.image_id, list):
                annot_id_set = set((annot.image_id,))
            else:
                annot_id_set = set(annot.image_id)
            annot_id_intersect = annot_id_set.intersection(images_ids_set)
            if len(annot_id_intersect) > 0:
                temp_annot = annot.copy(deep=True)
                temp_annot.image_id = list(annot_id_intersect)
                annotations.append(annot)
                annotations_ids.add(annot.id)
                category_ids.add(annot.category_id)
                contributor_ids.add(annot.contributor_id)

        categories = [cat for cat in self.categories if cat.id in category_ids]
        contributors = [
            contrib for contrib in self.contributors if contrib.id in contributor_ids
        ]

        data = {"info": self.info, "images": images}
        if len(annotations) > 0:
            data["annotations"] = annotations
        if len(confidential) > 0:
            data["confidential"] = confidential
        if len(contributors) > 0:
            data["contributors"] = contributors
        if len(categories) > 0:
            data["categories"] = categories
        if len(multilayer_images) > 0:
            data["multilayer_images"] = multilayer_images

        return YarrowDataset_pydantic(**data)

    def _get_subset_by_annotation_ids(self, annotIds: List[str]):

        annotations = []
        annotations_ids = set()
        contributor_ids = set()
        category_ids = set()
        images_ids = set()

        for annot in self.annotations:
            if annot.id in annotIds:
                annotations.append(annot)
                annotations_ids.add(annot.id)
                if type(annot.category_id) == list:
                    category_ids.add(*annot.category_id)
                else:
                    category_ids.add(annot.category_id)
                contributor_ids.add(annot.contributor_id)
                if type(annot.image_id) == list:
                    images_ids.add(*annot.image_id)
                else:
                    images_ids.add(annot.image_id)

        images = []
        confidential_ids = set()
        for img in self.images:
            if img.id in images_ids:
                images.append(img)
                confidential_ids.add(img.confidential_id)

        multilayer_images = []
        for multi_img in self.multilayer_images:
            if set(multi_img.image_id).issubset(images_ids):
                multilayer_images.append(multi_img)

        confidential = [
            confid for confid in self.confidential if confid.id in confidential_ids
        ]
        categories = [cat for cat in self.categories if cat.id in category_ids]
        contributors = [
            contrib for contrib in self.contributors if contrib.id in contributor_ids
        ]

        data = {"info": self.info, "images": images}

        if len(annotations) > 0:
            data["annotations"] = annotations
        if len(confidential) > 0:
            data["confidential"] = confidential
        if len(contributors) > 0:
            data["contributors"] = contributors
        if len(categories) > 0:
            data["categories"] = categories
        if len(multilayer_images) > 0:
            data["multilayer_images"] = multilayer_images

        return YarrowDataset_pydantic(**data)

    def _clean_unused(self):
        return NotImplemented

    def save_to_file(
        self,
        fp: str,
        exclude_unset: bool = True,
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
                self.dict(exclude_unset=exclude_unset),
                fp,
                default=default,
                indent=indent,
                **kwargs
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

"""Yarrow classes, enable the schema to be used more efficiently at runtime.

Contains all the non-pydantic class definitions

Each class has a pydantic conversion:

>>> img = Image(...)
    img_pydantic = img.pydantic() # you have a Image_pydantic instance
    img_as_dict = img_pydantic.dict() # now you have a dict

"""
from copy import copy
from datetime import datetime
from warnings import warn

from pydantic import StrBytes

from .yarrow import *


class Image:
    def __init__(
        self,
        width: int,
        height: int,
        file_name: str,
        date_captured: datetime,
        id: str = None,
        azure_url: str = None,
        confidential: Clearance = None,
        meta: dict = None,
        comment: str = None,
        asset_id: str = None,
        split: str = None,
        **kwargs
    ) -> None:
        """Image object, not a pydantic class, represents the image informations

        Args:
            width (int): image width in pixel
            height (int): image height in pixel
            file_name (str): file name OR path in container in azure
            date_captured (datetime): date of acquisition
            id (str, optional): pydantic identifier
            azure_url (str, optional): complete azure url. Defaults to None.
            confidential (Clearance, optional): clearance information, not necessary. Defaults to None.
            meta (dict, optional): optional metadata. Defaults to None.
            comment (str, optional): optional comment. Defaults to None.
            asset_id (str, optional): unique identifier of the asset that created the picture, not used. Defaults to None.
            split(str, optional): string to specify to which split the image belong, used to assign images to "train", "validate" or "test" when training models for example.
        """

        self.id = id or uuid_init()
        self.width = width
        self.height = height
        self.file_name = file_name
        self.date_captured = date_captured
        self.azure_url = azure_url
        self.confidential = confidential
        self.meta = meta or {}
        self.comment = comment
        self.asset_id = asset_id
        self.split = split

        self._pydantic_self = None

    def pydantic(self, id: str = None, reset: bool = False) -> Image_pydantic:
        """Returns the pydantic object mapping this class. After the first call_
        the object reference is kept. Pass reset=True to reinstantiate the object

        Args:
            id (str, optional): image id that will be passed to the pydantic class. IRIS2 use cas. Defaults to None.
            reset (bool, optional): Pass True to reinstantiate the object, previous object will be lost. Defaults to False.

        Returns:
            Image_pydantic: pydantic image class
        """
        if self._pydantic_self is None or reset:
            self._pydantic_self = self._pydantic_call(id)
        return self._pydantic_self

    def __eq__(self, other):
        if isinstance(other, Image):
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

    def _pydantic_call(self, id: str = None, **kwargs) -> Image_pydantic:
        if not id is None:
            self.id = id
        return Image_pydantic(
            confidential_id=None if self.confidential is None else self.confidential.id,
            **self.__dict__,
        )


class Annotation:
    def __init__(
        self,
        contributor: Contributor,
        name: str = None,
        images: List[Image] = None,
        categories: List[Category] = None,
        comment: str = None,
        segmentation: Union[RLE, List[List[float]]] = None,
        is_crowd: int = None,
        polygon: List[List[float]] = None,
        polyline: List[List[float]] = None,
        mask: RLE = None,
        area: float = None,
        bbox: List[float] = None,
        keypoints: List[List[Union[int, float]]] = None,
        num_keypoints: int = None,
        weight: float = None,
        date_captured: datetime = None,
        meta: dict = None,
        **kwargs
    ) -> None:
        """Annotation class, can handle bbox, polygon, mask and keypoint annotation types \
        and a single annotation can be applied to multiple images.

        ```python
        images = [Image(...), ...]
        multi_layer = MultiLayer(images=images, ...)
        
        annot = Annotation(images = images, ...)
        # or
        annot = Annotation(images = multi_layer.images, ...)
        
        yar_set = YarrowDataset(info=Info(...))

        yar_set.add_annotation(annot)
        yar_set.add_multilayer(multi_layer)
        ```

        Args:
            contributor (Contributor): contributor, human or machine that generated the annotation
            images (List[Image]): images to which the annotation applies
            name (str, optional): annotation name, not classification. Defaults to None.
            categories (List[Category]): categories classifying the annotation
            comment (str, optional): simple string comment. Defaults to None.
            segmentation (Union[RLE, List[List[float]]], optional): DEPRECATED, contains a mask or a polygon. Defaults to None.
            is_crowd (int, optional): DEPRECATED, 0 if segmentation contains a polygon, 1 if it contains a mask. Defaults to 0.
            polygon (List[List[float]], optional): A polygon made of points, it is assumed that the shape is closed, DO NOT add the first point at the end of the list
            polyline (List[List[float]], optional): A line made of points
            mask (RLE, optional):
            area (float, optional): relative surface area of the image covered by the annotation. Defaults to None.
            bbox (List[float], optional): bounding box, order[left, top, right, bot]. Defaults to None.
            keypoints (List[List[Union[int, float]]], optional): keypoint annotation, [[x,y,v], ...]; \
                v=0 not labeled, v=1 labeled not visible, v=2 labeled and visible. Defaults to None.
            num_keypoints (int, optional): number of labelled keypoints. Defaults to None.
            weight (float, optional): weight given to the quality of the annotation. Defaults to None.
            date_captured (datetime, optional): datetime at which the annotation was created. Defaults to None.
            meta (dict, optional): a free metadata information key. If the Annotation cannot hold your information then put it here
        """
        self.name = name

        self.images = images or []
        assert isinstance(self.images, List), "images is not a list"

        self.categories = categories or []
        assert isinstance(self.categories, List), "categories is not a list of Image"

        self.contributor = contributor
        assert isinstance(
            self.contributor, Contributor
        ), "contributor is not a Contributor object"
        self.comment = comment

        if not segmentation is None:
            warn(
                "segmentation is deprecated, use polygon or mask instead, will be deleted in v2.0",
                DeprecationWarning,
                stacklevel=2,
            )
        self.segmentation = segmentation
        if not is_crowd is None:
            warn(
                "is_crowd is deprecated, do not use, will be deleted in v2.0",
                DeprecationWarning,
                stacklevel=2,
            )
        self.is_crowd = is_crowd or 0

        self.polygon = polygon
        self.polyline = polyline
        self.mask = mask
        self._poly_mask_validator()

        self.area = area
        self.bbox = bbox
        self.keypoints = keypoints
        self.num_keypoints = num_keypoints
        self.weight = weight
        self.date_captured = date_captured
        self.meta = meta or {}

        self._pydantic_self = None

    def __hash__(self) -> int:
        return hash(
            (self.name, *set(self.images), *set(self.categories), self.contributor)
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Annotation):
            return all(
                (
                    self.name == other.name,
                    set(self.images) == set(other.images),
                    self.contributor == other.contributor,
                    set(self.categories) == set(other.categories),
                    self.polygon == other.polygon,
                    self.polyline == other.polyline,
                    self.mask == other.mask,
                    self.bbox == other.bbox,
                    self.keypoints == other.keypoints,
                )
            )
        return NotImplemented

    def _poly_mask_validator(self):
        if (
            sum(
                (
                    self.polygon is not None,
                    self.polyline is not None,
                    self.mask is not None,
                )
            )
            > 1
        ):
            raise ValueError(
                "Polygon, Polyline and Mask should not be given simultaneously, use one at a time"
            )
        return True

    def _image_list_validator(self):
        """validate if all objects contained in `self.images` are of type Image

        Raises:
            ValueError: value inside images list is not an instance of Image

        Returns:
            bool: True if validation doesn't raise any errors
        """
        for img in self.images:
            if not isinstance(img, Image):
                raise ValueError(
                    "value inside images list is not an instance of Image :", img
                )
        return True

    def pydantic(self, reset: bool = False) -> Annotation_pydantic:

        """Returns the pydanic equivalent class of this object, should not be used directly, \
            use only if you know what you are doing

        Args:
            reset (bool, optional): regenerates the pydantic class, using it will reset the id. Defaults to False.

        Returns:
            type(Annotation_pydantic)
        """
        if self._pydantic_self is None or reset:
            self._pydantic_self = self._pydantic_call()
        return self._pydantic_self

    def _pydantic_call(self) -> Annotation_pydantic:
        self._poly_mask_validator()
        self._image_list_validator()

        return Annotation_pydantic(
            image_id=list({img.pydantic().id for img in self.images}),
            category_id=[cat.id for cat in self.categories],
            contributor_id=self.contributor.id,
            **self.__dict__,
        )


class MultilayerImage:
    def __init__(
        self,
        images: List[Image] = None,
        name: str = None,
        meta: dict = None,
        id: str = None,
        split: str = None,
    ) -> None:
        """MultilayerImage class. Represents a collection of `Image` that should be
        considered as one element.

        Here is an example on how to insert it in an Annotation

        ```python
        images = [Image(...), ...]
        multi_layer = MultiLayer(images=images, ...)

        annot = Annotation(images = images, ...)
        # or
        annot = Annotation(images = multi_layer.images, ...)

        yar_set = YarrowDataset(info=Info(...))

        yar_set.add_annotation(annot)
        yar_set.add_multilayer(multi_layer)
        ```

        Args:
            id (str, optional): unique id of the object, will generate a uuid if None. Defaults to uuid4().hex.
            images (List[Image], optional): Defaults to [].
            name (str, optional): Name of the collection. Defaults to "".
            meta (dict, optional): Metadata. Defaults to {}.
            split(str, optional): string to specify to which split the image belong, used to assign images to "train", "validate" or "test" when training models for example.
        """
        self.id = id or uuid_init()
        self.images = images or []
        self.name = name or ""
        self.meta = meta or {}
        self.split = split

        self._pydantic = None

    def __hash__(self):
        # return hash((*set(self.images), self.name))
        return hash((*sorted(self.images, key=lambda x: hash(x)), self.name))

    def __eq__(self, other):
        if isinstance(other, MultilayerImage):
            return all(
                (
                    set(self.images) == set(other.images),
                    self.name == other.name,
                )
            )
        return NotImplemented

    def set_split(self, split: str):
        """Set the split for the current MultilayerImage and all its Images

        Args:
            split (str): The split value to assign
        """
        self.split = split
        for img in self.images:
            img.split = split

    def pydantic(self, reset: bool = False):
        """Returns the pydantic object mapping this class. After the first call_
        the object reference is kept. Pass reset=True to reinstantiate the object

        Args:
            reset (bool, optional): Pass True to reinstantiate the object, previous object will be lost. Defaults to False.

        Returns:
            Image_pydantic: pydantic image class
        """
        if self._pydantic is None or reset:
            self._pydantic = self._pydantic_call()
        return self._pydantic

    def _pydantic_call(self, **kwargs):
        return MultilayerImage_pydantic(
            id=self.id,
            name=self.name,
            image_id=[img.pydantic().id for img in self.images],
            meta=self.meta,
            split=self.split,
        )


class YarrowDataset:
    def __init__(
        self,
        info: Info,
        images: List[Image] = None,
        annotations: List[Annotation] = None,
        contributors: List[Contributor] = None,
        confidential: List[Clearance] = None,
        categories: List[Category] = None,
        multilayer_images: List[MultilayerImage] = None,
    ) -> None:
        """Entry point for a YarrowDataset, can be created empty of images or annotations.\
            Use the appropriate functions `add_annotations()` and `add_images()` to insert \
            elements in the object.
        
        Example:
        ```
        annot = Annotation(...)
        
        yar_dataset = YarrowDataset(info=Info(...))
        yar_dataset.add_annotation(annot) # This will take care of the image, categories and contributor
        
        ```

        Args:
            info (Info):
            images (List[Image], optional): Defaults to None.
            annotations (List[Annotation], optional): Defaults to None.
            contributors (List[Contributor], optional): Defaults to None.
            confidential (List[Clearance], optional): Defaults to None.
            categories (List[Category], optional): Defaults to None.
            multilayer_images (List[MultilayerImage], optional): Defaults to None.
        """
        self.info = info
        self.images = images or []
        self.annotations = annotations or []
        self.contributors = contributors or []
        self.confidential = confidential or []
        self.categories = categories or []
        self.multilayer_images = multilayer_images or []

    def __eq__(self, other: "YarrowDataset"):
        if isinstance(other, YarrowDataset):
            return all(
                (
                    set(self.images) == set(other.images),
                    set(self.annotations) == set(other.annotations),
                    set(self.contributors) == set(other.contributors),
                    set(self.confidential) == set(other.confidential),
                    set(self.categories) == set(other.categories),
                    set(self.multilayer_images) == set(other.multilayer_images),
                )
            )
        return NotImplemented

    def add_annotations(self, annots: List[Annotation]) -> List[Annotation]:
        """DONT NEED TO ADD IMAGE AFTER THIS. Insertion is done in place

        Args:
            annots (List[Annotation])

        Return:
            (List[Annotation]). Returns the annotation that were added
        """
        result = set()
        for annot in annots:
            result.add(self.add_annotation(annot))
        return list(result)

    def add_annotation(self, annot: Annotation) -> Annotation:
        """YOU DO NOT NEED TO ADD IMAGE AFTER THIS. Insertion is done in place
        If the annotation already exists in the dataset, it will not be added and this function will return the one found

        Be careful, to overwrite metadata you should modify directly the object and not try to overwrite it

        Args:
            annot (Annotation)

        Return:
            (Annotation)
        """
        annot = copy(annot)
        annot.images = self.add_images(annot.images)

        out_cat = set(annot.categories)
        for cat in annot.categories:
            elem_in = next((elem for elem in self.categories if elem == cat), None)
            if elem_in is None:
                self.categories.append(cat)
            else:
                out_cat.remove(cat)
                out_cat.add(elem_in)
        annot.categories = list(out_cat)

        assert isinstance(annot.contributor, Contributor)
        elem_in = next(
            (elem for elem in self.contributors if elem == annot.contributor), None
        )
        if elem_in is None:
            self.contributors.append(annot.contributor)
        else:
            annot.contributor = elem_in

        elem_in = next((elem for elem in self.annotations if elem == annot), None)
        if elem_in is None:
            self.annotations.append(annot)
        else:
            return elem_in
        return annot

    def add_images(self, images: List[Image]) -> List[Image]:
        """Add an image list and its confidential objects if they exists
        and returns the actual images found in the yarrow in case they
        are already present. SHould preserve image order in the list but
        does not guarantee only unique images are present in the returned
        image list

        Args:
            images (List[Image])

        Return:
            (List[Images])
        """
        result = list()
        for img in images:
            result.append(self.add_image(img))

        return result

    def add_image(self, image: Image) -> Image:
        """Add an image and its confidential object if it exists
        Returns the

        Args:
            image (Image)

        Return:
            (Image)
        """
        image = copy(image)
        if not image.confidential is None:
            elem_in = next(
                (elem for elem in self.confidential if elem == image.confidential), None
            )
            if elem_in is None:
                self.confidential.append(image.confidential)
            else:
                image.confidential = elem_in

        elem_in = next((elem for elem in self.images if elem == image), None)
        if elem_in is None:
            self.images.append(image)
        else:
            return elem_in
        return image

    def add_multilayer_image(self, multilayer: MultilayerImage) -> MultilayerImage:
        """Add a multilayer image object, the returned multilayer object will be
        the one in the current YarrowDataset and the original will remain unchanged

        Args:
            multilayer (MultilayerImage): input multilayer image object

        Returns:
            MultilayerImage: A copy of the original multilayer image object contained in the current YarrowDataset
        """
        multilayer = copy(multilayer)
        multilayer.images = self.add_images(multilayer.images)

        elem_in = next(
            (elem for elem in self.multilayer_images if elem == multilayer), None
        )
        if elem_in is None:
            self.multilayer_images.append(multilayer)
        else:
            return elem_in
        return multilayer

    def add_multilayer_images(
        self, multilayer_list: List[MultilayerImage]
    ) -> List[MultilayerImage]:
        """Adds a list of multilayer images and returns the actual multilayer images that are present in the dataset.
        The returned list will contain links to the objects in the current YarrowDataset

        Args:
            multilayer_list (List[MultilayerImage]): Input MultilayerImage list

        Returns:
            List[MultilayerImage]: MultilayerImage list with the current dataset objects linked
        """
        result = set()
        for multi in multilayer_list:
            result.add(self.add_multilayer_image(multi))
        return list(result)

    def pydantic(
        self, img_id: str = None, reset: bool = False
    ) -> YarrowDataset_pydantic:
        """Returns the pydantic YarrowDataset with all elements object links replaced by \
        id links. The returned object can then be used to serialize the dataset using \
        `dict()` and `json()` functions following a pydantic behaviour. See `pydantic` and \
        the `BaseModel` class to understand how it behaves.

        Args:
            img_id (str, optional): If supplied, this id will be given to all images in \
                the dataset and reinstantiate their pydantic objects. Defaults to None.
            reset (bool, optional): If supplied, it will reset all the cached pydantic \
                classes. Defaults to False

        Returns:
            YarrowDataset_pydantic
        """

        return YarrowDataset_pydantic(
            info=self.info,
            images=[img.pydantic(img_id, bool(img_id)) for img in self.images],
            annotations=[annot.pydantic(reset=reset) for annot in self.annotations]
            if len(self.annotations) > 0
            else None,
            contributors=self.contributors if len(self.contributors) > 0 else None,
            confidential=self.confidential if len(self.confidential) > 0 else None,
            categories=self.categories if len(self.categories) > 0 else None,
            multilayer_images=[
                multilayer.pydantic(reset=reset)
                for multilayer in self.multilayer_images
            ]
            if len(self.multilayer_images) > 0
            else None,
        )

    def set_split(self, split: str) -> None:
        """Assigns the value of `split` to all the images and multilayer images

        Args:
            split (str): Describes the split, used to set "train"/"validate"/"test" for example
        """
        for image in self.images:
            image.split = split
        for multilayer in self.multilayer_images:
            multilayer.split = split

    def get_split(self, split: str) -> "YarrowDataset":
        """Returns a new dataset based on a `split` value. 
        
        The returned YarrowDataset will copy all the internal elements,\
        meaning modifications on the new YarrowDataset won't impact the original YarrowDataset

        Args:
            split (str): The split to retrieve

        Returns:
            YarrowDataset: A copy of the current dataset containing only the elements linked to a given split value
        """
        new_yarrow_set = YarrowDataset(info=self.info)

        for annot in self.annotations:
            # Very strong assumption that all images of the annotation have the same value for split
            if len(annot.images) > 0 and annot.images[0].split == split:
                new_yarrow_set.add_annotation(annot)

        for multi in self.multilayer_images:
            if multi.split == split:
                new_yarrow_set.add_multilayer_image(multi)

        return new_yarrow_set

    def append(self, yarrow: "YarrowDataset") -> None:
        """Appends another YarrowDataset to this dataset. The resulting dataset is this object.
        The objects added will be the annotations, the multilayer_images and the images

        Args:
            yarrow (YarrowDataset): Input Yarrow to be merge
        """
        self.add_annotations(yarrow.annotations)
        self.add_multilayer_images(yarrow.multilayer_images)
        self.add_images(yarrow.images)

        for cat in yarrow.categories:
            if cat not in self.categories:
                self.categories.append(cat)

    def extend(self, yarrows: List["YarrowDataset"]) -> None:
        """Extends a YarrowDataset with a list of YarrowDatasets

        Args:
            yarrows (List[YarrowDataset]): List of YarrowDatasets, they will remain unchanged
        """
        for yarrow in yarrows:
            self.append(yarrow)

    @classmethod
    def from_yarrow(cls, yarrow: YarrowDataset_pydantic) -> "YarrowDataset":
        """Constructor to transform a `YarrowDataset_pydantic` and replace all id links \
        with direct object references. Be careful when using directly, it is better \
        to use `parse_*()` functions and not this one directly.

        Args:
            yarrow (YarrowDataset_pydantic): _description_

        Raises:
            TypeError: If the input is not of correct type.
            
            ValueError: Raised if an id link could not be resolved, ex: an annotation \
                referenced a category but no category had a matching id

        Returns:
            YarrowDataset
        """
        if not isinstance(yarrow, YarrowDataset_pydantic):
            raise TypeError("input is not appropriate type %s", yarrow)
        cat_list = [] if yarrow.categories is None else yarrow.categories.copy()
        conf_list = [] if yarrow.confidential is None else yarrow.confidential.copy()
        contrib_list = [] if yarrow.contributors is None else yarrow.contributors.copy()
        annot_list_source = (
            [] if yarrow.annotations is None else yarrow.annotations.copy()
        )
        multilayer_list_source = (
            [] if yarrow.multilayer_images is None else yarrow.multilayer_images.copy()
        )

        # img_list = []
        img_id_dict = {}
        for img in yarrow.images:
            img_param = img.dict()

            # Get confidential from its id
            conf = next(
                (conf for conf in conf_list if conf.id == img.confidential_id),
                None,
            )

            img_param["confidential"] = conf

            if not img.id in img_id_dict.keys():
                img_id_dict[img.id] = []
            img_id_dict[img.id].append(Image(**img_param))

        # multilayer_image
        multilayer_list = []
        for multilayer in multilayer_list_source:
            multi_img = []
            for multi_img_id in multilayer.image_id:
                multi_img.extend(img_id_dict[multi_img_id])

            multilayer_list.append(
                MultilayerImage(
                    images=multi_img,
                    name=multilayer.name,
                    meta=multilayer.meta,
                    id=multilayer.id,
                )
            )

        annot_list = []
        for annot in annot_list_source:
            annot_param = annot.dict(exclude_unset=True)

            # Get contributor from its id
            contr = next(
                (contr for contr in contrib_list if contr.id == annot.contributor_id),
                None,
            )
            if contr is None:
                raise ValueError(
                    "could not find the contributor matching object, invalid yarrow"
                )
            annot_param["contributor"] = contr

            # Get images objects
            if type(annot.image_id) == str:
                image_id_set = set((annot.image_id,))
            else:
                image_id_set = set(annot.image_id)

            annot_param["images"] = []
            for img_id in image_id_set:
                annot_param["images"].extend(img_id_dict[img_id])

            # Get categories objects
            if type(annot.category_id) == str:
                cat_id_set = [annot.category_id]
            else:
                cat_id_set = annot.category_id.copy()

            annot_param["categories"] = []
            for cat_id in cat_id_set:
                cat_cls = next((cat for cat in cat_list if cat.id == cat_id), None)
                if cat_cls is None:
                    raise ValueError("Could not find category matching object")
                annot_param["categories"].append(cat_cls)

            annot_list.append(Annotation(**annot_param))

        img_list = []
        for img_values in img_id_dict.values():
            img_list.extend(img_values)

        return cls(
            info=yarrow.info,
            images=img_list,
            annotations=annot_list,
            contributors=contrib_list,
            confidential=conf_list,
            categories=cat_list,
            multilayer_images=multilayer_list,
        )

    @classmethod
    def parse_file(cls, path, **kwargs) -> "YarrowDataset":
        return cls.from_yarrow(YarrowDataset_pydantic.parse_file(path, **kwargs))

    @classmethod
    def parse_obj(cls, obj: dict, **kwargs) -> "YarrowDataset":
        return cls.from_yarrow(YarrowDataset_pydantic.parse_obj(obj))

    @classmethod
    def parse_raw(cls, raw: StrBytes, **kwargs) -> "YarrowDataset":
        return cls.from_yarrow(YarrowDataset_pydantic.parse_raw(raw, **kwargs))

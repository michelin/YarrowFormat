# Definition Scheme

```javascript
yarrowdataset_pydantic{
    "info"              : info
    "images"            : List[image_pydantic]
    "annotations"       : Optional[List[annotation_pydantic]]
    "confidential"      : Optional[List[clearance]]
    "contributors"      : Optional[List[contributor]]
    "categories"        : Optional[List[category]]
    "multilayer_images" : Optional[List[multilayer_image_pydantic]]
}

info{
    "version"           : str
    "source"            : Union[str, dict]
    "date_created"      : datetime
    "destination"       : Optional[dict]
    "meta"              : Optional[dict]
}

image_pydantic{
    "id"                : str
    "width"             : int
    "height"            : int
    "file_name"         : str
    "date_captured"     : datetime
    "azure_url"         : Optional[str]
    "confidential_id"   : Optional[str]
    "meta"              : Optional[dict]
    "comment"           : Optional[str]
    "asset_id"          : Optional[str]
    "layers"            : Optional[List[layer]]
    "split"             : Optional[str]
}

multilayer_image_pydantic{
    "id"                : int
    "image_id"          : List[str]
    "meta"              : json 
}

layer{
    "frame_id"          : int
    "width"             : int
    "height"            : int
    "name"              : Optional[str]
    "meta"              : Optional[dict]
}

clearance{
    "id"                : str
    "level"             : int
    "perimeter"         : str
}

contributor{
    "id"                : str
    "human"             : bool
    "name"              : str
    "model_id"          : Optional[str]
    "human_id"          : Optional[str]

}

category{
    "id"                : str
    "name"              : str
    "super_category"    : str
    "value"             : Optional[str]
    "keypoints"         : Optional[List[str]]
    "skeleton"          : Optional[List[edge]]
}

edge{
    "start_idx"          : int
    "end_idx"            : int
}

annotation_pydantic{
    "id"                : str
    "image_id"          : Union[str, List[str]]
    "category_id"       : Union[str, List[str]]
    "contributor_id"    : str
    "name"              : Optional[str]
    "comment"           : Optional[str]
    "area"              : Optional[float]
    "mask"              : Optional[RLE]
    "polygon"           : Optional[List[List[x,y]]]
    "bbox"              : Optional[[left, top, right, bot]]
    "keypoints"         : Optional[List[List[x1, y1, v1]]]
    "num_keypoints"     : Optional[int]
    "weight"            : Optional[float]
    "date_captured"     : Optional[datetime]
}
```

> The type `dict` is equivalent to a valid json object. It is written `dict` to map it easier to python, any JSON object can be written, see the [definition](https://www.json.org/json-fr.html) for all the possibilities 

## Info

**version** : format is ```vMajor.minor-DD.MM.YYYY```

**source** : reference to the machine/application which generated the file

**date_created** : file creation date, format ISO 8601, `YYYY-MM-DDThh:mm:ss+hh:mm`

## Image

**id** : image id used in this file *only*, a single value can be repeated, in that case it means the images which share their id are considered to be linked, a single annotation can apply to multiple images

**width** : image width in pixels

**height** : image height in pixels

**file_name** : file name

**confidential_id** : confidential id to link to a clearance object

**azure_url** : a link where to find the image, should contain a SAS token if applicable

**date_captured** : earliest known date the image was captured (=camera time), format ISO 8601, `YYYY-MM-DDThh:mm:ss+hh:mm`

**meta** : key to store image metadata, the format is json and should be project specific.

**comment** : free comment string

**asset_id** : Optional for now, the unique id of the asset which captured the image, in the futur should be used to link these data to other information systems

**layers** : Optional, list of layers contained in the image file, to be used with `.tiff` when you want information at the slice level

**split** : Optional string to indicate the image belongs to a "split" of data, mainly used to differenciate between "train", "validate" and "test" when training a model

## multilayer_image_pydantic

**id** : multilayer id used in this file *only*

**image_id** : Reference to the image it applies

**name** : Optional name to give to a multilayer image

**meta** : key to store image metadata, the format is json and should be project specific.

**split** : Optional string to indicate the image belongs to a "split" of data, mainly used to differenciate between "train", "validate" and "test" when training a model

## layer

**id** : unique id for the layer

**frame_id** : frame identifier inside the multi image file

**name** : Optional name to give to a layer

**width** : frame width in pixels

**height** : frame height in pixels

**meta** : key to store layer metadata, the format is json and should be project specific.

## Clearance

**id** : accord id used in this file *only*

**level** : values are {1,2,3,4} corresponds to arbitrary security levels

**perimeter** : To be defined with the data owner, for example a team or a store to indicate who owns the data

## Contributors

**id** : contributor id used in this file *only*

**human** : Boolean to indicate if contributor is a human (true) or a program (false)

**name** : arbitrary name of the contributor, to be used when none of the other keys can be filled

**human_id** : Optional, should be handle carefully and be a secure hash based on a unique Michelin identifier. Not yet fully implemented

**model_id** : name, indication of the model which generated the annotation

## Category

**id** : category id used in this file *only*

**name** : category name, ex : "cat", "tire", "defect1", ...

**super_category** : if not applicable, write same value as **name**

**value** : Optional, string value of the category

**keypoints** : list of the labels to apply to the points, order of insertion must follow order of insertion in the Annotation class

**skeleton** : Indicates which points are linked together, the indexes are those of the `keypoints` list in the Annotation class

## Annotations

**id** : annotation id used in this file *only*

**image_id** : Reference to the images it applies, should be a list even when applying to a single image

**category_id** : Reference to the categories, should be a list

**contributor_id** : Reference to the contributor

**name** : annotation name, what object your are segmenting

**comment** : Optional text to comment the annotation

**mask** : RLE see [link](https://youtu.be/h6s61a_pqfM?t=688)

**polygon** : Polygon coordinates[^1] must be relative[^2] and follow `[[x, y],...]` order, the general convention is to automatically close the polygon hence the first point doesn't need to be repeated

**polyline** : Polyline coordinates[^1] must be relative[^2] and follow `[[x, y],...]` order

**area** : surface of the image occupied by the annotation, interval is 0..1

**bbox** : relative[^2] pixel position[^1], order is `[left, top, right, bot]` or `[x1, y1, x2, y2]`

**keypoints** : relative[^2] pixel positions[^1], `[[x,y,v],...]` order with v=0 not labeled, v=1 labeled not visible, v=2 labeled and visible

**num_keypoints** : number of labeled keypoints (v>0)

**weight** : Optional float value corresponding to the confidence of the annotation. Should be 1 for human based and in the range [0;1] for AI based

**date_captured** : Optional datetime when the annotation was generated

**meta** : Optional key to store annotation metadata, the format is json and should be project specific.

[^1]: Coordinate system origin is located in the top left corner of the image.

[^2]: Relative between 0 and 1

# Yarrow: a data format for computer vision

---------------

## What is it ?

**yarrow** is a python package to parse, manipulate and serialize data
following the yarrow [data schema](/schema/yarrow_schema.json). This format is
oriented around computer vision data and is heavily inspired by the COCO
[dataset format](https://cocodataset.org/#format-data) and was initially developed
and used in Michelin projects.

## How to install

```sh
pip install yarrowformat
```

## How to use

You can find multiple examples in the [examples directory](/examples/) and soon in a proper documentation (WIP). Here are a few examples.

```python
import json

from yarrow import YarrowDataset

# say you have a yarrow file at path
file_path = "path/to/file.yarrow.json"

yar_set = YarrowDataset.parse_file(file_path)
# You now have a YarrowDataset !

# Add annotations
annot = Annotation(...) # see documentation for parameters
yar_set.add_annotation(annot)

# now save it somewhere else
with open("path/to/other/file.yarrow.json", "w") as fp:
    json.dump(yar_set.pydantic().dict(), fp, default=str)

```

## License

[Apache 2.0](LICENSE)

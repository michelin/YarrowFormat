# Yarrow: a data format for computer vision

---------------

[![PyPI version](https://badge.fury.io/py/yarrowformat.svg)](https://badge.fury.io/py/yarrowformat) [![Documentation Status](https://readthedocs.org/projects/yarrowformat/badge/?version=latest)](https://yarrowformat.readthedocs.io/en/latest/?badge=latest) [![Test and Deploy](https://github.com/michelin/YarrowFormat/actions/workflows/test-deploy.yaml/badge.svg)](https://github.com/michelin/YarrowFormat/actions/workflows/test-deploy.yaml) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## What is it ?

**yarrow** is a python package to parse, manipulate and serialize data
following the yarrow [data schema](/schema/yarrow_schema.json). This format is
oriented around computer vision data and is heavily inspired by the COCO
[dataset format](https://cocodataset.org/#format-data) and was initially developed
and used in Michelin projects.

The full description can be found [here](schema/description.md) with the rules on how to fill different fields.

## How to install

```sh
pip install yarrowformat
```

## How to use

You can find multiple examples in the [examples directory](/examples/) and the package API in the [documentation](https://yarrowformat.readthedocs.io/en/latest/?badge=latest) (still WIP). Here are a few examples.

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

## Format explanation



## License

[Apache 2.0](LICENSE)

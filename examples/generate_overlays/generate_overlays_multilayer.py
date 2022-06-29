import json
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel

import yarrow

if __name__ == "__main__":
    """Goal is to generate a "complex" yarrow with multiple images linked via a
    Multilayer_Image object"""

    info = yarrow.Info(source="Demo", date_created=datetime.now())

    image_main = yarrow.Image(
        width=1000,
        height=1000,
        file_name="test_image_0.jpg",
        date_captured=datetime.now(),
        azure_url="https://picsum.photos/200/300",
        meta={"light": 0},
    )

    image_list = [image_main]
    for i in range(1, 4):
        image_list.append(
            yarrow.Image(
                width=1000,
                height=1000,
                file_name="test_image_{}.jpg".format(i),
                date_captured=datetime.now(),
                azure_url="https://picsum.photos/200/300",
                meta={"light": i},
            )
        )

    multilayer = yarrow.MultilayerImage(
        images=image_list, name="External_id_of_image", meta={"CAB": uuid4().hex}
    )

    yarrowset = yarrow.YarrowDataset(info=info)

    # You shoud use the add_* method insert elements into the dataset
    yarrowset.add_multilayer_image(multilayer=multilayer)

    with open(
        "examples/generate_overlays/example_overlays_multilayer.yarrow.json", "w"
    ) as fp:
        json.dump(
            yarrowset.pydantic().dict(exclude_none=True), fp, default=str, indent=4
        )

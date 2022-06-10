import json
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel

import yarrow


class FakeMeta(BaseModel):
    light: int
    CAB: str


if __name__ == "__main__":
    """Goal is to generate a "complex" yarrow with multiple images sharing an id"""

    info = yarrow.Info(source="Demo", date_created=datetime.now())

    image_main = yarrow.Image(
        width=1000,
        height=1000,
        file_name="test_image_0.jpg",
        date_captured=datetime.now(),
        azure_url="https://picsum.photos/200/300",
        meta=FakeMeta(light=0, CAB=uuid4().hex),
    )

    image_list = [image_main]
    for i in range(1, 4):
        image_list.append(
            yarrow.Image(
                id=image_main.id,  # Overlay images must have matching Ids
                width=1000,
                height=1000,
                file_name="test_image_{}.jpg".format(i),
                date_captured=datetime.now(),
                azure_url="https://picsum.photos/200/300",
                meta=FakeMeta(light=i, CAB=uuid4().hex),
            )
        )

    yarrowset = yarrow.YarrowDataset(info=info, images=image_list)

    with open(
        "examples/generate_overlays/example_overlays_classes.yarrow.json", "w"
    ) as fp:
        json.dump(yarrowset.pydantic().dict(), fp, default=str, indent=4)

import json
from datetime import datetime

import yarrow

if __name__ == "__main__":
    info = yarrow.Info(source="Demo", date_created=datetime.now())

    image = yarrow.Image(
        width=1000,
        height=1000,
        file_name="test_image.jpg",
        date_captured=datetime.now(),
        azure_url="https://picsum.photos/200/300",
    )

    yarrowset = yarrow.YarrowDataset(info=info, images=[image])

    yarrowset.pydantic().save_to_file(
        "examples/generate_simple/example_simple.yarrow.json",
    )

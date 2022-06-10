import yarrow
from datetime import datetime
import json

if __name__ == "__main__":
    info = yarrow.Info(source="Demo", date_created=datetime.now())

    image = yarrow.Image_pydantic(
        width=1000,
        height=1000,
        file_name="test_image.jpg",
        date_captured=datetime.now(),
        azure_url="https://picsum.photos/200/300",
    )

    yarrowset = yarrow.YarrowDataset_pydantic(info=info, images=[image])

    with open("examples/generate_simple/example_simple.yarrow.json", "w") as fp:
        json.dump(yarrowset.dict(exclude_unset=True), fp, default=str, indent=4)

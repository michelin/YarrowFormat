from datetime import datetime

from yarrow import *

if __name__ == "__main__":

    img = Image(
        width=300,
        height=200,
        file_name="path/to/image.jpeg",
        date_captured=datetime.now(),
        azure_url="http://<online_storage>/path/to/image.jpeg",
    )

    contrib = Contributor(human=True, name="labeler")

    categ = Category(name="Defect", super_category="Defect", value="15.1")

    annot = Annotation(
        contributor=contrib,
        name="bump",
        images=[img],
        categories=[categ],
        bbox=[0.5, 0.5, 0.75, 0.75],
        date_captured=datetime.now(),
    )

    yar_set = YarrowDataset(info=Info(source="example", date_created=datetime.now()))
    # You should instantiate the dataset as empty and use the add_*() functions

    yar_set.add_annotation(annot)

    yar_set_dict = yar_set.pydantic().save_to_file(
        "examples/object_classes/demo.yarrow.json"
    )

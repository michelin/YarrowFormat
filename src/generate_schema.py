import json

from yarrow import YarrowDataset_pydantic

if __name__ == "__main__":

    with open("schema/yarrow_schema.json", "w") as fp:
        json.dump(YarrowDataset_pydantic.schema(), fp, indent=4)

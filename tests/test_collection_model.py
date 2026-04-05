from pocketbase.models.collection import Collection


def test_collection_field_response_moves_unknown_keys_into_options():
    collection = Collection(
        {
            "id": "col_1",
            "name": "files",
            "type": "base",
            "fields": [
                {
                    "id": "field_1",
                    "name": "image",
                    "type": "file",
                    "required": False,
                    "maxSelect": 3,
                    "maxSize": 5242880,
                    "mimeTypes": ["text/plain"],
                },
                {
                    "id": "field_2",
                    "name": "rel",
                    "type": "relation",
                    "collectionId": "target",
                    "cascadeDelete": False,
                    "maxSelect": 1,
                },
            ],
        }
    )

    assert collection.fields[0].options["maxSelect"] == 3
    assert collection.fields[0].options["mimeTypes"] == ["text/plain"]
    assert collection.fields[1].options["collectionId"] == "target"
    assert collection.fields[1].options["cascadeDelete"] is False

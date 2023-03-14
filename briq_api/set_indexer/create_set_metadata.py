
from typing import Any


def create_set_metadata(
    token_id: str,
    name: str,
    description: str,
    network: str,
    briqs: list[Any],
) -> dict[str, Any]:
    return {
        "id": token_id,
        "name": name,
        "description": description,
        "version": 1,
        "regionSize": 100000,
        "briqs": briqs,
        "image": f"https://api.briq.construction/v1/preview/{network}/{token_id}.png",
        "animation_url": f"https://api.briq.construction/v1/model/{network}/{token_id}.glb",
        "external_url": f"https://briq.construction/set/{network}/{token_id}",
    }


def create_booklet_metadata(
    theme_id: str,
    booklet_id: str,
    theme_name: str,
    theme_artist: str,
    theme_date: str,
    name: str,
    description: str,
    network: str,
    nb_steps: int,
    step_progress_data: list[int],
    briqs: list[Any],
):
    return {
        "name": name,
        "description": description,
        "version": "1",
        "nb_pages": nb_steps,
        "steps_progress": step_progress_data,
        "booklet_id": f"{theme_id}/{booklet_id}",
        "image": f"https://api.briq.construction/v1/box/cover_booklet/{network}/{theme_id}/{booklet_id}.png",
        "external_url": f"https://api.briq.construction/v1/booklet/pdf/{network}/{theme_id}/{booklet_id}.pdf",
        "properties": {
            "collections": {
                "name": "Collections",
                "value": [theme_name],
            },
            "artist": {
                "name": "Artist",
                "value": theme_artist
            },
            "date": {
                "name": "Date",
                "value": theme_date
            },
            "nb_steps": {
                "name": "Number of steps",
                "value": nb_steps,
            }
        },
        "attributes": [
            {
                "trait_type": "Collections",
                "value": [theme_name],
            },
            {
                "trait_type": theme_name,
                "value": True,
            },
            {
                "trait_type": "Artist",
                "value": theme_artist,
            },
            {
                "trait_type": "Date",
                "value": theme_date,
            },
            {
                "trait_type": "Number of steps",
                "value": nb_steps,
            }
        ],
        "briqs": briqs,
    }

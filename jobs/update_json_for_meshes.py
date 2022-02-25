## Objectives:
# Fetch list of JSON for sets
# Update all the compatible ones
# Save them.

import copy
import logging

logger = logging.getLogger(__name__)

if __name__ != '__main__':
    logger.error("Must be called as a script")


from briq_api.storage.storage import get_storage
set_storage = get_storage()
state_storate = get_storage("jobs/update_json_for_meshes/")


## Because we know that current sets are good, we'll work on a fixed list of sets.
# The first step is to write that list.

def get_open_sets():
    open_sets = []
    try:
        open_sets = state_storate.load_json("open_sets")['sets']
        logger.info("Open list found, %(len)s elements", {"len": len(open_sets)})
        return open_sets
    except:
        logger.info("Open list not found, creating")
    files = set_storage.iterate_files()
    for file in files:
        if file.endswith(".json"):
            logger.info("Registering %(file)s", {"file": file})
            open_sets.append(file.replace(".json", ""))
    state_storate.store_json("open_sets", {"sets": open_sets})
    return open_sets

def update_sets(open_sets):
    i = 0
    while i < len(open_sets):
        for j in range(100):
            if i + j >= len(open_sets):
                break
            set = open_sets[i + j]
            json_data = set_storage.load_json(set)
            og = copy.deepcopy(json_data)
            token_id = json_data["id"]

            need_update = False
            try:
                # ERC 721 metadata compliance
                if "image" not in json_data:
                    json_data["image"] = f"https://api.briq.construction/preview/{token_id}"
                    logging.info("Updating %(key)s for %(token_id)s", {"key": "image", "token_id": token_id})
                    need_update = True
                if "description" not in json_data:
                    json_data["description"] = "A set made of briqs"
                    logging.info("Updating %(key)s for %(token_id)s", {"key": "description", "token_id": token_id})
                    need_update = True
                if "external_url" not in json_data:
                    json_data["external_url"] = f"https://briq.construction/share?set_id={token_id}&network=testnet&version=2"
                    logging.info("Updating %(key)s for %(token_id)s", {"key": "external_url", "token_id": token_id})
                    need_update = True
                if "background_color" not in json_data:
                    if 'recommendedSettings' in json_data:
                        json_data['background_color'] = json_data['recommendedSettings']['backgroundColor'][1:]
                        logging.info("Updating %(key)s for %(token_id)s", {"key": "background_color", "token_id": token_id})
                        need_update = True
                if "animation_url" not in json_data:
                    json_data["animation_url"] = f"https://api.briq.construction/get_model/{token_id}.glb"
                    logging.info("Updating %(key)s for %(token_id)s", {"key": "animation_url", "token_id": token_id})
                    need_update = True
            except Exception as err:
                logging.error("Exception while parsing set %(token_id)s", {"token_id": token_id, "set_data": json_data})
                logging.exception(err, exc_info=err)
            if need_update:
                logging.info("Updating %(token_id)s", {"token_id": token_id})
                set_storage.store_json(set + "_backup", og)
                set_storage.store_json(set, json_data)
        i += 100
        state_storate.store_json("open_sets", {"sets": open_sets[i:]})
        logging.info("Done 100 elements, remain %(remain)s", {"remain": len(open_sets[i:])})

open_sets = get_open_sets()
update_sets(open_sets)

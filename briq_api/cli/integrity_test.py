"""
The purpose of this file is to check the storage for data.
It loops through files and reports files unused by the API.
"""


def check_file_storage():
    import os
    from briq_api.chain.networks import get_network_metadata

    from briq_api.stores import setup_stores, file_storage

    setup_stores(os.getenv("LOCAL") or False, False)
    NETWORK_NAME = os.getenv("NETWORK_NAME") or "starknet-testnet"

    NETWORK = get_network_metadata(NETWORK_NAME)

    fst = file_storage.get_backend(NETWORK.id)

    """Check the file storage for unused files."""
    print("Checking file storage")
    roots = set(fst.list_paths(""))
    expected_roots = {'auctions', 'genesis_themes', 'sets'}
    if roots != expected_roots:
        print("Unexpected root paths:", roots.difference(expected_roots))
    for root in roots:
        print("Checking root", root)
        if root == "auctions":
            folders = set(fst.list_paths(f"{root}/"))
            for folder in folders:
                if not fst.has_json(f"{root}/{folder}/auction_data.json"):
                    print(f"Missing auction_data.json for {folder}")
        elif root == "genesis_themes":
            files = set(fst.list_paths(f"{root}/"))
            for file in files:
                if file == "booklet_spec.json":
                    continue
                if not fst.has_json(f"{root}/{file}/data.json"):
                    print(f"Missing theme_data.json for {file}")
                    continue
                # Check box/booklet data
                for box in fst.list_paths(f"{root}/{file}/"):
                    if box in {
                        "auction_data.json",
                        "cover_postlaunch_high.jpg",
                        "cover_postlaunch_low.jpg",
                        "cover_prelaunch_high.jpg",
                        "cover_prelaunch_low.jpg",
                        "data.json",
                        "logo.png",
                        "splash_high.jpg",
                        "splash_low.jpg",
                    }:
                        continue
                    try:
                        paths = fst.list_paths(f"{root}/{file}/{box}/")
                        if "metadata_booklet.json" not in paths:
                            print(f"Missing metadata_booklet.json for {file}/{box}")
                        if "cover.png" not in paths:
                            print(f"Missing cover.png for {file}/{box}")
                        if "step_0.glb" not in paths:
                            print(f"Missing step_0.glb for {file}/{box}")
                    except:
                        print(f"Error checking {file}/{box}")

        #elif root == "sets":
            #folders = set(fst.list_paths(root))
            #for folder in folders:

if __name__ == "__main__":
    check_file_storage()

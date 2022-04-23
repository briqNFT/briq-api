
if __name__ != "__main__":
    print("ERROR - need to be run as a script")
    exit(1)

import argparse
from briq_api.mesh.briq import BriqData

parser = argparse.ArgumentParser(description='Convert briq json data to other formats')
parser.add_argument('file', help='input briq json file')
args = parser.parse_args()

try:
    data = BriqData().load_file(args.file)
    with open(args.file.replace(".json", ".glb"), "wb") as f:
        f.write(b''.join(data.to_gltf().save_to_bytes()))
except Exception as err:
    print("Error running")
    print(err)

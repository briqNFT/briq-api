
if __name__ != "__main__":
    print("ERROR - need to be run as a script")
    exit(1)

import argparse
from briq_api.mesh.briq import BriqData

parser = argparse.ArgumentParser(description='Convert briq json data to other formats')
parser.add_argument('file', help='input briq json file')
args = parser.parse_args()

try:
    briqData = BriqData().load_file(args.file)
    with open(args.file.replace(".json", ".glb"), "wb") as f:
        data = briqData.to_gltf()
        f.write(b''.join(data.save_to_bytes()))
    with open(args.file.replace(".json", ".vox"), "wb") as f:
        data = briqData.to_vox(args.file)
        f.write(data.to_bytes())
except Exception as err:
    print("Error running conversion of ", args.file)
    raise err

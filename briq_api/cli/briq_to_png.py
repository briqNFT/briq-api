
if __name__ != "__main__":
    print("ERROR - need to be run as a script")
    exit(1)

import argparse
from briq_api.mesh.briq import BriqData

parser = argparse.ArgumentParser(description='Convert briq JSON to PNG image.')
parser.add_argument('file', help='input briq')
args = parser.parse_args()

try:
    briqData = BriqData().load_file(args.file)
    briqData.to_png().save(args.file.replace("json", "png"))
except Exception as err:
    print("Error running conversion of ", args.file)
    raise err

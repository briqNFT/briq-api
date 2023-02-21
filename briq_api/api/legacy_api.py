import asyncio
import io
import json
import logging

from anyio import to_process
from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse

from briq_api.chain.networks import TESTNET_LEGACY
from briq_api.set_identifier import SetRID

from briq_api.mesh.briq import BriqData

from briq_api.stores import genesis_storage, file_storage
from briq_api.storage.file.backends.legacy_cloud_storage import NotFoundException

logger = logging.getLogger(__name__)

app = APIRouter()


@app.head("/store_get/{token_id}")
@app.post("/store_get/{token_id}")
@app.get("/store_get/{token_id}")
async def store_get(token_id: str):
    try:
        data = file_storage.load_set_metadata(rid=SetRID(chain_id=TESTNET_LEGACY.id, token_id=token_id))
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="File not found")
    except Exception as e:
        logging.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="File not found")
    output = {
        "code": 200,
        "token_id": token_id,
        "data": data,
        "name": data['name'] if 'name' in data else '',
        "description": data['description'] if 'description' in data else 'A set made of briqs',
        "image": data['image'].replace('://briq.construction', '://api.briq.construction') if 'image' in data else '',
        "external_url": (data['external_url'] if 'external_url' in data else '').replace('://briq', '://old.briq'),
        "animation_url": (data['animation_url'] if 'animation_url' in data else '').replace('://briq', '://old.briq'),
        "background_color": data['background_color'] if 'background_color' in data else '',
    }
    out = io.StringIO()
    output = json.dump(output, out)
    out.seek(0)
    return StreamingResponse(out, media_type="application/json", headers={
        "Cache-Control": f"public,max-age={2 * 60}"
    })


@app.head("/preview/{token_id}")
@app.get("/preview/{token_id}")
@app.head("/preview/{token_id}.png")
@app.get("/preview/{token_id}.png")
async def get_preview(token_id: str):
    try:
        data = file_storage.load_set_preview(rid=SetRID(chain_id=TESTNET_LEGACY.id, token_id=token_id))
        return StreamingResponse(io.BytesIO(data), media_type="image/png", headers={
            "Cache-Control": f"public,max-age={3600 * 24}"
        })
    except Exception:
        raise HTTPException(status_code=500, detail="File not found")


@app.head("/get_model/{token_id}.{kind}")
@app.get("/get_model/{token_id}.{kind}")
async def get_model(kind: str, token_id: str):
    mime_type = {
        "glb": "model/gltf-binary",
        "vox": "application/octet-stream",
    }
    try:
        data = file_storage.load_set_model(rid=SetRID(chain_id=TESTNET_LEGACY.id, token_id=token_id), kind=kind)
        return StreamingResponse(io.BytesIO(data), media_type=mime_type[kind], headers={
            "Cache-Control": f"public,max-age={3600 * 24}"
        })
    except (NotFoundException, OSError):
        try:
            data = file_storage.load_set_metadata(rid=SetRID(chain_id=TESTNET_LEGACY.id, token_id=token_id))
            briqData = BriqData().load(data)
            output = None
            if kind == "glb":
                # Run this in a separate process, it can take a while and we need to not block.
                data = await to_process.run_sync(briqData.to_gltf)
                output = b''.join(data.save_to_bytes())
                file_storage.store_set_model(rid=SetRID(chain_id=TESTNET_LEGACY.id, token_id=token_id), kind='glb', data=output)
            elif kind == "vox":
                data = await to_process.run_sync(briqData.to_vox, token_id)
                output = data.to_bytes()
                file_storage.store_set_model(rid=SetRID(chain_id=TESTNET_LEGACY.id, token_id=token_id), kind='vox', data=output)
            else:
                raise Exception("Unknown model type " + kind)
            logger.info("Created %(type)s model for %(set)s on the fly.", {"type": kind, "set": token_id})
            return StreamingResponse(io.BytesIO(output), media_type=mime_type[kind], headers={
                "Cache-Control": f"public,max-age={3600 * 24}"
            })
        except Exception as e:
            logger.error(e, exc_info=e)
            raise HTTPException(status_code=500, detail="Error while creating model.")
    except Exception as e:
        logging.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Error while fetching model.")

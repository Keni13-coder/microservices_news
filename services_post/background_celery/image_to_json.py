import pybase64
from starlette.datastructures import UploadFile


async def image_serialization(image: UploadFile) -> dict[str, str]:
    '''
    Rerutn dict with filename and image
    Note:
        filename: str
        image : byte.decode('utf-8') -> str
    '''
    filename = image.filename

    image = await image.read()

    byte = pybase64.b64encode(image)
    decode_byte = byte.decode('utf-8')
    return {'filename': filename, 'image': decode_byte}


def image_deserialization(image: str):
    image = image.encode('utf-8')
    byte = pybase64.b64decode(image, validate=True)
    return byte
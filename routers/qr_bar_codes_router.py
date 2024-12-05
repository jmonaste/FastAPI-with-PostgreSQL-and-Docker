# routers/qr_codes.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import io
from PIL import Image
from pyzbar.pyzbar import decode
import models
import schemas
import services
from schemas import ImageBase64Request
from dependencies import get_current_user
from services.database_service import get_db
from base64 import b64decode

router = APIRouter(
    prefix="/api",
    tags=["QR & Barcodes"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)

# Definir los tipos de imagen permitidos
ALLOWED_EXTENSIONS = {"image/jpeg", "image/jpg", "image/png", "image/heic"}

@router.post(
    "/scan/v1",
    summary="Escanear códigos QR y códigos de barras",
    description="Endpoint para subir una imagen y escanear códigos QR y códigos de barras.",
)
async def scan_qr_barcode(
    file: UploadFile = File(...)
):
    # Verificar el tipo de archivo
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()

    # Manejo de imágenes HEIC
    if file.content_type == "image/heic":
        try:
            import pyheif
            heif_file = pyheif.read_heif(contents)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="HEIC format not supported. Please install 'pyheif' library.",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing HEIC image: {str(e)}")
    else:
        try:
            # Intentar abrir la imagen con PIL
            image = Image.open(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # Decodificar el código QR o de barras usando pyzbar
    decoded_objects = decode(image)

    if not decoded_objects:
        return JSONResponse(content={"error": "No QR or Barcode detected"}, status_code=400)

    # Procesar los códigos detectados
    result_data = []
    for obj in decoded_objects:
        code_type = "QR Code" if obj.type == "QRCODE" else obj.type
        result_data.append({
            "type": code_type,
            "data": obj.data.decode("utf-8")
        })

    # Devolver la lista de códigos detectados junto con su tipo
    return {"detected_codes": result_data}


from base64 import b64decode

@router.post(
    "/scan/v2",
    summary="Escanear códigos QR y códigos de barras desde una imagen en base64",
    description="Endpoint para recibir una imagen en base64 y escanear códigos QR y códigos de barras.",
)
async def scan_qr_barcode_base64(
    request: ImageBase64Request,
):
    # Decodificar la imagen base64
    try:
        image_data = b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # Decodificar el código QR o de barras usando pyzbar
    decoded_objects = decode(image)

    if not decoded_objects:
        return JSONResponse(content={"error": "No QR or Barcode detected"}, status_code=400)

    # Procesar los códigos detectados
    result_data = []
    for obj in decoded_objects:
        code_type = "QR Code" if obj.type == "QRCODE" else obj.type
        result_data.append({
            "type": code_type,
            "data": obj.data.decode("utf-8")
        })

    # Devolver la lista de códigos detectados junto con su tipo
    return {"detected_codes": result_data}

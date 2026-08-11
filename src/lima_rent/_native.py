"""Precarga de `libgomp` para LightGBM en runtimes tipo AWS Lambda (Vercel
Functions incluido).

El wheel de `lightgbm` en PyPI para Linux depende de `libgomp.so.1` del
sistema, y ni la imagen `python:3.11-slim` de Docker ni el runtime Python de
Vercel (Amazon Linux 2023) la traen — confirmado corriendo ambos: fallan con
`OSError: libgomp.so.1: cannot open shared object file`. Es un problema
conocido del empaquetado de LightGBM (no vendorea sus dependencias nativas
como sí hacen numpy/scipy), no algo específico de este proyecto.

`vendor/libgomp/<arquitectura>/libgomp.so.1` son binarios extraídos de
`public.ecr.aws/lambda/python:3.12` (la imagen oficial que usa Vercel por
debajo), uno por arquitectura porque no hay forma de saber de antemano cuál
usa la función desplegada.

Esta función debe llamarse ANTES de cualquier `import lightgbm` (directo o
indirecto, p.ej. al deserializar `models/model.joblib`). En Docker (donde
`Dockerfile` instala `libgomp1` vía apt) y en local (macOS) es un no-op salvo
por el intento de precarga, que falla silenciosamente si el sistema ya
resuelve la librería por su cuenta.
"""

import ctypes
import platform
from pathlib import Path

_VENDOR_DIR = Path(__file__).resolve().parents[2] / "vendor" / "libgomp"


def preload_libgomp() -> None:
    if platform.system() != "Linux":
        return

    lib_path = _VENDOR_DIR / platform.machine() / "libgomp.so.1"
    if not lib_path.exists():
        return

    try:
        ctypes.CDLL(str(lib_path), mode=ctypes.RTLD_GLOBAL)
    except OSError:
        pass  # el sistema ya podría proveerla (p.ej. Docker con libgomp1 instalado vía apt)

import hashlib
import json
import os
from pathlib import Path
from typing import Any


DIRECTORIO_DATOS = Path("datos")
ARCHIVO_PACIENTES = DIRECTORIO_DATOS / "pacientes.json"
ARCHIVO_HASH = DIRECTORIO_DATOS / "pacientes.sha256"

class ErrorIntegridadDatos(Exception):
    """Se produce cuando el archivo no coincide con su hash."""

class ErrorAlmacenamiento(Exception):
    """Se produce cuando no es posible leer o escribir los datos."""

def preparar_diretorio() -> None:

    DIRECTORIO_DATOS.mkdir(
    parents=True,
    exist_ok=True,
    mode=0o700,
    )
#Crea el directorio de datos si todavía no existe.




def calcular_hash_archivo(ruta: Path) -> str:

    sha256 = hashlib.sha256()
    try:
        with ruta.open("rb") as archivo:
            while bloque := archivo.read(8192):
                sha256.update(bloque)
    except OSError as error:
        raise ErrorAlmacenamiento(
            "No fue posible calcular la integridad del archivo."
            ) from error
    return sha256.hexdigest()
#Calcula el hash SHA-256 de un archivo.
#El archivo se lee por bloques para evitar cargar archivos grandes
#completamente en memoria.

def guardar_hash() -> None:

    if not ARCHIVO_PACIENTES.exists():
        raise ErrorAlmacenamiento(
            "no existe el rchivo de pacientes."
        )
    resumen = calcular_hash_archivo(ARCHIVO_PACIENTES)

    try:
        ARCHIVO_HASH.write_text(
            resumen,
            encoding="utf-8",
        )
    except OSError as error:
        raise ErrorAlmacenamiento(
            "no fue posible guardar el archivo de integridad."
        ) from error
#Calcula y guarda el hash del archivo de pacientes.

def verificar_integridad() -> bool:

    if not ARCHIVO_PACIENTES.exists():
        return True
    if not ARCHIVO_HASH.exists():
        raise ErrorIntegridadDatos(
            "existe el archivo de pacientes, pero no su hash."
        )
    try:
        hash_guardado = ARCHIVO_HASH.read_txt(
            encoding="utf-8"
        ).strip()
    except OSError as error:
        raise ErrorAlmacenamiento(
            "no fue posible leer el archivo de integridad."
        ) from error
    
    hash_actual = calcular_hash_archivo(ARCHIVO_PACIENTES)

    if not hash_guardado:
        raise ErrorIntegridadDatos(
            "el archivo de integridad está vacío."  
        )
    if not hashlib.compare_digest(hash_guardado, hash_actual):
        raise ErrorIntegridadDatos(
            "la integridad de los datos no pudo comprobarse."
            "el archivo de pacientes ha sido modificado."
        )
    return True
#Comprueba que el archivo JSON coincida con el hash guardado.

def cargar_pacientes() -> list [dict[str, any]]:

    preparar_diretorio()

    if not ARCHIVO_PACIENTES.exists():
        return []
    verificar_integridad()

    try:
        with ARCHIVO_PACIENTES.open(
            "r",
            encoding="utf-8",
            ) as archivo:
            contenido = json.load(archivo)
    except json.JSONDecodeError as error:
        raise ErrorAlmacenamiento(
            "el archivo de pacientes contiene JSOIN invalido."
        ) from error
    except OSError as error:
        raise ErrorAlmacenamiento(
            "no fue posible leer el archivo de pacientes"
        ) from error
    if not isinstance(contenido, list):
        raise ErrorAlmacenamiento(
            "la estructura principal del archivo debe ser una lista."
        )
    pacientes_validos: list [dict[str, any]] = []
    for elemento in contenido:
        if isinstance(elemento,dict):
            pacientes_validos.append(elemento)
    return pacientes_validos
#Carga los pacientes almacenados.
#Si el archivo no existe, retorna una lista vacía.

def escritura_atomica(
        ruta: Path,
        contenido: str,
) -> None:
    
    ruta_temporal = ruta.with_suffix(ruta.suffix + ".tmp")

    try:
        ruta_temporal.write_text(
            contenido,
            encoding="utf-8",
        )

        os.replace(ruta_temporal, ruta)
    except OSError as error:
        try:
            if ruta_temporal.exists():
                ruta_temporal.unlink()
        except OSError:
            pass
        raise ErrorAlmacenamiento(
            "no fue posible guardar los datos."
        ) from error
#Escribe primero en un archivo temporal y luego lo reemplaza.
#Esta técnica reduce el riesgo de dejar un archivo incompleto si
#ocurre un problema durant

def guardar_pacientes(
        pacientes:list [dict[str,any]]
) -> None:
    
    preparar_diretorio()

    if not isinstance(pacientes,list):
        raise ErrorAlmacenamiento(
            "los pacientes deben almacenarse en una lista."
        )
    try:
        contenido = json.dump(
            pacientes,
            ensure_ascii=False,
            indent=4,
        )
    except (TypeError, ValueError) as error:
        raise ErrorAlmacenamiento(
            "los datos no pueden convertirse a JSON."
        ) from error
    
    escritura_atomica(
        ARCHIVO_PACIENTES,
        contenido,
    )

    guardar_hash()
#Guarda la lista completa de pacientes.
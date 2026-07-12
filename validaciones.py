"""
Funciones de validación y sanitización.
Este módulo controla la información ingresada antes de que sea
utilizada o almacenada por la aplicación.
"""

import re
from typing import Any

LONGITUD_MAXIMA_NOMBRE = 80
LONGITUD_MAXIMA_DIAGNOSTICO = 150
EDAD_MINIMA = 0
EDAD_MAXIMA = 120


def asegurar_texto(valor: Any, nombre_campo: str) -> str:
    """
    Comprueba que un valor sea texto.
    Args:
    valor: Valor que se desea revisar.
    nombre_campo: Nombre utilizado en el mensaje de error.
    Returns:
    El valor convertido en texto limpio.
    Raises:
    ValueError: Si el valor no es una cadena de texto.
    """

    if not isinstance(valor, str):
        raise ValueError(f"El campo {nombre_campo} debe ser texto.")

    return valor.strip()


def sanitizar_nombre(nombre: str) -> str:
    """
    Sanitiza un nombre.
    Se permiten:
    - Letras.
    - Vocales acentuadas.
    - Letra ñ.
    - Espacios.
    - Apóstrofes.
    - Guiones.
    No se permiten números, etiquetas HTML ni otros símbolos.
    """

    nombre = asegurar_texto(nombre, "nombre")
    # Sustituye varios espacios consecutivos por uno solo.
    nombre = re.sub(r"\s+", " ", nombre)
    # Elimina caracteres que no pertenecen al conjunto permitido.
    nombre = re.sub(
        r"[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ' -]",
        "",
        nombre,
    )
    nombre = nombre.strip()

    if not nombre:
        raise ValueError("nombre no puede estar vacío.")

    if len(nombre) < 3:
        raise ValueError("El nombre debe contener al menos 3 caracteres.")

    if len(nombre) > LONGITUD_MAXIMA_NOMBRE:
        raise ValueError(
            f"El nombre no puede superar "
            f"{LONGITUD_MAXIMA_NOMBRE} caracteres."
        )

    return nombre.title()


def limpiar_rut(rut: str) -> str:
    """
    Elimina puntos, espacios y guiones del RUT.

    Ejemplo:
    18.234.567-8 -> 18234578
    """

    rut = asegurar_texto(rut, "RUT")
    return re.sub(r"[^0-9kK]", "", rut).upper()


def calcular_digito_verificador(cuerpo: str) -> str:
    """
    Calcula el dígito verificador de un RUT chileno.

    Args:
        cuerpo: Parte numérica del RUT, sin dígito verificador.
    Returns:
        Dígito verificador calculado.
    """

    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT debe contener solo números.")

    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1

        if multiplicador > 7:
            multiplicador = 2
    resultado = 11 - (suma % 11)

    if resultado == 11:
        return "0"

    if resultado == 10:
        return "K"

    return str(resultado)


def validar_rut(rut: str) -> str:
    """
    Valida y normaliza un RUT chileno

    Returns: 
        RUT en formato sin puntos y con guión.

        Ejemplo: 
        18.234.567-8 -> 18234567-8
    """

    rut_limpio = limpiar_rut(rut)

    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise ValueError("El RUT debe tener entre 8 y 9 caracteres.")

    cuerpo = rut_limpio[:-1]
    digito_recibido = rut_limpio[-1]

    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT debe ser númerico.")

    digito_calculado = calcular_digito_verificador(cuerpo)

    if digito_recibido != digito_calculado:
        raise ValueError("El RUT ingresado no es válido.")

    return f"{int(cuerpo)} - {digito_recibido}"


def validar_edad(edad: Any) -> int:
    """
    Valida que la edad sea un número entero entre 0 y 120.
    """

    if isinstance(edad, bool):
        raise ValueError("La edad debe ser un número entero.")

    try:
        edad_numerica = int(edad)
    except (TypeError, ValueError) as error:
        raise ValueError("La edad debe ser un número entero.") from error

    # Evita que un valor como 20.5 sea transformado silenciosamente a 20.
    if isinstance(edad, float) and not edad.is_integer():
        raise ValueError("La edad no puede contener decimales.")

    if isinstance(edad, str) and not re.fullmatch(r"\d{1,3}", edad.strip()):
        raise ValueError("La edad debe contener solo números enteros.")

    if edad_numerica < EDAD_MINIMA or edad_numerica > EDAD_MAXIMA:
        raise ValueError(
            f"La edad debe estar entre {EDAD_MINIMA}"
            f"y {EDAD_MAXIMA} años."
        )

    return edad_numerica


def validar_correo(correo: str) -> str:
    """
    Realiza una validación básica de correo electrónico.

    No intenta comprobar que la cuenta realmente exista.
    """

    correo = asegurar_texto(correo, "correo").lower()

    if len(correo) > 254:
        raise ValueError("El correo electrónico es demasido largo.")

    patron = re.compile(
        r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
    )

    if not patron.fullmatch(correo):
        raise ValueError("El correo electrónico no tiene un formato válido.")

    return correo


def sanitizar_diagnostico(diagnostico: str) -> str:
    """
    Sanitiza un diagnóstico de demostración.

    Para este ejercicio se permiten letras, números y signos básicos.
    Se eliminan etiquetas HTML y caracteres de control.
    """

    diagnostico = asegurar_texto(diagnostico, "diagnostico")

    # Elimina etiquetas similares a HTML.
    diagnostico = re.sub(r"<[^>]*>", "", diagnostico)

    # Elimina caracteres de control.
    diagnostico = re.sub(r"[\x00-\x1f\x7f]", "", diagnostico)

    # Conserva solamente caracteres permitidos.
    diagnostico = re.sub(
        r"[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ0-9 .,;:()'/-]",
        "",
        diagnostico,
    )

    diagnostico = re.sub(r"\s+", " ", diagnostico).strip()

    if not diagnostico:
        raise ValueError("El diagnostico no puede estar vacío.")

    if len(diagnostico) < 3:
        raise ValueError(
            "El diagnóstico debe contener al menos 3 caracteres."
        )

    if len(diagnostico) > LONGITUD_MAXIMA_DIAGNOSTICO:
        raise ValueError(
            f"El diagnostico no puede superar "
            f"{LONGITUD_MAXIMA_DIAGNOSTICO} caracteres."

        )

    return diagnostico


def sanitizar_estructura_paciente(datos: dict[str, Any]) -> dict[str, Any]:
    """
    Valida y sanitiza una estructura completa de paciente.
    Esta función evita confiar en que los datos del diccionario ya
    fueron validados individualmente.
    """
    if not isinstance(datos, dict):
        raise ValueError("Los datos del paciente deben ser un diccionario.")

    campos_requeridos = {
        "nombre",
        "rut",
        "edad",
        "correo",
        "diagnostico",
    }

    campos_recibidos = set(datos.keys())

    campos_faltantes = campos_requeridos - campos_recibidos

    if campos_faltantes:
        campos = ", ".join(sorted(campos_faltantes))
        raise ValueError(f"Faltan los siguientes campos: {campos}.")

    return {
        "nombre": sanitizar_nombre(datos["nombre"]),
        "rut": validar_rut(datos["rut"]),
        "edad": validar_edad(datos["edad"]),
        "correo": validar_correo(datos["correo"]),
        "diagnostico": sanitizar_diagnostico(
            datos["diagnostico"]
        ),
    }

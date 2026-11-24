"""Configuración centralizada del registro de eventos y errores del sistema."""

import logging

_FORMATO_LOG = "%(asctime)s - %(levelname)s - %(message)s"
_NOMBRE_LOGGER = "software_fj"


def obtener_logger(nombre: str) -> logging.Logger:
    """Retorna un logger de dominio conectado al archivo central del sistema."""
    logger_raiz = logging.getLogger(_NOMBRE_LOGGER)
    logger_raiz.setLevel(logging.INFO)
    logger_raiz.propagate = False

    # La marca evita registrar el mismo evento varias veces si se importa el
    # paquete desde distintos módulos de modelos.
    if not any(
        getattr(manejador, "_software_fj_archivo", False)
        for manejador in logger_raiz.handlers
    ):
        manejador_archivo = logging.FileHandler(
            filename="software_fj.log",
            encoding="utf-8",
        )
        manejador_archivo.setFormatter(logging.Formatter(_FORMATO_LOG))
        setattr(manejador_archivo, "_software_fj_archivo", True)
        logger_raiz.addHandler(manejador_archivo)

    return logger_raiz.getChild(nombre)

"""Define el modelo Cliente y valida sus datos de contacto e identificación."""

import re

from utilidades.excepciones import ClienteInvalidoError
from utilidades.logger import obtener_logger

from .entidad import Entidad

_LOGGER = obtener_logger(__name__)

# El documento admite letras, números, puntos y guiones, con longitud de 5 a 20.
_PATRON_DOCUMENTO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{3,18}[A-Za-z0-9]$")

# Se valida un correo común: usuario, dominio con etiquetas válidas y TLD de 2 a 63 letras.
_PATRON_CORREO = re.compile(
    r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)

# Se permiten números internacionales y separadores telefónicos habituales.
_PATRON_TELEFONO = re.compile(r"^\+?[0-9][0-9\s().-]*[0-9]$")


class Cliente(Entidad):
    """Representa un cliente con datos privados y propiedades validadas."""

    def __init__(
        self, nombre: str, documento: str, correo: str, telefono: str
    ) -> None:
        """Crea un cliente y valida todos sus datos antes de almacenarlos."""
        super().__init__()
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        _LOGGER.info("Cliente creado correctamente: %s", self.identificador)

    @property
    def nombre(self) -> str:
        """Retorna el nombre del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Almacena el nombre sin espacios externos y rechaza valores vacíos."""
        try:
            if not isinstance(valor, str):
                raise TypeError("El nombre debe ser una cadena de texto.")
            nombre_limpio = valor.strip()
            if not nombre_limpio:
                raise ValueError("El nombre no puede estar vacío.")
            if any(not caracter.isprintable() for caracter in nombre_limpio):
                raise ValueError("El nombre contiene caracteres no válidos.")
            self.__nombre = nombre_limpio
        except (TypeError, ValueError) as error:
            _LOGGER.exception("No se pudo validar el nombre del cliente.")
            raise ClienteInvalidoError(str(error)) from error

    @property
    def documento(self) -> str:
        """Retorna el documento de identificación del cliente."""
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        """Valida el formato general del documento antes de almacenarlo."""
        try:
            if not isinstance(valor, str):
                raise TypeError("El documento debe ser una cadena de texto.")
            documento_limpio = valor.strip()
            if not _PATRON_DOCUMENTO.fullmatch(documento_limpio):
                raise ValueError(
                    "El documento debe tener entre 5 y 20 caracteres "
                    "alfanuméricos; puede incluir puntos o guiones internos."
                )
            self.__documento = documento_limpio
        except (TypeError, ValueError) as error:
            _LOGGER.exception("No se pudo validar el documento del cliente.")
            raise ClienteInvalidoError(str(error)) from error

    @property
    def correo(self) -> str:
        """Retorna el correo electrónico del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato del correo y lo almacena en minúsculas."""
        try:
            if not isinstance(valor, str):
                raise TypeError("El correo debe ser una cadena de texto.")
            correo_limpio = valor.strip()
            if not _PATRON_CORREO.fullmatch(correo_limpio):
                raise ValueError("El correo electrónico tiene un formato no válido.")
            self.__correo = correo_limpio.lower()
        except (TypeError, ValueError) as error:
            _LOGGER.exception("No se pudo validar el correo del cliente.")
            raise ClienteInvalidoError(str(error)) from error

    @property
    def telefono(self) -> str:
        """Retorna el teléfono del cliente en el formato proporcionado."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida un teléfono de 7 a 15 dígitos y separadores habituales."""
        try:
            if not isinstance(valor, str):
                raise TypeError("El teléfono debe ser una cadena de texto.")
            telefono_limpio = valor.strip()
            cantidad_digitos = sum(
                caracter.isdigit() for caracter in telefono_limpio
            )
            if (
                not _PATRON_TELEFONO.fullmatch(telefono_limpio)
                or not 7 <= cantidad_digitos <= 15
                or ("(" in telefono_limpio) != (")" in telefono_limpio)
                or telefono_limpio.count("(") > 1
                or telefono_limpio.count(")") > 1
                or (
                    "(" in telefono_limpio
                    and telefono_limpio.index("(") > telefono_limpio.index(")")
                )
            ):
                raise ValueError(
                    "El teléfono debe contener entre 7 y 15 dígitos y usar "
                    "un formato telefónico válido."
                )
            self.__telefono = telefono_limpio
        except (TypeError, ValueError) as error:
            _LOGGER.exception("No se pudo validar el teléfono del cliente.")
            raise ClienteInvalidoError(str(error)) from error

    def obtener_resumen(self) -> str:
        """Retorna un resumen del cliente sin exponer datos sensibles."""
        return f"Cliente: {self.nombre} (documento: {self.documento})"

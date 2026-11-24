"""Define la estructura abstracta compartida por las entidades del sistema."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import UUID, uuid4


class Entidad(ABC):
    """Base abstracta con identificador único y fecha de creación."""

    def __init__(self) -> None:
        """Genera la identidad y registra la fecha de creación en UTC."""
        self.__identificador: UUID = uuid4()
        self.__fecha_creacion: datetime = datetime.now(timezone.utc)

    @property
    def identificador(self) -> UUID:
        """Retorna el identificador único e inmutable de la entidad."""
        return self.__identificador

    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la fecha y hora de creación, con zona horaria UTC."""
        return self.__fecha_creacion

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Retorna una descripción legible de la entidad concreta."""
        raise NotImplementedError(
            "Las entidades concretas deben implementar obtener_resumen()."
        )

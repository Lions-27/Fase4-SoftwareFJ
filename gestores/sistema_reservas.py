"""Gestión en memoria de clientes, servicios y reservas."""

from decimal import Decimal

from modelos.cliente import Cliente
from modelos.reserva import Reserva
from modelos.servicio import Servicio
from utilidades.excepciones import (
    ClienteInvalidoError,
    ReservaError,
    ServicioInvalidoError,
)
from utilidades.logger import obtener_logger

_LOGGER = obtener_logger(__name__)


class SistemaReservas:
    """Administra las colecciones del sistema únicamente mediante listas."""

    def __init__(self) -> None:
        """Crea las tres listas en memoria que almacenan los objetos del sistema."""
        self.__clientes: list[Cliente] = []
        self.__servicios: list[Servicio] = []
        self.__reservas: list[Reserva] = []
        _LOGGER.info("Gestor de reservas inicializado en memoria.")

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        """Expone una vista inmutable de los clientes registrados."""
        return tuple(self.__clientes)

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        """Expone una vista inmutable de los servicios registrados."""
        return tuple(self.__servicios)

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        """Expone una vista inmutable de las reservas registradas."""
        return tuple(self.__reservas)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        """Añade un cliente válido y evita duplicar su documento."""
        if not isinstance(cliente, Cliente):
            causa = TypeError("Solo se pueden registrar objetos Cliente.")
            _LOGGER.error("Registro de cliente rechazado: %s", causa)
            raise ClienteInvalidoError(str(causa)) from causa
        if any(
            existente.documento.casefold() == cliente.documento.casefold()
            for existente in self.__clientes
        ):
            causa = ValueError(
                f"El documento {cliente.documento} ya pertenece a un cliente."
            )
            _LOGGER.error("Registro de cliente duplicado: %s", causa)
            raise ClienteInvalidoError(str(causa)) from causa
        self.__clientes.append(cliente)
        _LOGGER.info("Cliente registrado: %s", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        """Añade un servicio válido y evita registrar la misma instancia."""
        if not isinstance(servicio, Servicio):
            causa = TypeError("Solo se pueden registrar objetos Servicio.")
            _LOGGER.error("Registro de servicio rechazado: %s", causa)
            raise ServicioInvalidoError(str(causa)) from causa
        if any(
            existente.identificador == servicio.identificador
            for existente in self.__servicios
        ):
            causa = ValueError("El servicio ya está registrado en el sistema.")
            _LOGGER.error("Registro de servicio duplicado: %s", causa)
            raise ServicioInvalidoError(str(causa)) from causa
        self.__servicios.append(servicio)
        _LOGGER.info("Servicio registrado: %s", servicio.identificador)
        return servicio

    def crear_reserva(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int | float | Decimal,
    ) -> Reserva:
        """Crea y registra una reserva de objetos que ya pertenecen al sistema."""
        if cliente not in self.__clientes:
            causa = ValueError("El cliente debe estar registrado en el sistema.")
            _LOGGER.error("Creación de reserva rechazada: %s", causa)
            raise ReservaError(str(causa)) from causa
        if servicio not in self.__servicios:
            causa = ValueError("El servicio debe estar registrado en el sistema.")
            _LOGGER.error("Creación de reserva rechazada: %s", causa)
            raise ReservaError(str(causa)) from causa
        reserva = Reserva(cliente, servicio, duracion)
        self.__reservas.append(reserva)
        _LOGGER.info("Reserva añadida al sistema: %s", reserva.identificador)
        return reserva

    def obtener_resumen(self) -> str:
        """Genera un resumen legible del contenido actual de las tres listas."""
        return (
            f"Clientes: {len(self.__clientes)}; "
            f"servicios: {len(self.__servicios)}; "
            f"reservas: {len(self.__reservas)}."
        )

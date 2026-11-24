"""Define reservas de clientes para los servicios ofrecidos por la empresa."""

from decimal import Decimal

from utilidades.excepciones import (
    CalculoCostoError,
    DuracionInvalidaError,
    EstadoReservaInvalidoError,
    ReservaError,
    ServicioNoDisponibleError,
)
from utilidades.logger import obtener_logger

from .cliente import Cliente
from .entidad import Entidad
from .servicio import Servicio

_LOGGER = obtener_logger(__name__)


class Reserva(Entidad):
    """Vincula un cliente con un servicio y controla su ciclo de vida."""

    ESTADOS_VALIDOS = ("pendiente", "confirmada", "procesada", "cancelada")

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int | float | Decimal,
    ) -> None:
        """Crea una reserva pendiente y valida sus participantes y duración."""
        super().__init__()
        if not isinstance(cliente, Cliente):
            error = TypeError("La reserva requiere un objeto Cliente válido.")
            _LOGGER.error("%s", error)
            raise ReservaError(str(error)) from error
        if not isinstance(servicio, Servicio):
            error = TypeError("La reserva requiere un objeto Servicio válido.")
            _LOGGER.error("%s", error)
            raise ReservaError(str(error)) from error
        if not servicio.disponible:
            error = ValueError("No se puede reservar un servicio no disponible.")
            _LOGGER.error("%s", error)
            raise ServicioNoDisponibleError(str(error)) from error
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = self._validar_duracion(duracion)
        self.__estado = "pendiente"
        self.__costo_total: Decimal | None = None
        _LOGGER.info("Reserva creada correctamente: %s", self.identificador)

    @staticmethod
    def _validar_duracion(valor: int | float | Decimal) -> Decimal:
        """Valida una duración numérica finita y estrictamente positiva."""
        try:
            duracion = Servicio._decimal_no_negativo(valor, "La duración")
            if duracion == 0:
                raise ValueError("La duración debe ser mayor que cero.")
        except (TypeError, ValueError) as error:
            _LOGGER.exception("La duración de la reserva no es válida.")
            raise DuracionInvalidaError(str(error)) from error
        return duracion

    @property
    def cliente(self) -> Cliente:
        """Retorna el cliente vinculado a la reserva."""
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        """Retorna el servicio vinculado a la reserva."""
        return self.__servicio

    @property
    def duracion(self) -> Decimal:
        """Retorna la duración de la reserva."""
        return self.__duracion

    @property
    def estado(self) -> str:
        """Retorna el estado actual de la reserva."""
        return self.__estado

    @property
    def costo_total(self) -> Decimal | None:
        """Retorna el costo final una vez procesada la reserva."""
        return self.__costo_total

    def confirmar(self) -> None:
        """Confirma una reserva pendiente si el servicio sigue disponible."""
        try:
            if self.__estado != "pendiente":
                raise ValueError("Solo se pueden confirmar reservas pendientes.")
        except ValueError as error:
            _LOGGER.exception("No se pudo confirmar la reserva %s.", self.identificador)
            raise EstadoReservaInvalidoError(str(error)) from error
        try:
            if not self.servicio.disponible:
                raise ValueError(
                    "El servicio ya no está disponible para confirmación."
                )
        except ValueError as error:
            _LOGGER.exception("No se pudo confirmar la reserva %s.", self.identificador)
            raise ServicioNoDisponibleError(str(error)) from error
        self.__estado = "confirmada"
        _LOGGER.info("Reserva confirmada: %s", self.identificador)

    def cancelar(self) -> None:
        """Cancela una reserva pendiente o confirmada."""
        try:
            if self.__estado not in ("pendiente", "confirmada"):
                raise ValueError(
                    "Solo se pueden cancelar reservas pendientes o confirmadas."
                )
        except ValueError as error:
            _LOGGER.exception("No se pudo cancelar la reserva %s.", self.identificador)
            raise EstadoReservaInvalidoError(str(error)) from error
        self.__estado = "cancelada"
        _LOGGER.info("Reserva cancelada: %s", self.identificador)

    def procesar(
        self,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula y guarda el costo y cambia una reserva confirmada a procesada."""
        try:
            if self.__estado != "confirmada":
                raise ValueError(
                    "Solo se pueden procesar reservas confirmadas."
                )
        except ValueError as error:
            _LOGGER.exception("No se pudo procesar la reserva %s.", self.identificador)
            raise EstadoReservaInvalidoError(str(error)) from error
        try:
            costo = self.servicio.calcular_costo(
                self.duracion,
                descuento_porcentaje=descuento_porcentaje,
                iva_porcentaje=iva_porcentaje,
                recargo=recargo,
            )
        except CalculoCostoError as error:
            _LOGGER.exception(
                "Falló el cálculo al procesar la reserva %s.", self.identificador
            )
            raise CalculoCostoError(
                "No se pudo procesar el costo de la reserva."
            ) from error
        self.__costo_total = costo
        self.__estado = "procesada"
        _LOGGER.info("Reserva procesada: %s; costo total: %s", self.identificador, costo)
        return costo

    def calcular_costo_total(
        self,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula el costo a partir del servicio sin cambiar el estado."""
        try:
            costo = self.servicio.calcular_costo(
                self.duracion,
                descuento_porcentaje=descuento_porcentaje,
                iva_porcentaje=iva_porcentaje,
                recargo=recargo,
            )
        except CalculoCostoError as error:
            _LOGGER.exception(
                "No se pudo calcular el costo de la reserva %s.", self.identificador
            )
            raise CalculoCostoError(
                "No se pudo calcular el costo total de la reserva."
            ) from error
        _LOGGER.info(
            "Costo de reserva calculado: %s; valor: %s", self.identificador, costo
        )
        return costo

    def obtener_resumen(self) -> str:
        """Retorna un resumen de la reserva sin exponer datos de contacto."""
        return (
            f"Reserva {self.identificador}: {self.servicio.nombre} para "
            f"{self.cliente.nombre}, estado {self.estado}"
        )

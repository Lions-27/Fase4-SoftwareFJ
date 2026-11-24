"""Define reservas de clientes para los servicios ofrecidos por la empresa."""

from decimal import Decimal

from .cliente import Cliente
from .entidad import Entidad
from .servicio import Servicio


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
            raise TypeError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise TypeError("La reserva requiere un objeto Servicio válido.")
        if not servicio.disponible:
            raise ValueError("No se puede reservar un servicio no disponible.")
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = self._validar_duracion(duracion)
        self.__estado = "pendiente"
        self.__costo_total: Decimal | None = None

    @staticmethod
    def _validar_duracion(valor: int | float | Decimal) -> Decimal:
        """Valida una duración numérica finita y estrictamente positiva."""
        duracion = Servicio._decimal_no_negativo(valor, "La duración")
        if duracion == 0:
            raise ValueError("La duración debe ser mayor que cero.")
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
        if self.__estado != "pendiente":
            raise ValueError("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.disponible:
            raise ValueError("El servicio ya no está disponible para confirmación.")
        self.__estado = "confirmada"

    def cancelar(self) -> None:
        """Cancela una reserva pendiente o confirmada."""
        if self.__estado not in ("pendiente", "confirmada"):
            raise ValueError("Solo se pueden cancelar reservas pendientes o confirmadas.")
        self.__estado = "cancelada"

    def procesar(
        self,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula y guarda el costo y cambia una reserva confirmada a procesada."""
        if self.__estado != "confirmada":
            raise ValueError("Solo se pueden procesar reservas confirmadas.")
        costo = self.servicio.calcular_costo(
            self.duracion,
            descuento_porcentaje=descuento_porcentaje,
            iva_porcentaje=iva_porcentaje,
            recargo=recargo,
        )
        self.__costo_total = costo
        self.__estado = "procesada"
        return costo

    def calcular_costo_total(
        self,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula el costo a partir del servicio sin cambiar el estado."""
        return self.servicio.calcular_costo(
            self.duracion,
            descuento_porcentaje=descuento_porcentaje,
            iva_porcentaje=iva_porcentaje,
            recargo=recargo,
        )

    def obtener_resumen(self) -> str:
        """Retorna un resumen de la reserva sin exponer datos de contacto."""
        return (
            f"Reserva {self.identificador}: {self.servicio.nombre} para "
            f"{self.cliente.nombre}, estado {self.estado}"
        )

"""Excepciones de dominio para errores identificables de Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Excepción base de los errores controlados del sistema."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Indica que los datos de un cliente no cumplen las validaciones."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Indica que los datos de un servicio no cumplen las validaciones."""


class ServicioNoDisponibleError(ServicioInvalidoError):
    """Indica que se intentó reservar un servicio no disponible."""


class ReservaError(ErrorSoftwareFJ):
    """Indica un error general al crear o gestionar una reserva."""


class EstadoReservaInvalidoError(ReservaError):
    """Indica que una operación no es válida para el estado de la reserva."""


class DuracionInvalidaError(ReservaError):
    """Indica que la duración de una reserva no es válida."""


class CalculoCostoError(ReservaError, ServicioInvalidoError):
    """Indica que no se pudo calcular un costo de servicio o de reserva."""

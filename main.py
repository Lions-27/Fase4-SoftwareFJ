"""Punto de entrada con simulaciones seguras del sistema de reservas."""

from collections.abc import Callable

from gestores import SistemaReservas
from modelos import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    ReservaSala,
)
from utilidades.excepciones import (
    CalculoCostoError,
    ClienteInvalidoError,
    DuracionInvalidaError,
    EstadoReservaInvalidoError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from utilidades.logger import obtener_logger

_LOGGER = obtener_logger(__name__)


def _mostrar_causa_encadenada(error: BaseException) -> None:
    """Imprime y registra cada causa original asociada a un error."""
    causa = error.__cause__
    nivel = 1
    while causa is not None:
        mensaje = f"Causa encadenada {nivel}: {type(causa).__name__}: {causa}"
        print(f"  {mensaje}")
        _LOGGER.error("%s", mensaje)
        causa = causa.__cause__
        nivel += 1


def _esperar_excepcion(
    descripcion: str,
    excepcion_esperada: type[Exception],
    operacion: Callable[[], object],
) -> None:
    """Verifica que una operación falle con la excepción esperada y continúa."""
    try:
        operacion()
    except excepcion_esperada as error:
        mensaje = (
            f"{descripcion}: se capturó "
            f"{type(error).__name__}: {error}"
        )
        print(mensaje)
        _LOGGER.exception("%s", mensaje)
        # La causa explícita conserva el motivo inicial de la validación.
        _mostrar_causa_encadenada(error)
    except Exception as error:
        mensaje = (
            f"{descripcion}: ocurrió una excepción distinta, "
            f"{type(error).__name__}: {error}"
        )
        print(mensaje)
        _LOGGER.exception("%s", mensaje)
        _mostrar_causa_encadenada(error)
    else:
        mensaje = f"{descripcion}: no ocurrió la excepción esperada."
        print(mensaje)
        _LOGGER.error("%s", mensaje)
        raise AssertionError(mensaje)
    finally:
        # Se registra el cierre del intento incluso si ocurre un fallo inesperado.
        _LOGGER.info("Finalizó la comprobación: %s", descripcion)


def _ejecutar_simulacion(
    nombre: str,
    operacion: Callable[[], object],
) -> None:
    """Ejecuta una simulación aislada, registra su resultado y no detiene la serie."""
    print(f"\nSimulación: {nombre}")
    try:
        operacion()
    except Exception as error:
        # Captura errores inesperados para permitir que corra la siguiente prueba.
        print(f"Error capturado; la ejecución continuará: {error}")
        _LOGGER.exception("Falló la simulación: %s", nombre)
        _mostrar_causa_encadenada(error)
    else:
        print("Resultado: completada.")
        _LOGGER.info("Simulación completada: %s", nombre)
    finally:
        # Separador y registro incondicional para mostrar que el bloque terminó.
        print("-" * 60)
        _LOGGER.info("Fin de la simulación: %s", nombre)


def _crear_simulaciones(sistema: SistemaReservas) -> list[tuple[str, Callable[[], object]]]:
    """Construye las operaciones de prueba sobre el gestor en memoria."""
    def registrar_cliente_valido() -> None:
        """Registra el cliente de prueba que utilizarán las reservas."""
        cliente = Cliente(
            "Andrés Felipe Leones Rosado",
            "CC-10203040",
            "andres@example.com",
            "+57 300 123 4567",
        )
        sistema.registrar_cliente(cliente)
        print(cliente.obtener_resumen())

    def registrar_sala_valida() -> None:
        """Crea y registra una sala válida."""
        sala = ReservaSala(
            "Sala principal",
            120000,
            "Sala para reuniones y capacitaciones.",
            20,
            ["Proyector", "Pizarra", "Videoconferencia"],
        )
        sistema.registrar_servicio(sala)
        print(sala.obtener_resumen())

    def registrar_equipo_valido() -> None:
        """Crea y registra un servicio de alquiler de equipos."""
        equipo = AlquilerEquipo(
            "Alquiler de portátiles",
            25000,
            "Portátiles para actividades empresariales.",
            "Computador portátil",
            3,
        )
        sistema.registrar_servicio(equipo)
        print(equipo.obtener_resumen())

    def registrar_asesoria_valida() -> None:
        """Crea y registra una asesoría especializada."""
        asesoria = AsesoriaEspecializada(
            "Asesoría de software",
            90000,
            "Acompañamiento en diseño de software.",
            "Arquitectura de software",
            "Laura Gómez",
        )
        sistema.registrar_servicio(asesoria)
        print(asesoria.obtener_resumen())

    def calcular_costos() -> None:
        """Ejecuta las variantes de costo básico, descuento, impuestos y recargo."""
        sala = sistema.servicios[0]
        print(f"Costo básico por dos horas: ${sala.calcular_costo(2)}")
        print(
            "Costo con descuento del 10 %: "
            f"${sala.calcular_costo(2, descuento_porcentaje=10)}"
        )
        print(
            "Costo con IVA del 19 %: "
            f"${sala.calcular_costo(2, iva_porcentaje=19)}"
        )
        print(
            "Costo con descuento, IVA y recargo: "
            f"${sala.calcular_costo(2, 10, 19, 15000)}"
        )

    def crear_reserva_valida() -> None:
        """Crea una reserva válida pendiente con cliente y sala registrados."""
        reserva = sistema.crear_reserva(
            sistema.clientes[0],
            sistema.servicios[0],
            2,
        )
        print(reserva.obtener_resumen())

    def confirmar_y_procesar_reserva() -> None:
        """Confirma y procesa la primera reserva con IVA y un descuento."""
        reserva = sistema.reservas[0]
        reserva.confirmar()
        costo = reserva.procesar(descuento_porcentaje=5, iva_porcentaje=19)
        print(f"Reserva procesada; costo total: ${costo}.")

    def crear_y_cancelar_reserva() -> None:
        """Crea y cancela correctamente una reserva pendiente."""
        reserva = sistema.crear_reserva(
            sistema.clientes[0],
            sistema.servicios[1],
            3,
        )
        reserva.cancelar()
        print(f"Reserva cancelada correctamente: {reserva.estado}.")

    def verificar_nombre_invalido() -> None:
        """Prueba el rechazo de un cliente cuyo nombre está vacío."""
        _esperar_excepcion(
            "Cliente con nombre vacío",
            ClienteInvalidoError,
            lambda: Cliente("", "CC-10203041", "valido@example.com", "3001234567"),
        )

    def verificar_documento_invalido() -> None:
        """Prueba el rechazo de un documento con formato incorrecto."""
        _esperar_excepcion(
            "Cliente con documento inválido",
            ClienteInvalidoError,
            lambda: Cliente(
                "Cliente de prueba", "12", "valido@example.com", "3001234567"
            ),
        )

    def verificar_correo_invalido() -> None:
        """Prueba el rechazo de una dirección de correo mal formada."""
        _esperar_excepcion(
            "Cliente con correo inválido",
            ClienteInvalidoError,
            lambda: Cliente("Cliente de prueba", "CC-12345", "correo-malo", "3001234567"),
        )

    def verificar_tarifa_invalida() -> None:
        """Prueba el rechazo de una tarifa no numérica en una sala."""
        _esperar_excepcion(
            "Reserva de sala con tarifa inválida",
            ServicioInvalidoError,
            lambda: ReservaSala(
                "Sala inválida", "sin tarifa", "Descripción", 10, []
            ),
        )

    def verificar_capacidad_invalida() -> None:
        """Prueba el rechazo de una capacidad cero en una sala."""
        _esperar_excepcion(
            "Reserva de sala con capacidad inválida",
            ServicioInvalidoError,
            lambda: ReservaSala("Sala pequeña", 50000, "Descripción", 0, []),
        )

    def verificar_cantidad_invalida() -> None:
        """Prueba el rechazo de una cantidad cero para alquiler de equipos."""
        _esperar_excepcion(
            "Alquiler de equipo con cantidad inválida",
            ServicioInvalidoError,
            lambda: AlquilerEquipo(
                "Equipo inválido", 20000, "Descripción", "Tableta", 0
            ),
        )

    def verificar_consultor_invalido() -> None:
        """Prueba el rechazo de una asesoría sin nombre de consultor."""
        _esperar_excepcion(
            "Asesoría con consultor inválido",
            ServicioInvalidoError,
            lambda: AsesoriaEspecializada(
                "Asesoría inválida", 80000, "Descripción", "Seguridad", ""
            ),
        )

    def verificar_duracion_invalida() -> None:
        """Prueba el rechazo de una reserva cuya duración no es numérica."""
        _esperar_excepcion(
            "Reserva con duración inválida",
            DuracionInvalidaError,
            lambda: sistema.crear_reserva(
                sistema.clientes[0], sistema.servicios[0], "muchas horas"
            ),
        )

    def verificar_servicio_no_disponible() -> None:
        """Prueba que una reserva no se cree para un servicio no disponible."""
        servicio = ReservaSala(
            "Sala temporalmente cerrada",
            40000,
            "Sala fuera de servicio.",
            8,
            [],
            disponible=False,
        )
        sistema.registrar_servicio(servicio)
        _esperar_excepcion(
            "Reserva de servicio no disponible",
            ServicioNoDisponibleError,
            lambda: sistema.crear_reserva(
                sistema.clientes[0], servicio, 1
            ),
        )

    def intentar_procesar_reserva_cancelada() -> None:
        """Prueba que una reserva cancelada no pueda procesarse."""
        reserva = sistema.reservas[1]
        _esperar_excepcion(
            "Procesamiento de reserva cancelada",
            EstadoReservaInvalidoError,
            reserva.procesar,
        )

    def intentar_confirmar_reserva_procesada() -> None:
        """Prueba que una reserva procesada no vuelva a confirmarse."""
        reserva = sistema.reservas[0]
        _esperar_excepcion(
            "Confirmación repetida de reserva procesada",
            EstadoReservaInvalidoError,
            reserva.confirmar,
        )

    def verificar_costo_invalido() -> None:
        """Prueba que el descuento superior al cien por ciento sea rechazado."""
        sala = sistema.servicios[0]
        _esperar_excepcion(
            "Cálculo con descuento fuera de rango",
            CalculoCostoError,
            lambda: sala.calcular_costo(1, descuento_porcentaje=101),
        )

    def verificar_cliente_duplicado() -> None:
        """Prueba que el gestor impida registrar dos veces el mismo documento."""
        duplicado = Cliente(
            "Cliente repetido",
            sistema.clientes[0].documento,
            "repetido@example.com",
            "3001234568",
        )
        _esperar_excepcion(
            "Registro de documento duplicado",
            ClienteInvalidoError,
            lambda: sistema.registrar_cliente(duplicado),
        )

    return [
        ("registro de cliente válido", registrar_cliente_valido),
        ("registro de cliente con nombre vacío", verificar_nombre_invalido),
        ("registro de cliente con documento inválido", verificar_documento_invalido),
        ("registro de cliente con correo inválido", verificar_correo_invalido),
        ("creación de reserva de sala válida", registrar_sala_valida),
        ("creación de alquiler de equipo válido", registrar_equipo_valido),
        ("creación de asesoría especializada válida", registrar_asesoria_valida),
        ("tarifa inválida para una reserva de sala", verificar_tarifa_invalida),
        ("capacidad inválida para una reserva de sala", verificar_capacidad_invalida),
        ("cantidad inválida para alquiler de equipo", verificar_cantidad_invalida),
        ("consultor inválido para una asesoría", verificar_consultor_invalido),
        ("variantes de cálculo de costos", calcular_costos),
        ("creación de reserva válida", crear_reserva_valida),
        ("duración inválida para una reserva", verificar_duracion_invalida),
        ("servicio no disponible para una reserva", verificar_servicio_no_disponible),
        ("confirmación y procesamiento de reserva", confirmar_y_procesar_reserva),
        ("creación y cancelación de reserva", crear_y_cancelar_reserva),
        ("procesamiento de una reserva cancelada", intentar_procesar_reserva_cancelada),
        ("confirmación repetida de reserva procesada", intentar_confirmar_reserva_procesada),
        ("cálculo con descuento inválido", verificar_costo_invalido),
        ("registro de cliente duplicado", verificar_cliente_duplicado),
    ]


def main() -> None:
    """Ejecuta todas las simulaciones y muestra el estado final en memoria."""
    print("Sistema Integral de Gestión de Clientes, Servicios y Reservas")
    print("Simulaciones de Software FJ")
    sistema = SistemaReservas()
    simulaciones = _crear_simulaciones(sistema)

    for numero, (nombre, operacion) in enumerate(simulaciones, start=1):
        _ejecutar_simulacion(f"{numero} de {len(simulaciones)}: {nombre}", operacion)

    # El resumen se presenta aunque haya fallado una o más simulaciones.
    print("\nResumen final del estado en memoria")
    print(sistema.obtener_resumen())
    print("\nClientes registrados:")
    for cliente in sistema.clientes:
        print(f"- {cliente.obtener_resumen()}")
    print("\nServicios registrados:")
    for servicio in sistema.servicios:
        print(f"- {servicio.obtener_resumen()}")
    print("\nReservas registradas:")
    for reserva in sistema.reservas:
        costo = (
            f"${reserva.costo_total}"
            if reserva.costo_total is not None
            else "pendiente de cálculo"
        )
        print(f"- {reserva.obtener_resumen()}; costo: {costo}")
    _LOGGER.info("Todas las simulaciones finalizaron; %s", sistema.obtener_resumen())
    print("\nTodas las simulaciones finalizaron.")


if __name__ == "__main__":
    # Esta protección permite importar main sin ejecutar automáticamente las pruebas.
    try:
        main()
    except Exception as error:
        # Última barrera para mostrar el error y guardar su causa sin perder el log.
        print(f"Error general capturado; el programa terminó de forma controlada: {error}")
        _LOGGER.exception("Error general en el punto de entrada.")
        _mostrar_causa_encadenada(error)

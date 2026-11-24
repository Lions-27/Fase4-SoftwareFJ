"""Modelos de servicios ofrecidos por Software FJ."""

from abc import abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable

from .entidad import Entidad

_CENTAVO = Decimal("0.01")


class Servicio(Entidad):
    """Define los datos y cálculos comunes de un servicio contratable."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: int | float | Decimal,
        descripcion: str,
        disponible: bool = True,
    ) -> None:
        """Inicializa la identidad y valida los atributos comunes."""
        super().__init__()
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.descripcion = descripcion
        self.disponible = disponible

    @staticmethod
    def _texto_no_vacio(valor: str, atributo: str) -> str:
        """Valida texto obligatorio y elimina espacios externos."""
        if not isinstance(valor, str):
            raise TypeError(f"{atributo} debe ser una cadena de texto.")
        valor_limpio = valor.strip()
        if not valor_limpio:
            raise ValueError(f"{atributo} no puede estar vacío.")
        if any(not caracter.isprintable() for caracter in valor_limpio):
            raise ValueError(f"{atributo} contiene caracteres no válidos.")
        return valor_limpio

    @staticmethod
    def _decimal_no_negativo(valor: int | float | Decimal, atributo: str) -> Decimal:
        """Convierte una cantidad a Decimal y rechaza valores negativos o no finitos."""
        if isinstance(valor, bool):
            raise TypeError(f"{atributo} debe ser un valor numérico.")
        try:
            cantidad = Decimal(str(valor))
        except (InvalidOperation, ValueError):
            raise TypeError(f"{atributo} debe ser un valor numérico válido.") from None
        if not cantidad.is_finite() or cantidad < 0:
            raise ValueError(f"{atributo} debe ser finito y no negativo.")
        return cantidad

    @staticmethod
    def _entero_positivo(valor: int, atributo: str) -> int:
        """Valida que un atributo de cantidad sea un entero positivo."""
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(f"{atributo} debe ser un número entero.")
        if valor <= 0:
            raise ValueError(f"{atributo} debe ser mayor que cero.")
        return valor

    @staticmethod
    def _validar_porcentaje(valor: int | float | Decimal, atributo: str) -> Decimal:
        """Convierte un porcentaje a Decimal y verifica que no sea negativo."""
        return Servicio._decimal_no_negativo(valor, atributo)

    @property
    def nombre(self) -> str:
        """Retorna el nombre del servicio."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y almacena el nombre del servicio."""
        self.__nombre = self._texto_no_vacio(valor, "El nombre")

    @property
    def tarifa_base(self) -> Decimal:
        """Retorna la tarifa base del servicio como Decimal."""
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: int | float | Decimal) -> None:
        """Valida y almacena una tarifa base estrictamente positiva."""
        tarifa = self._decimal_no_negativo(valor, "La tarifa base")
        if tarifa == 0:
            raise ValueError("La tarifa base debe ser mayor que cero.")
        self.__tarifa_base = tarifa

    @property
    def descripcion(self) -> str:
        """Retorna la descripción del servicio."""
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        """Valida y almacena la descripción del servicio."""
        self.__descripcion = self._texto_no_vacio(valor, "La descripción")

    @property
    def disponible(self) -> bool:
        """Indica si el servicio puede ser reservado."""
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        """Almacena la disponibilidad únicamente si el valor es booleano."""
        if not isinstance(valor, bool):
            raise TypeError("La disponibilidad debe ser un valor booleano.")
        self.__disponible = valor

    def _calcular_costo(
        self,
        duracion: int | float | Decimal,
        descuento_porcentaje: int | float | Decimal,
        iva_porcentaje: int | float | Decimal,
        recargo: int | float | Decimal,
        multiplicador: int = 1,
    ) -> Decimal:
        """Calcula el subtotal, aplica descuento e IVA y redondea a centavos."""
        horas = self._decimal_no_negativo(duracion, "La duración")
        if horas == 0:
            raise ValueError("La duración debe ser mayor que cero.")
        descuento = self._validar_porcentaje(
            descuento_porcentaje, "El descuento porcentual"
        )
        if descuento > 100:
            raise ValueError("El descuento porcentual no puede superar el 100 %.")
        iva = self._validar_porcentaje(iva_porcentaje, "El IVA porcentual")
        recargo_valido = self._decimal_no_negativo(recargo, "El recargo")
        cantidad = self._entero_positivo(multiplicador, "El multiplicador")

        subtotal = self.tarifa_base * horas * cantidad + recargo_valido
        total_con_descuento = subtotal * (Decimal("1") - descuento / Decimal("100"))
        total_con_impuesto = total_con_descuento * (
            Decimal("1") + iva / Decimal("100")
        )
        return total_con_impuesto.quantize(_CENTAVO, rounding=ROUND_HALF_UP)

    @abstractmethod
    def calcular_costo(
        self,
        duracion: int | float | Decimal,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula el costo polimórfico con ajustes monetarios opcionales."""
        raise NotImplementedError(
            "Cada servicio concreto debe implementar calcular_costo()."
        )

    def obtener_resumen(self) -> str:
        """Retorna el nombre, tarifa y disponibilidad del servicio."""
        estado = "disponible" if self.disponible else "no disponible"
        return f"{type(self).__name__}: {self.nombre} - {self.tarifa_base} ({estado})"


class ReservaSala(Servicio):
    """Servicio de reserva de salas con capacidad y equipamiento definidos."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: int | float | Decimal,
        descripcion: str,
        capacidad: int,
        equipamiento: Iterable[str],
        disponible: bool = True,
    ) -> None:
        """Inicializa la sala y valida su capacidad y equipamiento."""
        super().__init__(nombre, tarifa_base, descripcion, disponible)
        self.capacidad = capacidad
        self.equipamiento = equipamiento

    @property
    def capacidad(self) -> int:
        """Retorna la cantidad máxima de personas que admite la sala."""
        return self.__capacidad

    @capacidad.setter
    def capacidad(self, valor: int) -> None:
        """Valida y almacena la capacidad de la sala."""
        self.__capacidad = self._entero_positivo(valor, "La capacidad")

    @property
    def equipamiento(self) -> tuple[str, ...]:
        """Retorna el equipamiento de la sala como una tupla inmutable."""
        return self.__equipamiento

    @equipamiento.setter
    def equipamiento(self, valores: Iterable[str]) -> None:
        """Valida y almacena una lista inmutable de equipos no repetidos."""
        if isinstance(valores, (str, bytes)):
            raise TypeError("El equipamiento debe ser una colección de elementos.")
        try:
            equipo_validado = tuple(
                self._texto_no_vacio(valor, "Cada elemento del equipamiento")
                for valor in valores
            )
        except TypeError:
            raise TypeError("El equipamiento debe ser una colección iterable.") from None
        if len({elemento.casefold() for elemento in equipo_validado}) != len(
            equipo_validado
        ):
            raise ValueError("El equipamiento no puede contener elementos repetidos.")
        self.__equipamiento = equipo_validado

    def calcular_costo(
        self,
        duracion: int | float | Decimal,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula la tarifa de sala por duración y ajustes opcionales."""
        return self._calcular_costo(
            duracion, descuento_porcentaje, iva_porcentaje, recargo
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por duración y cantidad."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: int | float | Decimal,
        descripcion: str,
        tipo_equipo: str,
        cantidad: int,
        disponible: bool = True,
    ) -> None:
        """Inicializa el equipo y valida su tipo y cantidad de unidades."""
        super().__init__(nombre, tarifa_base, descripcion, disponible)
        self.tipo_equipo = tipo_equipo
        self.cantidad = cantidad

    @property
    def tipo_equipo(self) -> str:
        """Retorna el tipo de equipo que se ofrece en alquiler."""
        return self.__tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor: str) -> None:
        """Valida y almacena el tipo de equipo."""
        self.__tipo_equipo = self._texto_no_vacio(valor, "El tipo de equipo")

    @property
    def cantidad(self) -> int:
        """Retorna la cantidad de unidades solicitadas."""
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        """Valida y almacena la cantidad de equipos."""
        self.__cantidad = self._entero_positivo(valor, "La cantidad")

    def calcular_costo(
        self,
        duracion: int | float | Decimal,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula el alquiler multiplicado por unidades y ajustes opcionales."""
        return self._calcular_costo(
            duracion,
            descuento_porcentaje,
            iva_porcentaje,
            recargo,
            multiplicador=self.cantidad,
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con especialidad y consultor asignado."""

    def __init__(
        self,
        nombre: str,
        tarifa_base: int | float | Decimal,
        descripcion: str,
        especialidad: str,
        consultor: str,
        disponible: bool = True,
    ) -> None:
        """Inicializa la asesoría y valida sus datos profesionales."""
        super().__init__(nombre, tarifa_base, descripcion, disponible)
        self.especialidad = especialidad
        self.consultor = consultor

    @property
    def especialidad(self) -> str:
        """Retorna la especialidad de la asesoría."""
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor: str) -> None:
        """Valida y almacena la especialidad ofrecida."""
        self.__especialidad = self._texto_no_vacio(valor, "La especialidad")

    @property
    def consultor(self) -> str:
        """Retorna el nombre del consultor asignado."""
        return self.__consultor

    @consultor.setter
    def consultor(self, valor: str) -> None:
        """Valida y almacena el nombre del consultor."""
        self.__consultor = self._texto_no_vacio(valor, "El consultor")

    def calcular_costo(
        self,
        duracion: int | float | Decimal,
        descuento_porcentaje: int | float | Decimal = 0,
        iva_porcentaje: int | float | Decimal = 0,
        recargo: int | float | Decimal = 0,
    ) -> Decimal:
        """Calcula el costo de asesoría por duración y ajustes opcionales."""
        return self._calcular_costo(
            duracion, descuento_porcentaje, iva_porcentaje, recargo
        )

# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto académico en Python para la gestión en memoria de clientes, servicios y
reservas de Software FJ.

**Autor:** Andrés Felipe Leones Rosado

## Descripción

La aplicación demuestra programación orientada a objetos, validación de datos,
manejo de excepciones propias, registro centralizado y simulaciones completas.
Los clientes, servicios y reservas se conservan únicamente en listas durante la
ejecución. No se utilizan bases de datos.

## Arquitectura POO

- `Entidad` es la clase base abstracta con identificador y fecha de creación.
- `Cliente` hereda de `Entidad` y encapsula sus datos personales validados.
- `Servicio` hereda de `Entidad` y define la interfaz abstracta para calcular
  costos. `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` implementan
  el cálculo de forma polimórfica.
- `Reserva` hereda de `Entidad`, asocia un cliente con un servicio y controla
  los estados pendiente, confirmada, procesada y cancelada.
- `SistemaReservas` administra en memoria las listas de clientes, servicios y
  reservas, valida su registro y crea reservas con objetos registrados.

Los precios se calculan con `Decimal`, con soporte para descuento porcentual,
IVA y recargos adicionales.

## Excepciones y logs

`utilidades/excepciones.py` contiene la jerarquía de excepciones de dominio.
Las validaciones y operaciones registran éxitos y errores mediante el logger
central de `utilidades/logger.py`. El archivo `software_fj.log` se crea en el
directorio actual al ejecutar el programa y se escribe en UTF-8. Los errores
capturados conservan y muestran su causa encadenada cuando corresponde.

El archivo de log es un resultado local de ejecución y está excluido del control
de versiones por `.gitignore`.

## Estructura del proyecto

```text
Fase4-SoftwareFJ/
├── gestores/
│   ├── __init__.py
│   └── sistema_reservas.py
├── modelos/
│   ├── __init__.py
│   ├── cliente.py
│   ├── entidad.py
│   ├── reserva.py
│   └── servicio.py
├── utilidades/
│   ├── __init__.py
│   ├── excepciones.py
│   └── logger.py
├── main.py
├── README.md
└── .gitignore
```

## Requisitos

- Python 3.10 o posterior.
- No se requieren dependencias externas.

## Ejecución

Desde la carpeta raíz del proyecto:

```powershell
python main.py
```

En Windows también se puede indicar directamente el intérprete:

```powershell
py -3 main.py
```

El programa ejecuta más de veinte simulaciones válidas e inválidas de principio
a fin, muestra un resumen final de los objetos en memoria y registra los eventos
en `software_fj.log`.

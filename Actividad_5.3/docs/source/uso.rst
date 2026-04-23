Guia de Uso
===========

Requisitos
----------

* Python 3.10 o superior.
* Dependencia externa: ``requests``.

Instalacion
-----------

Desde la raiz del proyecto:

.. code-block:: bash

   pip install requests

Ejecucion
---------

.. code-block:: bash

   python main.py

La aplicacion abre una interfaz con:

* Panel NO OPTIMIZADO
* Panel OPTIMIZADO
* Graficos en vivo de tiempo y latitud

Interpretacion de resultados
----------------------------

* ``Tiempo``: duracion por ciclo de consulta y procesamiento.
* ``Promedio lat``: media de latitudes calculada por cada estrategia.
* ``Top Profiling``: resumen de funciones con mayor costo acumulado.
* Graficos:

  * Tiempo (ms): compara latencia entre estrategias.
  * Latitud promedio: muestra estabilidad/variacion del dato procesado.

Notas operativas
----------------

* La app actualiza cada 3 segundos.
* El profiling se ejecuta en ciclos alternos para mantener fluidez.
* Si falla la API, se usa el ultimo valor valido conocido como fallback.

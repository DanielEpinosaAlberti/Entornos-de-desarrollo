Arquitectura del Sistema
========================

Vision general
--------------

La aplicacion esta compuesta por cinco modulos principales:

* ``main.py``: interfaz grafica, actualizacion asincrona y graficos en vivo.
* ``api.py``: cliente HTTP para consultar la posicion de la ISS con tolerancia a fallos.
* ``no_opt.py``: flujo de procesamiento no optimizado.
* ``opt.py``: flujo de procesamiento optimizado.
* ``profiler_utils.py``: utilidades de profiling con ``cProfile``.

Flujo de datos
--------------

1. La interfaz de ``main.py`` programa actualizaciones periodicas.
2. Cada panel ejecuta su funcion de datos en segundo plano usando ``ThreadPoolExecutor``.
3. Se obtiene el resultado y se actualizan metricas, texto y graficos.
4. En ciclos alternos se aplica profiling para reducir sobrecarga en UI.

Decisiones de diseno
--------------------

* Se evita bloquear el hilo principal de Tkinter.
* Se usa ``after`` para el polling de resultados asincornos.
* La capa API incorpora timeout, reintentos y ultimo valor conocido para robustez.
* Los graficos se dibujan con ``Canvas`` para no depender de librerias externas.

Estructura del proyecto
-----------------------

::

   Actividad_5.3/
   |- api.py
   |- main.py
   |- no_opt.py
   |- opt.py
   |- profiler_utils.py
   `- docs/
      |- source/
      `- build/

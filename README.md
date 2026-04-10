# Terminal Baires - Simulacion de Operaciones Portuarias

Proyecto de simulacion de eventos discretos para analizar la operacion de un terminal portuario con buques, contenedores y gruas. El objetivo es comparar escenarios operativos y cuantificar su impacto en tiempos de espera, utilizacion de recursos y duracion total del sistema.

Este repositorio combina:

- Modelado estocastico con SimPy.
- Analisis de resultados en CSV.
- Dashboard interactivo en Streamlit.
- Notebook de exploracion y experimentacion.

## Que demuestra este proyecto

Si sos recruiter o lider tecnico, este trabajo muestra capacidad para:

- Modelar procesos reales con objetos y reglas de negocio.
- Implementar simulaciones orientadas a decisiones operativas.
- Definir escenarios comparativos (1 vs 2 gruas).
- Diseñar y calcular metricas de performance.
- Construir una interfaz de analisis para usuarios no tecnicos.
- Trabajar con Python, estadistica aplicada y visualizacion.

## Problema que se plantea

En una terminal portuaria, los buques llegan con carga/descarga variable y compiten por una cantidad limitada de gruas. La pregunta central es:

> Como cambia el desempeno del sistema al modificar capacidad operativa (cantidad de gruas), rendimiento y tasa de llegada de buques.

El modelo incorpora variabilidad en:

- Llegadas de buques (proceso estocastico).
- Cantidad y tipo de contenedores por buque.
- Tiempo de navegacion/amarre previo al servicio.
- Fallas de grua con tiempo adicional de reparacion.

## Modelado orientado a objetos

### Objeto `Contenedor`

- Atributos principales: tipo (`liviano`, `mediano`, `pesado`), estado de llenado y peso.
- Reglas: el peso depende de clase y si esta lleno o medio lleno.

### Objeto `Buque`

- Atributos principales: cantidad de contenedores a cargar/descargar, total de contenedores, peso total.
- Composicion: un buque contiene una coleccion de objetos `Contenedor`.

Este enfoque encapsula el dominio logistico y permite extender reglas (nuevos tipos, distribuciones o eventos).

## Motor de simulacion

Implementado con SimPy (eventos discretos):

1. Llega un buque.
2. Espera disponibilidad de grua.
3. Realiza navegacion/amarre.
4. Recibe servicio de carga/descarga.
5. Puede ocurrir rotura de grua (afecta duracion).
6. Finaliza operacion y libera recurso.

Se ejecutan 1000 ciclos por escenario para estabilizar estimaciones.

## Escenarios evaluados

- Escenario A: 1 grua.
- Escenario B: 2 gruas.

Parametros configurables:

- `rendimiento`: productividad de grua (contenedores/h o aproximacion equivalente).
- `tasa`: intensidad de llegadas (barcos por mes).
- `barcos`: cantidad de buques a atender por corrida.

## Metricas y resultados

Se registran resultados a nivel buque y a nivel corrida:

- `tiempo_espera`
- `tiempo_servicio`
- `tiempo_ocioso`
- `tiempo_total_operacion`
- `peso_total_operado`
- `reparacion` (evento binario)
- indicadores por ciclo para resumen estadistico

Ademas, se calcula resumen por ciclo con promedio e intervalo de confianza para comparar escenarios con criterio estadistico.

## Estructura del repositorio

```text
terminalBaires-main/
	app.py                     # Dashboard Streamlit para ejecutar/comparar simulaciones
	run_simulation.py          # Entrada CLI para correr simulacion por parametros
	terminalBaires.ipynb       # Notebook de desarrollo, analisis y pruebas
	requirements.txt           # Dependencias del proyecto
	guia_local.txt             # Guia rapida de entorno local
	data/                      # CSV de simulaciones ya generadas
	terminalbaires/
		generators.py            # Objetos de dominio + logica de eventos y metricas
		simulation.py            # Orquestacion de escenarios y exportacion a CSV
		main.py                  # Version de trabajo/experimental previa
```

## Stack tecnologico

- Python
- SimPy
- NumPy
- Pandas
- SciPy
- Matplotlib
- Streamlit

## Instalacion

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Ejecucion

### Opcion 1: dashboard interactivo

```bash
streamlit run app.py
```

Desde la UI se cargan parametros, se ejecuta simulacion y se comparan curvas por buque para ambos escenarios.

### Opcion 2: linea de comandos

```bash
python run_simulation.py -r 25 -t 30 -b 10
```

## Salidas del modelo

Cada corrida genera (por escenario):

- `*_log.csv`: detalle por buque y por ciclo.
- `*_sim.csv`: resumen por corrida (duracion total, recursos, etc.).

Los archivos en `data/` son ejemplos de resultados listos para analisis.

## Enfoque de analisis

El proyecto esta pensado para responder decisiones de capacidad, por ejemplo:

- Conviene invertir en una segunda grua?
- Cuanto baja la espera promedio?
- Como cambian los cuellos de botella con distintas tasas de llegada?

Es una base solida para evolucionar hacia optimizacion, simulacion de costos y analisis de sensibilidad.

## Posibles mejoras (roadmap)

- Corregir y endurecer el script CLI para produccion.
- Versionar escenarios y semillas para reproducibilidad total.
- Incluir tests unitarios y de regresion de metricas.
- Agregar KPIs economicos (costo de espera, costo de inactividad, SLA).
- Publicar dashboard en nube (Streamlit Community Cloud o similar).

## Autor

Proyecto desarrollado como trabajo de simulacion aplicada a operaciones logisticas y analitica de procesos.

Si queres, puedo ayudarte a adaptar este README a un perfil mas Data Science, mas Backend o mas Industrial Engineering segun el tipo de busqueda laboral.


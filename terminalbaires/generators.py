# terminalbaires/generators.py

# terminalbaires/generators.py
import simpy, random
import numpy as np
import streamlit as st
import pandas as pd
from collections import Counter
from scipy.stats import norm


class Contenedor:
    # Peso promedio de los contenedores según tipo
    clases_peso = {
        'liviano': random.randint(5, 10),  # peso promedio
        'mediano': random.randint(11, 16),
        'pesado': random.randint(17, 22),
    }

    def __init__(self, tipo):
        # Tipo de contenedor (liviano, mediano, pesado)
        self.tipo = tipo

        # Distribución binomial para decidir si el contenedor está lleno o medio lleno
        self.lleno = random.choices([True, False], weights=[0.7, 0.3])[0]  # 80% lleno, 20% medio lleno

        # Obtener peso base según tipo
        self.peso_base = self.clases_peso[self.tipo]  # Peso base dependiendo del tipo

        # Si está medio lleno, el peso es la mitad
        self.peso = self.peso_base if self.lleno else self.peso_base / 2



class Buque:
    def __init__(self, id_buque):
        self.id = id_buque

        # Generar aleatoriamente la cantidad de contenedores para carga y descarga
        self.descargar = random.randint(200, 1200)  # Descarga entre 200 y 1200 contenedores
        self.cargar = random.randint(100, 600)  # Carga entre 100 y 600 contenedores
        self.num_contenedores = self.cargar + self.descargar  # Total de contenedores

        # Crear contenedores con tipos aleatorios
        self.contenedores = [Contenedor(tipo=np.random.choice(['liviano', 'mediano', 'pesado'])) for _ in range(self.num_contenedores)]

        # Calcular el peso total del buque
        self.peso_total = sum([c.peso for c in self.contenedores])

    def resumen(self):
        return {
            "id": self.id,
            "num_contenedores": self.num_contenedores,
            "cargar": self.cargar,
            "descargar": self.descargar,
            "peso_total": self.peso_total
        }





def generador_buques(env, gruas, tasa_llegada_dias, rendimiento, barcos_servidos, BARCOS_A_SERVIR, fin_simulacion,simulacion,grua_ts,log,sim):
    for i in range(1, BARCOS_A_SERVIR + 1):
        buque = Buque(i)
        env.process(operar_buque(env, buque, gruas, rendimiento, barcos_servidos, BARCOS_A_SERVIR, fin_simulacion,simulacion,grua_ts,log,sim))
        tiempo_entre_llegadas = np.random.exponential(tasa_llegada_dias * 24)  # en horas

        yield env.timeout(tiempo_entre_llegadas)


# Lógica para calcular la probabilidad de rotura según el tipo de contenedor
def calcular_probabilidad_rotura(contenedor, x=0.1,y=0.15,z=0.20):
    if contenedor.tipo == "liviano":
        probabilidad_rotura = x
    elif contenedor.tipo == "liviano_medio_lleno":
        probabilidad_rotura = 0.75 * x
    elif contenedor.tipo == "mediano":
        probabilidad_rotura = y
    elif contenedor.tipo == "mediano_medio_lleno":
        probabilidad_rotura = 0.75 * y
    elif contenedor.tipo == "pesado":
        probabilidad_rotura = z
    elif contenedor.tipo == "pesado_medio_lleno":
        probabilidad_rotura = 0.75 * z
    else:
        probabilidad_rotura = 0  # Si no es ningún tipo definido, no hay probabilidad de rotura

    return probabilidad_rotura




def operar_buque(env, buque, gruas, rendimiento, barcos_servidos, BARCOS_A_SERVIR, fin_simulacion,simulacion,grua_ts,log,sim):
    llegada = env.now
    buque.tiempo_llegada = llegada  # guardar si querés usar luego
    print(f"{env.now:.2f} - Buque {buque.id} llegó a altamar y espera una grúa")
            # Calcular tiempo estimado en horas

    with gruas.request() as req:
        yield req
        assert gruas.count <= gruas.capacity, "No hay gruas disponibles"
        inicio_navegacion = env.now
        espera =  inicio_navegacion - llegada
        assert espera >= 0, "El tiempo de espera no puede ser negativo"
        print(f"{env.now:.2f} - Buque {buque.id} accede a grúa tras {espera:.2f} horas")

        ### Bloque navegacion ###

        # Simular tiempo de navegación de la grúa (en horas)
        tiempo_navegacion = np.random.uniform(15/60, 30/60) # el tiempo de navegacion es el tiempo entre inicio de navegacion hasta el amarre del barco
        tiempo_ocioso = max(0, env.now - grua_ts[0])# tiempo desde última operación hasta ahora
        assert grua_ts[0]>=0, "El tiempo no puede ser negativo"
        print(f"{env.now:.2f} - Buque {buque.id} navega por {tiempo_navegacion:.2f} horas de espera en pre mar")
        yield env.timeout(tiempo_navegacion)   #Pausa el tiempo del sistema... del buque.
        inicio_servicio =  env.now
        ##################################

        ## Bloque grua ##
        print(f"{env.now:.2f} - Buque {buque.id} comienza a ser atendido por una grúa... posee {buque.num_contenedores} contenedores")

        ## La duración en horas es la relación entre la cantidad de contendeores y el rendimiento hora. Se asume que tarda lo mismo por contenedor. Podemos diverisifcarlo en liviano, mediano y pesado
        duracion = buque.num_contenedores / rendimiento  #rendimiento_grua_tn_hora es la tasa de atención de la grua por hora.
        assert 200 <= buque.descargar <= 1200, "La cantidad de contenedores de descarga debe estar entre 200 y 1200"
        assert 100 <= buque.cargar <= 600, "La cantidad de contenedores de carga debe estar entre 100 y 600"
        assert buque.num_contenedores == buque.cargar + buque.descargar, "La cantidad de contenedores de carga y descarga no coinciden"

        peso_x_hora = (buque.peso_total)/duracion # Rendimiento de la grua por hora segun peso

        # Posible rotura
        probabilidad_rotura_total = 0
        contenedor_que_rompe = None  # Variable para almacenar el contenedor que causa la rotura

        for contenedor in buque.contenedores:
            probabilidad_rotura = calcular_probabilidad_rotura(contenedor)
            probabilidad_rotura_total += probabilidad_rotura

            # Si la rotura ocurre, almacenamos el contenedor que la causó
            if np.random.random() < probabilidad_rotura:
                contenedor_que_rompe = contenedor

        # Promediamos la probabilidad de rotura por el número de contenedores
        probabilidad_media = probabilidad_rotura_total / buque.num_contenedores

        if np.random.random() < probabilidad_media:
            print(f"{env.now:.2f} - ¡Grúa se rompe durante el servicio del buque {buque.id}!")

            # Determinar el tiempo de reparación según el tipo de contenedor que causó la rotura
            if contenedor_que_rompe.tipo == "liviano":
                duracion += np.random.uniform(1, 2)  # Entre 1 y 2 horas
            elif contenedor_que_rompe.tipo == "mediano":
                duracion += np.random.uniform(3, 5)  # Entre 3 y 5 horas
            elif contenedor_que_rompe.tipo == "pesado":
                duracion += np.random.uniform(6, 8)  # Entre 6 y 8 horas
            reparacion = 1
        else:
            reparacion = 0

        yield env.timeout(duracion)
        grua_ts[0] = env.now

        assert env.now >= llegada, "El tiempo actual no puede ser menor a la llegada"
        tiempo_total = round(env.now - llegada, 3)
        suma = round(espera + tiempo_navegacion + duracion,3)
        assert tiempo_total >= suma, "El tiempo total es menor a la suma de sus partes"

####### Se corre un contador de barcos servidos.. se van sirviendo barcos a medida que van llegando.

        barcos_servidos[0] += 1
        if barcos_servidos[0] >= BARCOS_A_SERVIR and not fin_simulacion.triggered:
          fin_simulacion.succeed()

        #print(grua_ts[0])
        print(f"{env.now:.2f} - Buque {buque.id} termina operación y libera grúa")

        # Actualiza el momento en que la grúa queda libre

        assert buque.num_contenedores > 0, "No puede haber buqes sin contenedores"
        assert buque.peso_total > 0, "El peso del buque debe ser positivo"

        conteo = Counter([c.tipo for c in buque.contenedores])  # Contamos las clases de cada contenedor
        proporciones = {k: round(v / buque.num_contenedores, 2) for k, v in conteo.items()}

        assert all(0 <= p <= 1 for p in proporciones.values()), "Las proporciones de contenedores deben estar entre 0 y 1"
        assert sum(proporciones.values()) <= 1.03, "La suma de proporciones supera 1" # le agregamos una toleracia a redondeo
        assert sum(conteo.values())==buque.num_contenedores, "Hay mas contenedores de lo previsto"

        # Contenedores medio llenos
        contenedores_medio_llenos = [c for c in buque.contenedores if not c.lleno]
        cant_medio_llenos = len(contenedores_medio_llenos)
        peso_total_medio_llenos = sum(c.peso for c in contenedores_medio_llenos)
        proporcion_medio_llenos = round(cant_medio_llenos / buque.num_contenedores, 2)
        peso_promedio_medio_llenos = round(peso_total_medio_llenos / cant_medio_llenos, 2) if cant_medio_llenos > 0 else 0

        # 7️⃣ Navegación de salida
        tiempo_salida = np.random.uniform(10/60, 30/60)

        log.append({
            "id": buque.id,
            'llegada(ts)':llegada,
            "hora_navegacion_inicio(ts)": inicio_navegacion,
            "tiempo_navegacion": tiempo_navegacion + tiempo_salida,
            "inicio_servicio(ts)": inicio_servicio,
            "fin_servicio(ts)": env.now,
            "tiempo_espera": espera,
            "tiempo_servicio": duracion,
            'tiempo_ocioso': tiempo_ocioso,
            'tiempo_total_operacion':env.now-llegada,
            "peso_total_operado": buque.peso_total,
            "peso_x_hora": round(peso_x_hora, 2),  # Está relativamente inflado
            "clases_contenedores": proporciones,
            "contenedores_carga": buque.cargar,
            "contenedores_descarga": buque.descargar,
            'contenedores_total': buque.num_contenedores,
            "proporcion_carga": round(buque.cargar / (buque.cargar + buque.descargar), 2) if (buque.cargar + buque.descargar) > 0 else 0,
            "medio_llenos": cant_medio_llenos,
            "peso_medio_llenos_total": peso_total_medio_llenos,
            "peso_x_hora_medio_lleno": peso_total_medio_llenos / rendimiento,
            "proporcion_medio_llenos": proporcion_medio_llenos,
            "reparacion": reparacion,
            'buque_espero_T_F': False if espera == 0 else True,
            'grua_ocioso_T_F': True if tiempo_ocioso != 0 else False,
            'ciclo': simulacion
        })


def calcular_promedio_por_ciclo(df, variable):
    """
    Calcula el promedio por ciclo y el promedio global para una variable dada.

    Parámetros:
        df (pd.DataFrame): DataFrame con los resultados de simulaciones.
        variable (str): Nombre de la columna a analizar.

    Retorna:
        promedio_global (float): Promedio global de la variable entre ciclos.
        std_global (float): Desvío estándar de la variable entre ciclos.
        promedios_por_ciclo (pd.Series): Promedio de la variable por ciclo.
    """
    if variable not in df.columns:
        raise ValueError(f"La variable '{variable}' no existe en el DataFrame.")

    # Asegurar que la columna sea numérica
    df[variable] = pd.to_numeric(df[variable], errors='coerce')

    # Agrupar por ciclo y calcular promedio por simulación
    promedios_por_ciclo = df.groupby("ciclo")[variable].mean()

    # Promedio y desvío global entre ciclos
    promedio_global = promedios_por_ciclo.mean()
    std_global = promedios_por_ciclo.std()
    # intervalo de confianza (normal, σ desconocida pero n ≥ 30 o normalidad asumida)
    z = norm.ppf(1 - (1 - 0.95) / 2)                  # 1.96 si conf=0.95
    margen_error = z * std_global / np.sqrt(1000)

    res = f"{promedio_global:.3f} ± {margen_error:.3f}"

    return promedio_global, std_global, res


def contar_eventos_binarios(df, columna):
    resumen = df.groupby("ciclo")[columna].sum()
    promedio = resumen.mean()
    desvio = resumen.std()
    return promedio, desvio, resumen

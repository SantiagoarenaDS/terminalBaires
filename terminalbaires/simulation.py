# terminalbaires/simulation.py
import simpy, pandas as pd
from pathlib import Path
from .generators import generador_buques

# simulation.py (ámbito de módulo)
sim = None
log = None

def SIMULAR(rendimiento,tasa_llegada_dias,BARCOS_A_SERVIR,out_dir):
    for i in [1,2]:
        N_GRUAS = i
        barcos_servidos = [0]  # usar lista para modificarlo dentro del proceso
        global sim, log 
        sim = []
        log = []

        for simulacion in range(1000):
            grua_ts = [0]
            barcos_servidos = [0]  # usar lista para modificarlo dentro del proceso
            env = simpy.Environment()
            fin_simulacion = env.event()


            gruas = simpy.Resource(env, capacity=N_GRUAS)

            env.process(generador_buques(env, gruas, tasa_llegada_dias, rendimiento, barcos_servidos, BARCOS_A_SERVIR, fin_simulacion,simulacion,grua_ts,log,sim))
            env.run(until=fin_simulacion)

            sim.append(
                {
                "duracion_sistema": env.now,
                "barcos_servidos": barcos_servidos,
                "tasa_llegada_dias": tasa_llegada_dias,
                "gruas":N_GRUAS,
                "rendimiento":rendimiento,
                "ciclo":simulacion
                }
                )

        sim = pd.DataFrame(sim)
        sim.to_csv(f"{N_GRUAS}_{rendimiento}_{tasa_llegada_dias}_{BARCOS_A_SERVIR}_sim.csv" , sep=";",decimal=",")

        log = pd.DataFrame(log)
        log.to_csv(f"{N_GRUAS}_{rendimiento}_{tasa_llegada_dias}_{BARCOS_A_SERVIR}_log.csv" , sep=";",decimal=",")
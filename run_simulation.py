#!/usr/bin/env python
import argparse
from terminalbaires.simulation import SIMULAR

parser = argparse.ArgumentParser("Simulación Terminal Baires")
parser.add_argument("-r", "--rendimiento", type=int, required=True,
                    help="Rendimiento promedio grúa (t/h)")
parser.add_argument("-t", "--tasa", type=float, required=True,
                    help="Barcos esperados por mes")
parser.add_argument("-b", "--barcos", type=int, required=True,
                    help="Barcos a servir")
args = parser.parse_args()

out_dir = SIMULAR(args.rendimiento, args.tasa, args.barcos,out_dir=data_path)

print(f"CSV generados en {out_dir.resolve()}")


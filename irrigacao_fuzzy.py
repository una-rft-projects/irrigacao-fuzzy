"""
Controlador fuzzy de irrigação (método de Mamdani)

Entradas: umidade do solo (%) e temperatura (°C)
Saída:    tempo de rega (min)

Uso:
    python irrigacao_fuzzy.py                         # roda os cenários de teste e gera os gráficos
    python irrigacao_fuzzy.py -u 35 -t 30             # calcula um caso específico
    python irrigacao_fuzzy.py -u 35 -t 30 --mostrar   # idem, e mostra a área do centroide
    python irrigacao_fuzzy.py --sem-graficos          # só os cenários de teste, sem gráficos
"""

import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

PASTA_GRAFICOS = Path(__file__).parent / "graficos"


def criar_variaveis():
    """Passos 3 e 4: variáveis linguísticas e funções de pertinência."""
    umidade = ctrl.Antecedent(np.arange(0, 101, 1), "umidade")         # % de umidade do solo
    temperatura = ctrl.Antecedent(np.arange(0, 46, 1), "temperatura")  # °C
    tempo = ctrl.Consequent(np.linspace(0, 30, 301), "tempo", defuzzify_method="centroid")  # min

    umidade["seca"] = fuzz.trapmf(umidade.universe, [0, 0, 25, 40])
    umidade["umida"] = fuzz.trimf(umidade.universe, [30, 50, 70])
    umidade["encharcada"] = fuzz.trapmf(umidade.universe, [60, 75, 100, 100])

    temperatura["baixa"] = fuzz.trapmf(temperatura.universe, [0, 0, 15, 22])
    temperatura["media"] = fuzz.trimf(temperatura.universe, [15, 25, 35])
    temperatura["alta"] = fuzz.trapmf(temperatura.universe, [28, 35, 45, 45])

    tempo["nenhum"] = fuzz.trapmf(tempo.universe, [0, 0, 2, 6])
    tempo["curto"] = fuzz.trimf(tempo.universe, [3, 8, 13])
    tempo["medio"] = fuzz.trimf(tempo.universe, [10, 15, 20])
    tempo["longo"] = fuzz.trimf(tempo.universe, [17, 22, 27])
    tempo["muito_longo"] = fuzz.trapmf(tempo.universe, [24, 28, 30, 30])

    return umidade, temperatura, tempo


def criar_regras(umidade, temperatura, tempo):
    """Passo 6: a matriz de regras 3 x 3 (a linha 'encharcada' vira uma regra só)."""
    return [
        # Solo seco: precisa de água; quanto mais calor, mais tempo
        ctrl.Rule(umidade["seca"] & temperatura["baixa"], tempo["medio"]),
        ctrl.Rule(umidade["seca"] & temperatura["media"], tempo["longo"]),
        ctrl.Rule(umidade["seca"] & temperatura["alta"], tempo["muito_longo"]),
        # Solo úmido: só rega se estiver quente
        ctrl.Rule(umidade["umida"] & temperatura["baixa"], tempo["nenhum"]),
        ctrl.Rule(umidade["umida"] & temperatura["media"], tempo["curto"]),
        ctrl.Rule(umidade["umida"] & temperatura["alta"], tempo["medio"]),
        # Solo encharcado: nunca regar
        ctrl.Rule(umidade["encharcada"], tempo["nenhum"]),
    ]


class ControladorIrrigacao:
    """Passo 7: junta variáveis e regras em um sistema pronto para simular."""

    def __init__(self):
        self.umidade, self.temperatura, self.tempo = criar_variaveis()
        regras = criar_regras(self.umidade, self.temperatura, self.tempo)
        self.sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))

    def tempo_de_rega(self, umidade, temperatura):
        """Recebe umidade (%) e temperatura (°C) e devolve o tempo de rega em minutos."""
        umidade = float(np.clip(umidade, 0, 100))
        temperatura = float(np.clip(temperatura, 0, 45))
        self.sim.input["umidade"] = umidade
        self.sim.input["temperatura"] = temperatura
        self.sim.compute()
        return self.sim.output["tempo"]


def rodar_cenarios(controlador):
    """Passo 8: alguns cenários para conferir se as respostas fazem sentido."""
    cenarios = [
        (10, 35, "seco e quente"),
        (35, 30, "exemplo da aula"),
        (20, 10, "seco, mas frio"),
        (50, 25, "úmido e ameno"),
        (55, 38, "úmido, mas muito quente"),
        (85, 40, "encharcado"),
    ]
    print()
    print(" Umidade | Temp.  |   Rega    | Situação")
    print("---------+--------+-----------+------------------------")
    for u, t, desc in cenarios:
        minutos = controlador.tempo_de_rega(u, t)
        print(f"  {u:>4}%  | {t:>3} °C | {minutos:5.1f} min | {desc}")
    print()


def salvar_funcoes(controlador):
    """Passo 5: gráficos das funções de pertinência."""
    for var in (controlador.umidade, controlador.temperatura, controlador.tempo):
        var.view()
        plt.savefig(PASTA_GRAFICOS / f"funcoes_{var.label}.png", dpi=120, bbox_inches="tight")


def salvar_superficie(controlador):
    """Passo 9: superfície de controle 3D."""
    U, T = np.meshgrid(np.arange(0, 101, 5), np.arange(0, 46, 2.5))
    Z = np.vectorize(controlador.tempo_de_rega)(U, T)

    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(U, T, Z, cmap="viridis", edgecolor="none")
    ax.set_xlabel("Umidade do solo (%)")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_zlabel("Tempo de rega (min)")
    ax.set_title("Superfície de controle: irrigação fuzzy")
    fig.savefig(PASTA_GRAFICOS / "superficie_controle.png", dpi=120, bbox_inches="tight")


def main():
    parser = argparse.ArgumentParser(description="Controlador fuzzy de irrigação")
    parser.add_argument("-u", "--umidade", type=float, help="umidade do solo em % (0 a 100)")
    parser.add_argument("-t", "--temperatura", type=float, help="temperatura em °C (0 a 45)")
    parser.add_argument("--sem-graficos", action="store_true", help="não gera nem mostra gráficos")
    parser.add_argument("--mostrar", action="store_true", help="abre as janelas dos gráficos ao final")
    args = parser.parse_args()

    controlador = ControladorIrrigacao()

    # Caso específico informado na linha de comando
    if args.umidade is not None or args.temperatura is not None:
        if args.umidade is None or args.temperatura is None:
            parser.error("informe as duas entradas: -u UMIDADE -t TEMPERATURA")
        minutos = controlador.tempo_de_rega(args.umidade, args.temperatura)
        print(f"Umidade {args.umidade:g}% e temperatura {args.temperatura:g} °C "
              f"-> tempo de rega: {minutos:.1f} min")
        if args.mostrar and not args.sem_graficos:
            controlador.tempo.view(sim=controlador.sim)
            plt.show()
        return

    # Sem argumentos: cenários de teste + gráficos
    rodar_cenarios(controlador)
    if args.sem_graficos:
        return

    PASTA_GRAFICOS.mkdir(exist_ok=True)
    salvar_funcoes(controlador)
    salvar_superficie(controlador)
    print(f"Gráficos salvos em: {PASTA_GRAFICOS}")

    if args.mostrar:
        plt.show()
    else:
        plt.close("all")


if __name__ == "__main__":
    main()

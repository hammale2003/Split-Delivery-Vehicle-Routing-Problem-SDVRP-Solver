"""
Split Delivery Vehicle Routing Problem (SDVRP)
Team Members:
    - HAMMALE MOURAD
    - DOHA CHBIHI
    - AYA BOUKHARI
    - MOHAMED BENKIRANE
    - HABBANI MOHAMMED
Institution: CENTRALE CASABLANCA
Year: 2024-2025
"""
import math
import gurobipy as gp
from gurobipy import GRB

def solve_sdvrp_with_gurobi(input_file, output_file, time_limit=None):
    # Lire les données à partir du fichier d'entrée
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Extraction des paramètres
    n_clients, vehicle_capacity = map(int, lines[0].strip().split())
    demands = list(map(int, lines[1].strip().split()))
    coords = [tuple(map(int, line.strip().split())) for line in lines[2:]]

    # Calcul de M (borne supérieure du nombre de véhicules nécessaires)
    M = sum(demands) // vehicle_capacity + min(len(demands), sum(demands) % vehicle_capacity + 1)

    # Calcul des distances euclidiennes arrondies selon la formule donnée
    def calculate_distance(p1, p2):
        return math.floor(math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2) + 0.5)

    # Création de la matrice des distances
    n_nodes = n_clients + 1  # nombre total de nœuds (clients + dépôt)
    distances = {}
    for i in range(n_nodes):
        for j in range(n_nodes):
            distances[i, j] = calculate_distance(coords[i], coords[j])

    # Création du modèle Gurobi
    model = gp.Model("SD-VRP")

    # Appliquer la limite de temps si spécifiée
    if time_limit is not None:
        model.setParam(GRB.Param.TimeLimit, time_limit)

    # Variables de décision
    x = model.addVars(n_nodes, n_nodes, M, vtype=GRB.BINARY, name="x")
    y = model.addVars(range(1, n_nodes), range(M), vtype=GRB.CONTINUOUS, name="y")

    # Fonction objectif: minimiser la distance totale parcourue
    model.setObjective(gp.quicksum(distances[i, j] * x[i, j, k] for i in range(n_nodes) for j in range(n_nodes) for k in range(M)), GRB.MINIMIZE)

    # Contraintes
    # Satisfaction des demandes
    for i in range(1, n_nodes):
        model.addConstr(gp.quicksum(y[i, k] for k in range(M)) == demands[i - 1], f"Demand_{i}")

    # Capacité des véhicules
    for k in range(M):
        model.addConstr(gp.quicksum(y[i, k] for i in range(1, n_nodes)) <= vehicle_capacity, f"Capacity_{k}")

    # Contraintes de flux
    for k in range(M):
        model.addConstr(gp.quicksum(x[0, j, k] for j in range(1, n_nodes)) <= 1, f"DepotOut_{k}")

        for i in range(n_nodes):
            model.addConstr(gp.quicksum(x[i, j, k] for j in range(n_nodes)) == gp.quicksum(x[j, i, k] for j in range(n_nodes)), f"Flow_{i}_{k}")

    # Pas de self-loops
    for i in range(n_nodes):
        for k in range(M):
            model.addConstr(x[i, i, k] == 0, f"NoSelfLoop_{i}_{k}")

    # Liaison entre les variables x et y
    for i in range(1, n_nodes):
        for k in range(M):
            model.addConstr(gp.quicksum(x[j, i, k] for j in range(n_nodes)) * vehicle_capacity >= y[i, k], f"Link_{i}_{k}")

    # Élimination des sous-tours
    u = model.addVars(n_nodes, M, vtype=GRB.CONTINUOUS, name="u")
    for i in range(1, n_nodes):
        for j in range(1, n_nodes):
            if i != j:
                for k in range(M):
                    model.addConstr(u[i, k] - u[j, k] + n_nodes * x[i, j, k] <= n_nodes - 1, f"Subtour_{i}_{j}_{k}")

    # Force l'utilisation séquentielle des véhicules
    for k in range(1, M):
        model.addConstr(gp.quicksum(x[0, j, k - 1] for j in range(1, n_nodes)) >= gp.quicksum(x[0, j, k] for j in range(1, n_nodes)), f"Sequential_{k}")

    # Résolution du modèle
    model.optimize()

    # Extraction des résultats
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        routes = []
        total_cost = model.objVal
        truck_loads = [0] * M
        num_deliveries = 0

        for k in range(M):
            route = []
            current = 0
            route_exists = False
            while True:
                next_node = None
                for j in range(n_nodes):
                    if x[current, j, k].x > 0.99:
                        next_node = j
                        route_exists = True
                        break

                if next_node is None or next_node == 0:
                    if route and route_exists:
                        formatted_deliveries = []
                        for node in route:
                            quantity = y[node, k].x
                            if quantity > 0:
                                num_deliveries += 1
                                truck_loads[k] += quantity
                                formatted_deliveries.append(f"{node} ({int(quantity)})")
                        routes.append(f"Route {k + 1}: 0 - " + " - ".join(formatted_deliveries) + " - 0")
                    break

                route.append(next_node)
                current = next_node

        # Écriture du fichier de sortie
        with open(output_file, 'w', encoding='utf-8') as f:
            for route in routes:
                f.write(route + '\n')
            f.write(f"Total cost: {int(total_cost)}\n")
            f.write(f"Number of deliveries: {num_deliveries}\n")
            f.write(f"Trucks loads: {' '.join(str(int(load)) for load in truck_loads if load > 0)}\n")

    else:
        print("No optimal solution found or time limit exceeded.")
    return None




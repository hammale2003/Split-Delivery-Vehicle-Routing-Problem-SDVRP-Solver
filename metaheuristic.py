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
import random
from collections import deque
from typing import List, Tuple

class SDVRP_Solution:
    def __init__(self, routes, cost, deliveries, truck_loads):
        self.routes = routes
        self.cost = cost
        self.num_deliveries = deliveries
        self.truck_loads = truck_loads

def solve_sdvrp_with_metaheuristic(input_file, output_file, max_iterations=100, time_limit=300):
    # Lire les données du fichier d'entrée
    n, Q, demands, coordinates = read_input(input_file)
    
    # Exécuter la recherche tabou
    best_solution, best_cost = tabu_search(n, Q, demands, coordinates, max_iterations)
    
    # Convertir la solution au format requis
    formatted_solution = []
    truck_loads = []
    num_deliveries = 0
    
    for route, load in best_solution:
        formatted_route = []
        for i in range(1, len(route)-1):  # Ignorer le dépôt (0) au début et à la fin
            client = route[i]
            qty = demands[client-1]  # Utiliser la demande complète du client
            formatted_route.append((client, qty))
            num_deliveries += 1
        formatted_solution.append(formatted_route)
        truck_loads.append(load)
    
    # Écrire la solution dans le fichier de sortie
    with open(output_file, "w") as f:
        f.write(f"Total cost: {best_cost:.2f}\n")
        for i, route in enumerate(formatted_solution, 1):
            route_str = "0"  # Début au dépôt
            for client, qty in route:
                route_str += f" - {client} ({qty})"
            route_str += " - 0"  # Retour au dépôt
            f.write(f"Route {i}: {route_str}\n")
        f.write(f"Number of deliveries: {num_deliveries}\n")
        f.write(f"Trucks loads: {' '.join(map(str, truck_loads))}\n")

    return SDVRP_Solution(formatted_solution, best_cost, num_deliveries, truck_loads)

def read_input(file_path):
    """Lire le fichier d'entrée"""
    with open(file_path, "r") as file:
        n, Q = map(int, file.readline().split())
        demands = list(map(int, file.readline().split()))
        coordinates = [tuple(map(int, line.split())) for line in file if line.strip()]

        if len(demands) != n or len(coordinates) != n + 1:
            raise ValueError("Invalid input file format.")

    return n, Q, demands, coordinates

def euclidean_distance(coord1, coord2):
    """Calculer la distance euclidienne"""
    return int(math.sqrt((coord2[0] - coord1[0])**2 + (coord2[1] - coord1[1])**2) + 0.5)

def compute_distance_matrix(coordinates):
    """Générer la matrice des distances"""
    n = len(coordinates)
    return [[euclidean_distance(coordinates[i], coordinates[j]) for j in range(n)] for i in range(n)]

def generate_initial_solution(n, Q, demands):
    """Générer une solution initiale gloutonne"""
    routes = []
    clients = deque(range(1, n + 1))
    while clients:
        current_route = [0]  # Commencer par le dépôt
        current_load = 0

        for _ in range(len(clients)):
            client = clients.popleft()
            if current_load + demands[client - 1] <= Q:
                current_route.append(client)
                current_load += demands[client - 1]
            else:
                clients.append(client)

        current_route.append(0)  # Retourner au dépôt
        if len(current_route) > 2:  # Ajouter la route seulement si elle contient des clients
            routes.append((current_route, current_load))

    return routes

def compute_total_cost(routes, distance_matrix):
    """Calculer le coût total d'une solution"""
    total_cost = 0
    for route, _ in routes:
        for i in range(len(route) - 1):
            total_cost += distance_matrix[route[i]][route[i + 1]]
    return total_cost

def generate_neighbors(current_solution, Q, demands, distance_matrix):
    """Générer des solutions voisines"""
    neighbors = []

    for route_idx, (route, load) in enumerate(current_solution):
        if len(route) <= 3:  # Ignorer les routes avec un seul client
            continue

        for i in range(1, len(route) - 1):
            for j, (other_route, other_load) in enumerate(current_solution):
                if route_idx == j or route[i] in other_route:
                    continue

                client = route[i]
                if other_load + demands[client - 1] <= Q:
                    new_solution = [list(r) for r, _ in current_solution]
                    new_loads = [l for _, l in current_solution]

                    new_solution[route_idx].remove(client)
                    new_loads[route_idx] -= demands[client - 1]

                    new_solution[j].insert(-1, client)
                    new_loads[j] += demands[client - 1]

                    neighbors.append(list(zip(new_solution, new_loads)))

    return neighbors

def tabu_search(n, Q, demands, coordinates, max_iterations=100, tabu_size=10):
    """Recherche Tabou pour le SDVRP"""
    distance_matrix = compute_distance_matrix(coordinates)
    current_solution = generate_initial_solution(n, Q, demands)
    best_solution = current_solution[:]
    best_cost = compute_total_cost(best_solution, distance_matrix)

    tabu_list = []
    for _ in range(max_iterations):
        neighbors = generate_neighbors(current_solution, Q, demands, distance_matrix)

        if not neighbors:
            continue

        best_neighbor = None
        best_neighbor_cost = float("inf")
        for neighbor in neighbors:
            neighbor_cost = compute_total_cost(neighbor, distance_matrix)
            if neighbor not in tabu_list and neighbor_cost < best_neighbor_cost:
                best_neighbor = neighbor
                best_neighbor_cost = neighbor_cost

        if best_neighbor:
            current_solution = best_neighbor
            tabu_list.append(current_solution)
            if len(tabu_list) > tabu_size:
                tabu_list.pop(0)

        if best_neighbor_cost < best_cost:
            best_solution = best_neighbor
            best_cost = best_neighbor_cost

    return best_solution, best_cost

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else f"solution_{input_file}"
        max_iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        time_limit = int(sys.argv[4]) if len(sys.argv) > 4 else 300
        solve_sdvrp_with_metaheuristic(input_file, output_file, max_iterations, time_limit)
    else:
        print("Usage: python metaheuristic.py <input_file> [output_file] [max_iterations] [time_limit]")
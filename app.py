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
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math
import os
from datetime import datetime
import time
import importlib
from metaheuristic import solve_sdvrp_with_metaheuristic
from solve import solve_sdvrp_with_gurobi as solve_sdvrp_with_gurobi_base
from sdvrp_solver import solve_sdvrp_with_gurobi as solve_sdvrp_with_gurobi_advanced


class SDVRP_Solution:
    def __init__(self, routes, cost, deliveries, truck_loads):
        self.routes = routes
        self.cost = cost
        self.num_deliveries = deliveries
        self.truck_loads = truck_loads

def parse_solution_file(solution_file):
    """Parse le fichier de solution généré"""
    try:
        with open(solution_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return None
            
        # Parser le coût total
        cost_line = next(line for line in lines if line.startswith('Total cost'))
        cost = float(cost_line.split(': ')[1])
        
        # Parser les routes
        routes = []
        for line in lines:
            if line.startswith('Route'):
                route_parts = line.split(': ')[1].strip().split(' - ')
                route = []
                for i in range(1, len(route_parts)-1):  # Ignorer le premier et dernier 0
                    part = route_parts[i]
                    if '(' in part:
                        client, qty = part.split('(')
                        client = int(client.strip())
                        qty = int(qty.strip(')').strip())
                        route.append((client, qty))
                if route:  # N'ajouter que les routes non vides
                    routes.append(route)
        
        # Parser le nombre de livraisons
        deliveries_line = next(line for line in lines if line.startswith('Number of deliveries'))
        num_deliveries = int(deliveries_line.split(': ')[1])
        
        # Parser les charges des camions
        loads_line = next(line for line in lines if line.startswith('Trucks loads'))
        truck_loads = [int(load) for load in loads_line.split(': ')[1].split()]
        
        return SDVRP_Solution(routes, cost, num_deliveries, truck_loads)
        
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier de solution: {str(e)}")
        return None

def create_solution_visualization(solver, solution):
    fig = go.Figure()
    
    # Ajout du dépôt
    fig.add_trace(go.Scatter(
        x=[solver.depot[0]],
        y=[solver.depot[1]],
        mode='markers+text',
        marker=dict(size=20, symbol='star', color='gold', line=dict(color='black', width=2)),
        text=['Dépôt'],
        textposition='bottom center',
        name='Dépôt'
    ))
    
    # Ajout des clients
    for i, coords in enumerate(solver.clients):
        fig.add_trace(go.Scatter(
            x=[coords[0]],
            y=[coords[1]],
            mode='markers+text',
            marker=dict(size=10),
            text=[f'Client {i+1}\nDemande: {solver.demands[i]}'],
            textposition='top center',
            name=f'Client {i+1}'
        ))
    
    # Tracé des routes
    colors = px.colors.qualitative.Set3
    for i, route in enumerate(solution.routes):
        if not route:
            continue
            
        route_coords = [(solver.depot[0], solver.depot[1])]  # Début au dépôt
        for client, qty in route:
            client_coords = solver.clients[client-1]
            route_coords.append((client_coords[0], client_coords[1]))
        route_coords.append((solver.depot[0], solver.depot[1]))  # Retour au dépôt
        
        x_coords = [coord[0] for coord in route_coords]
        y_coords = [coord[1] for coord in route_coords]
        
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines+markers',
            line=dict(color=colors[i % len(colors)], width=2),
            name=f'Route {i+1} (Charge: {sum(qty for _, qty in route)})'
        ))
    
    fig.update_layout(
        title='Visualisation des routes',
        showlegend=True,
        hovermode='closest'
    )
    
    return fig

def parse_case_file(file_path):
    """Parse le fichier d'entrée et valide les données"""
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Première ligne
        parts = lines[0].split()
        num_clients, vehicle_capacity = map(int, parts[:2])
        
        # Validation basique
        if num_clients <= 0 or vehicle_capacity <= 0:
            raise ValueError("Nombre de clients ou capacité invalide")
        
        # Deuxième ligne: demandes
        demands = list(map(int, lines[1].split()))
        if len(demands) != num_clients:
            st.error(f"Nombre de demandes ({len(demands)}) ne correspond pas au nombre de clients ({num_clients})")
            raise ValueError("Mismatch in number of demands")

        # Coordonnées
        coordinates = []
        for line in lines[2:num_clients+3]:
            try:
                x, y = map(float, line.split())
                coordinates.append((x, y))
            except Exception as e:
                st.error(f"Erreur lors de la lecture des coordonnées: {str(e)}")
                raise

        return {
            "num_clients": num_clients,
            "vehicle_capacity": vehicle_capacity,
            "demands": demands,
            "coordinates": coordinates
        }
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        raise

def display_solution_details(solver, solution, solve_time):
    """Affiche les détails de la solution dans l'interface"""
    tab1, tab2, tab3 = st.tabs(["Résumé", "Détails des Routes", "Visualisation"])
    
    with tab1:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Coût Total", f"{solution.cost:.2f}")
        with col2:
            st.metric("Nombre de Routes", len(solution.routes))
        with col3:
            st.metric("Livraisons Totales", solution.num_deliveries)
        with col4:
            st.metric("Temps de Résolution", f"{solve_time:.2f}s")
    
    with tab2:
        for i, route in enumerate(solution.routes):
            with st.expander(f"Route {i+1} - Charge: {solution.truck_loads[i]}"):
                route_data = []
                prev_node = 0  # dépôt
                total_distance = 0
                
                for client, qty in route:
                    distance = solver.distances[prev_node][client]
                    total_distance += distance
                    route_data.append({
                        'Client': client,
                        'Quantité': qty,
                        'Distance depuis précédent': f"{distance:.2f}"
                    })
                    prev_node = client
                
                # Ajouter la distance de retour au dépôt
                total_distance += solver.distances[prev_node][0]
                
                if route_data:
                    route_df = pd.DataFrame(route_data)
                    st.dataframe(route_df)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Distance Totale", f"{total_distance:.2f}")
                    col2.metric("Charge Totale", solution.truck_loads[i])
                    col3.metric("Utilisation Capacité", 
                            f"{(solution.truck_loads[i]/solver.vehicle_capacity)*100:.1f}%")
    
    with tab3:
        try:
            fig = create_solution_visualization(solver, solution)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur lors de la visualisation: {str(e)}")

class DummyExactSolver:
    """Classe minimale pour supporter la visualisation des résultats"""
    def __init__(self, num_clients, vehicle_capacity, demands, coordinates):
        self.num_clients = num_clients
        self.vehicle_capacity = vehicle_capacity
        self.demands = demands
        self.coordinates = coordinates
        self.depot = coordinates[0]
        self.clients = coordinates[1:]
        self.distances = self._calculate_distances()
    
    def _calculate_distances(self):
        n = len(self.coordinates)
        distances = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    distances[i][j] = math.floor(
                        math.sqrt((self.coordinates[j][0] - self.coordinates[i][0])**2 +
                                  (self.coordinates[j][1] - self.coordinates[i][1])**2) + 0.5)
        return distances
def show_about():
    st.sidebar.markdown("---")
    st.sidebar.header("À propos")
    st.sidebar.markdown("""
    ### Équipe
    - HAMMALE MOURAD
    - DOHA CHBIHI
    - AYA BOUKHARI
    - MOHAMED BENKIRANE
    - HABBANI MOHAMMED
    
    ### Institution
    ECOLE CENTRALE CASABLANCA
    """)

def main():
    st.set_page_config(
        layout="wide",
        page_title="SDVRP Solver - ECC",
        page_icon="🚚"
    )
    
    # En-tête personnalisé
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Split Delivery Vehicle Routing Problem Solver")
        st.markdown("*Développé par l'équipe ECC*")
    
    # Configuration dans la barre latérale
    st.sidebar.title("Configuration")
    
    # Sélection de la méthode de résolution
    solver_method = st.sidebar.radio(
        "Méthode de résolution",
        ["Métaheuristique", "Solveur Exact (Gurobi)"]
    )
    
    # Sélection du fichier
    case_files = [f for f in os.listdir('.') if f.startswith('Case') and f.endswith('.txt')]
    selected_file = st.sidebar.selectbox('Sélectionner un cas:', case_files)
    
    # Paramètres communs
    st.sidebar.subheader("Paramètres communs")
    max_time = st.sidebar.slider('Temps maximum (secondes):', 60, 600, 300)
    
    # Paramètres spécifiques à la métaheuristique
    if solver_method == "Métaheuristique":
        st.sidebar.subheader("Paramètres Métaheuristique")
        max_iterations = st.sidebar.slider('Nombre maximum d\'itérations:', 100, 1000, 200)
    
    if selected_file:
        try:
            # Chargement et parsing des données
            case_data = parse_case_file(selected_file)
            
            # Affichage des détails de l'instance
            with st.expander("Détails de l'Instance", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nombre de Clients", case_data['num_clients'])
                with col2:
                    st.metric("Capacité des Véhicules", case_data['vehicle_capacity'])
                with col3:
                    st.metric("Demande Totale", sum(case_data['demands']))
            
            # Bouton de résolution
            if st.button('Résoudre', type='primary'):
                with st.spinner('Résolution en cours...'):
                    start_time = time.time()
                    
                    try:
                        output_file = f"solution_{selected_file}"
                        
                        if solver_method == "Métaheuristique":
                            solve_sdvrp_with_metaheuristic(selected_file, output_file, 
                                                         max_iterations=max_iterations,
                                                         time_limit=max_time)
                        else:
                            # Extraire le numéro du cas
                            case_number = int(''.join(filter(str.isdigit, selected_file)))
                            
                            # Choisir le solveur approprié
                            if case_number <= 6:
                                solve_sdvrp_with_gurobi_base(selected_file, output_file, time_limit=max_time)
                            else:
                                solve_sdvrp_with_gurobi_advanced(selected_file, output_file, time_limit=max_time)
                        
                        # Lire la solution
                        solution = parse_solution_file(output_file)
                        if solution:
                            solver_instance = DummyExactSolver(
                                case_data['num_clients'],
                                case_data['vehicle_capacity'],
                                case_data['demands'],
                                case_data['coordinates']
                            )
                            
                            solve_time = time.time() - start_time
                            
                            # Afficher les résultats
                            display_solution_details(solver_instance, solution, solve_time)
                            
                            # Bouton de téléchargement
                            with open(output_file, 'r') as f:
                                solution_content = f.read()
                                
                            st.download_button(
                                label="📥 Télécharger la Solution",
                                data=solution_content,
                                file_name=f"solution_{selected_file}",
                                mime="text/plain"
                            )
                            
                            with st.expander("Voir la solution brute"):
                                st.code(solution_content)
                        else:
                            st.error("Échec de la génération de la solution")
                            
                    except Exception as e:
                        if "size-limited license" in str(e):
                            st.error("Erreur de licence Gurobi: Le modèle est trop grand pour la licence d'évaluation.")
                        else:
                            st.error(f"Erreur lors de la résolution: {str(e)}")

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier: {str(e)}")

if __name__ == "__main__":
    main()
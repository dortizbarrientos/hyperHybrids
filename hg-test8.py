# SCRIPT 8: Plotting the 2-Section Graph of the Hypergraph

import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# --- Input Filenames ---
HYPERGRAPH_STRUCTURE_FILE = 'hypergraph_structure.json' # From Script 3
INDIVIDUALS_FILE = 'simulated_individuals.csv'      # From Script 1
CLUSTER_ASSIGNMENTS_FILE = 'hypergraph_cluster_assignments.csv' # From Script 4

# --- Output Plot Filenames ---
TWASECTION_PLOT_TRUE_GROUPS_FILE = '2section_plot_true_groups.png'
TWASECTION_PLOT_FOUND_CLUSTERS_FILE = '2section_plot_found_clusters.png'

# --- Load Data ---
print("SCRIPT 8: Plotting 2-Section Graph...")
try:
    with open(HYPERGRAPH_STRUCTURE_FILE, 'r') as f:
        data = json.load(f)
    hyperedges = data.get('hyperedges', [])
    nodes = data.get('nodes', []) # List of all node IDs

    individuals_df = pd.read_csv(INDIVIDUALS_FILE)
    cluster_assignments_df = pd.read_csv(CLUSTER_ASSIGNMENTS_FILE)
    print("Data loaded successfully.")

except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure necessary CSV files are in the correct location.")
    exit()
except Exception as e:
    print(f"An error occurred while loading data: {e}")
    exit()

if not hyperedges:
    print("No hyperedges found in structure file. Cannot build 2-section graph.")
    exit()

# --- Create the 2-Section Graph using NetworkX ---
G_2section = nx.Graph()
G_2section.add_nodes_from(nodes) # Add all nodes from the hypergraph

# Add edges: two nodes are connected if they appear in the same hyperedge
for he in hyperedges:
    he_nodes = list(map(int, he)) # Ensure integer IDs
    for i in range(len(he_nodes)):
        for j in range(i + 1, len(he_nodes)):
            G_2section.add_edge(he_nodes[i], he_nodes[j])

print(f"2-Section graph created with {G_2section.number_of_nodes()} nodes and {G_2section.number_of_edges()} edges.")

# --- Merge node attributes for coloring ---
node_attributes = pd.merge(individuals_df[['individual_id', 'true_group']],
                           cluster_assignments_df[['individual_id', 'cluster_id']],
                           on='individual_id', how='left')

# Prepare color maps
true_group_to_color = {}
if 'true_group' in node_attributes.columns:
    unique_true_groups = sorted(node_attributes['true_group'].dropna().unique())
    if unique_true_groups:
        palette_true = cm.get_cmap('Paired', len(unique_true_groups)) if len(unique_true_groups) <=10 else cm.get_cmap('tab20', len(unique_true_groups))
        true_group_to_color = {group: palette_true(i) for i, group in enumerate(unique_true_groups)}

cluster_id_to_color = {}
if 'cluster_id' in node_attributes.columns:
    unique_clusters = sorted(node_attributes['cluster_id'].dropna().unique())
    if unique_clusters:
        palette_cluster = cm.get_cmap('Set1', len(unique_clusters)) if len(unique_clusters) <=9 else cm.get_cmap('tab20', len(unique_clusters))
        cluster_id_to_color = {cid: palette_cluster(i) for i, cid in enumerate(unique_clusters)}

# --- Plotting Function for 2-Section Graph ---
def plot_2section_graph(graph, node_coloring_attribute, color_map, title, filename, pos=None):
    plt.figure(figsize=(14, 11))
    
    node_colors = []
    if node_coloring_attribute in node_attributes.columns:
        # Create a mapping from node ID to the attribute for coloring
        attr_map = pd.Series(node_attributes[node_coloring_attribute].values, index=node_attributes.individual_id).to_dict()
        # Get colors in the order of graph.nodes()
        for node in graph.nodes():
            attr_val = attr_map.get(node)
            node_colors.append(color_map.get(attr_val, 'grey')) # Default to grey if not found
    else:
        node_colors = 'skyblue' # Default single color

    if pos is None:
        print(f"Calculating spring layout for: {title}...")
        pos = nx.spring_layout(graph, k=0.2, iterations=50, seed=42) # k can be adjusted
    
    nx.draw_networkx_edges(graph, pos, alpha=0.2, width=0.5)
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=100, edgecolors='black', linewidths=0.5)
    # nx.draw_networkx_labels(graph, pos, font_size=6, alpha=0.8) # Labels can make it cluttered

    plt.title(title, fontsize=16)
    
    if color_map: # Create legend
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', label=str(group),
                                      markerfacecolor=color, markersize=10)
                          for group, color in color_map.items()]
        plt.legend(handles=legend_handles, title=node_coloring_attribute.replace('_',' ').title(),
                   bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
        plt.subplots_adjust(right=0.85)
        
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight')
    print(f"Saved 2-section graph plot to {filename}")
    # plt.show()

# --- Generate and Save Plots ---
# Calculate a common position layout once if you want plots to be comparable
print("Calculating initial layout for 2-section graph (may take a moment)...")
common_pos = nx.spring_layout(G_2section, k=0.2, iterations=50, seed=42)

# Plot 1: 2-Section graph colored by True Group
if true_group_to_color:
    plot_2section_graph(G_2section, 'true_group', true_group_to_color,
                        "2-Section Graph (Nodes colored by True Group)",
                        TWASECTION_PLOT_TRUE_GROUPS_FILE, pos=common_pos)
else:
    print("Skipping plot by true_group due to missing color map.")

# Plot 2: 2-Section graph colored by Found Hypergraph Cluster ID
if cluster_id_to_color:
    plot_2section_graph(G_2section, 'cluster_id', cluster_id_to_color,
                        "2-Section Graph (Nodes colored by Hypergraph Cluster ID)",
                        TWASECTION_PLOT_FOUND_CLUSTERS_FILE, pos=common_pos)
else:
    print("Skipping plot by cluster_id due to missing color map.")

print("\nSCRIPT 8: 2-Section graph plotting attempt complete.")
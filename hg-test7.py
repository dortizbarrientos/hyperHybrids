# SCRIPT 7: Plotting the Hypergraph using HyperNetX

import json
import pandas as pd
import hypernetx as hnx
import matplotlib.pyplot as plt
import matplotlib.cm as cm 
import networkx as nx 

# --- Input Filenames ---
HYPERGRAPH_STRUCTURE_FILE = 'hypergraph_structure.json' 
INDIVIDUALS_FILE = 'simulated_individuals.csv'      

# --- Output Plot Filename ---
HYPERGRAPH_PLOT_FILE = 'hypergraph_visualization.png'

# --- Load Hypergraph Structure and Reconstruct H ---
print("SCRIPT 7: Loading hypergraph structure and reconstructing H...")
H = None
try:
    with open(HYPERGRAPH_STRUCTURE_FILE, 'r') as f:
        data = json.load(f)
    raw_hyperedges = data.get('hyperedges', [])
    hyperedges_for_hnx_constructor = []
    for i_he, he_list in enumerate(raw_hyperedges):
        try:
            current_edge = set(map(int, he_list))
            if not current_edge: continue
            hyperedges_for_hnx_constructor.append(current_edge)
        except ValueError as ve:
            print(f"Warning: Non-integer data in loaded hyperedge: {he_list}. Error: {ve}. Skipping.")
            continue
    if not hyperedges_for_hnx_constructor:
        print("Error: No valid hyperedges found to construct H.")
        exit()
    H = hnx.Hypergraph(hyperedges_for_hnx_constructor)
    print(f"Hypergraph H reconstructed successfully with {len(H.nodes)} nodes and {len(H.edges)} hyperedges.")
except FileNotFoundError:
    print(f"Error: {HYPERGRAPH_STRUCTURE_FILE} not found. Please ensure Script 3 ran successfully.")
    exit()
except Exception as e:
    print(f"An error occurred while loading or reconstructing H: {e}")
    exit()

# --- Prepare Node Color Data ---
legend_elements_data = {} 
node_colors_list_for_draw = None 

try:
    individuals_df = pd.read_csv(INDIVIDUALS_FILE)
    unique_true_groups = sorted(individuals_df['true_group'].unique())
    
    if len(unique_true_groups) <= 10: palette = cm.get_cmap('Paired', len(unique_true_groups))
    elif len(unique_true_groups) <= 20: palette = cm.get_cmap('tab20', len(unique_true_groups))
    else: palette = cm.get_cmap('viridis', len(unique_true_groups))
    
    group_to_color_map = {group: palette(i) for i, group in enumerate(unique_true_groups)}
    legend_elements_data = group_to_color_map

    temp_node_colors_list = []
    h_nodes_list = list(H.nodes) 
    for node_id in h_nodes_list:
        # Find the true_group for the node_id
        # Ensure individual_id in individuals_df is the same type as node_id from H.nodes for matching
        node_info = individuals_df[individuals_df['individual_id'] == int(node_id)]
        if not node_info.empty:
            true_group = node_info['true_group'].iloc[0]
            temp_node_colors_list.append(group_to_color_map.get(true_group, 'grey'))
        else:
            temp_node_colors_list.append('grey') # Default if node_id not in individuals_df
    
    if len(temp_node_colors_list) == len(H.nodes):
        node_colors_list_for_draw = temp_node_colors_list
        print("Prepared list of node colors based on 'true_group' in H.nodes order.")
    else:
        print("Warning: Length mismatch when creating ordered node color list. Defaulting colors.")

except FileNotFoundError:
    print(f"Warning: {INDIVIDUALS_FILE} not found. Nodes will use a default plot color.")
except Exception as e:
    print(f"Warning: Could not prepare node colors. Nodes will use a default color. Error: {e}")

# --- Plot the Hypergraph using HyperNetX ---
if H and len(H.nodes) > 0:
    print("\nPlotting the hypergraph using hnx.draw()...")
    plt.figure(figsize=(15, 12)) 
    
    current_nodes_kwargs = {
        'linewidths': 0.5,
        'edgecolors': 'black'
        # 's' (size) is removed, will be controlled by node_radius parameter of hnx.draw()
    }
    if node_colors_list_for_draw:
        current_nodes_kwargs['facecolors'] = node_colors_list_for_draw # List of colors
    else:
        current_nodes_kwargs['facecolor'] = 'skyblue' # Single color

    try:
        hnx.draw(H,
                 layout=nx.spring_layout, 
                 layout_kwargs={'seed': 42, 'k': 0.3, 'iterations': 50}, 
                 node_radius=0.1, # Use node_radius for size (experiment with this value, e.g., 0.05 to 1 or higher)
                 with_node_labels=True,      
                 node_labels_kwargs={'fontsize': 6, 'alpha':0.8}, # Reduced fontsize
                 with_edge_labels=False,     
                 nodes_kwargs=current_nodes_kwargs, 
                 edges_kwargs={'linewidths': 1.5, 'alpha': 0.2, 'edgecolors':'darkgray', 'facecolors':'whitesmoke'}
                )
        
        plot_title = "Hypergraph Visualization"
        if node_colors_list_for_draw and legend_elements_data:
            handles = [plt.Line2D([0], [0], marker='o', color='w', label=group,
                                   markerfacecolor=color, markersize=10)
                       for group, color in legend_elements_data.items()]
            plt.legend(handles=handles, title="True Group", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
            plot_title += " (Nodes colored by True Group)"
            plt.subplots_adjust(right=0.85) 
        
        plt.title(plot_title, fontsize=16)
        plt.savefig(HYPERGRAPH_PLOT_FILE, bbox_inches='tight')
        print(f"Hypergraph plot saved to {HYPERGRAPH_PLOT_FILE}")
        # plt.show() 

    except TypeError as te:
        print(f"TypeError during hypergraph plotting: {te}")
        print("This can happen if an argument in nodes_kwargs or edges_kwargs is not as expected by Matplotlib.")
        print(f"DEBUG: nodes_kwargs used: {current_nodes_kwargs}")
    except Exception as e_draw:
        print(f"An error occurred during hypergraph plotting: {e_draw}")
else:
    print("\nSkipping hypergraph plotting as H is not defined or is empty.")

print("\nSCRIPT 7: Hypergraph plotting attempt complete.")
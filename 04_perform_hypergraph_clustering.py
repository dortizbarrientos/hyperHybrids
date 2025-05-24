# SCRIPT 4: Loading Hypergraph, Clustering, and Saving Assignments

import json
import pandas as pd
import hypernetx as hnx
# Attempt to import the hypergraph_modularity module
try:
    import hypernetx.algorithms.hypergraph_modularity as hmod
    HMOD_AVAILABLE = True
except ImportError:
    print("Warning: Could not import hypernetx.algorithms.hypergraph_modularity.")
    print("Hypergraph clustering via Kumar's algorithm will not be available.")
    print("Please ensure HyperNetX is fully installed with all its algorithm components,")
    print("or that the module path is correct for your version.")
    HMOD_AVAILABLE = False
except Exception as e:
    print(f"An unexpected error occurred importing hypergraph_modularity: {e}")
    HMOD_AVAILABLE = False


# --- Input Filename (from Script 3) ---
HYPERGRAPH_STRUCTURE_FILE = 'hypergraph_structure.json'

# --- Output Filename for Cluster Assignments ---
CLUSTER_ASSIGNMENTS_FILE = 'hypergraph_cluster_assignments.csv'

# --- Load Hypergraph Structure and Reconstruct H ---
print("SCRIPT 4: Loading hypergraph structure and reconstructing H...")
H = None
nodes_from_file = []
hyperedges_from_file = []

try:
    with open(HYPERGRAPH_STRUCTURE_FILE, 'r') as f:
        data = json.load(f)
    
    nodes_from_file = data.get('nodes', [])
    raw_hyperedges = data.get('hyperedges', [])
    
    # Convert hyperedges to sets of integers for HNX constructor
    hyperedges_for_hnx_constructor = []
    for i_he, he_list in enumerate(raw_hyperedges):
        try:
            current_edge = set(map(int, he_list))
            if not current_edge:
                # print(f"Warning: Skipping empty hyperedge at index {i_he} from loaded structure.")
                continue
            hyperedges_for_hnx_constructor.append(current_edge)
        except ValueError as ve:
            print(f"Warning: Non-integer data in loaded hyperedge: {he_list}. Error: {ve}. Skipping.")
            continue
            
    if not hyperedges_for_hnx_constructor:
        print("Error: No valid hyperedges found in the loaded structure file to construct H.")
        exit()

    H = hnx.Hypergraph(hyperedges_for_hnx_constructor)
    print(f"Hypergraph H reconstructed successfully with {len(H.nodes)} nodes and {len(H.edges)} hyperedges.")

except FileNotFoundError:
    print(f"Error: {HYPERGRAPH_STRUCTURE_FILE} not found. Please ensure Script 3 ran successfully.")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {HYPERGRAPH_STRUCTURE_FILE}.")
    exit()
except Exception as e:
    print(f"An error occurred while loading or reconstructing H: {e}")
    exit()

# --- Apply Hypergraph Clustering Algorithm ---
cluster_assignments_df = pd.DataFrame()

if H and HMOD_AVAILABLE:
    print("\nApplying Kumar's algorithm for hypergraph clustering...")
    try:
        # According to HNX documentation, kumar algorithm returns a partition (list of sets of nodes)
        # K = hmod.kumar(HG)
        partition = hmod.kumar(H) # This might take a moment for larger hypergraphs
        
        if partition:
            print(f"Kumar's algorithm resulted in {len(partition)} clusters.")
            
            # Convert partition (list of sets) to a DataFrame: individual_id, cluster_id
            node_to_cluster = {}
            for cluster_idx, node_set in enumerate(partition):
                for node in node_set:
                    node_to_cluster[int(node)] = cluster_idx # Ensure node is int for merging
            
            if node_to_cluster:
                cluster_assignments_df = pd.DataFrame(list(node_to_cluster.items()), columns=['individual_id', 'cluster_id'])
                cluster_assignments_df = cluster_assignments_df.sort_values(by='individual_id').reset_index(drop=True)
                
                print(f"Successfully assigned {len(cluster_assignments_df)} individuals to clusters.")
                print("Cluster assignments (first 5 rows):")
                print(cluster_assignments_df.head())

                # Save cluster assignments
                cluster_assignments_df.to_csv(CLUSTER_ASSIGNMENTS_FILE, index=False)
                print(f"\nCluster assignments saved to {CLUSTER_ASSIGNMENTS_FILE}")
            else:
                print("Warning: Kumar's algorithm returned a partition, but no node assignments could be derived.")
                
        else:
            print("Warning: Kumar's algorithm did not return a partition or returned an empty partition.")

    except Exception as e_kumar:
        print(f"An error occurred while applying Kumar's algorithm: {e_kumar}")
        print("This might be due to missing dependencies (e.g., 'python-igraph') or an issue within the algorithm for this data.")
        print("You can try other clustering approaches or ensure all dependencies for hmod.kumar are met.")

elif not H:
    print("\nSkipping clustering as Hypergraph H was not reconstructed.")
elif not HMOD_AVAILABLE:
    print("\nSkipping Kumar's clustering as hypergraph_modularity module is not available.")


if cluster_assignments_df.empty:
    print("\nNo cluster assignments were generated or saved.")

print("\nSCRIPT 4: Clustering attempt complete.")
print("If successful, the next step (Script 5) will be to evaluate these cluster assignments.")
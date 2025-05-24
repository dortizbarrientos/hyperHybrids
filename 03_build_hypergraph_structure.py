# SCRIPT 3: Loading Hyperedges, Constructing H, and SAVING H's Structure

import json
import hypernetx as hnx

# --- Input Filename for Hyperedges (must match output from Script 2) ---
HYPEREDGES_FILE = 'simulated_hyperedges.json'

# --- Output Filename for the Hypergraph's Essential Structure ---
HYPERGRAPH_STRUCTURE_FILE = 'hypergraph_structure.json'

# --- Load Hyperedges from JSON file ---
print("SCRIPT 3: Loading hyperedges from file...")
H = None # Initialize H to None
hyperedges_for_hnx_constructor = [] # Initialize

try:
    with open(HYPEREDGES_FILE, 'r') as f:
        loaded_hyperedges_as_lists = json.load(f)
    
    hyperedges_for_hnx_constructor = []
    for i_he, he_list in enumerate(loaded_hyperedges_as_lists):
        try:
            # Ensure all elements are integers and form a set
            current_edge = set(map(int, he_list))
            if not current_edge: # Skip empty hyperedges if any were accidentally created/loaded
                # print(f"Warning: Skipping empty hyperedge at index {i_he} from input file.")
                continue
            hyperedges_for_hnx_constructor.append(current_edge)
        except ValueError as ve:
            print(f"Warning: Found non-integer data in hyperedge list: {he_list} at index {i_he}. Skipping this hyperedge. Error: {ve}")
            continue
    
    if not hyperedges_for_hnx_constructor:
        print("Warning: No valid hyperedges were loaded/processed from the file for HNX constructor.")
    else:
        print(f"Successfully processed {len(hyperedges_for_hnx_constructor)} valid hyperedges from {HYPEREDGES_FILE} for HNX constructor.")

except FileNotFoundError:
    print(f"Error: {HYPEREDGES_FILE} not found. Please ensure Script 2 has been run successfully.")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {HYPEREDGES_FILE}. File might be corrupted or not in JSON format.")
    exit()
except Exception as e:
    print(f"An error occurred while loading or processing hyperedges: {e}")
    exit()

# --- Construct Hypergraph Object using HyperNetX ---
if hyperedges_for_hnx_constructor:
    print("\nConstructing HyperNetX Hypergraph object...")
    try:
        import warnings
        # warnings.filterwarnings("ignore", category=DeprecationWarning, module="hypernetx")
        # warnings.filterwarnings("ignore", category=FutureWarning, module="hypernetx")
        # warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

        H = hnx.Hypergraph(hyperedges_for_hnx_constructor)
        
        print("Hypergraph object `H` created successfully in memory.")
        print(f"Number of nodes (individuals) in H: {len(H.nodes)}")
        # H.edges contains the UIDs of the hyperedges as recognized by HNX
        print(f"Number of unique hyperedges in H object (UIDs): {len(H.edges)}") 
        
        # --- Extract essential structure from H and save it ---
        print(f"\nExtracting structure from H and saving to {HYPERGRAPH_STRUCTURE_FILE}...")
        
        nodes_list = sorted(list(map(int, H.nodes))) # Ensure nodes are ints and sorted

        processed_hyperedges_list = []
        if hasattr(H, 'incidence_dict') and isinstance(H.incidence_dict, dict):
            print("Using H.incidence_dict to retrieve hyperedges...")
            # H.edges provides the UIDs which should be keys in H.incidence_dict
            # The values in H.incidence_dict (for these keys) should be the sets of nodes.
            edge_uids_from_H = list(H.edges)
            for edge_uid in edge_uids_from_H:
                edge_members = H.incidence_dict.get(edge_uid) # Use .get() for safety
                if edge_members is not None and hasattr(edge_members, '__iter__'):
                    try:
                        processed_hyperedges_list.append(sorted(list(map(int, edge_members))))
                    except (TypeError, ValueError) as e_conv:
                        print(f"Warning: Could not convert members of edge UID {edge_uid} (members: {edge_members}) to sorted list of ints. Error: {e_conv}. Skipping.")
                else:
                    print(f"Warning: Hyperedge with UID {edge_uid} has None or non-iterable members in H.incidence_dict (members: {edge_members}). Skipping.")
            print(f"Extracted {len(processed_hyperedges_list)} hyperedges using H.incidence_dict.")
        else:
            print("Warning: H.incidence_dict not found or not a dictionary. Cannot extract hyperedge compositions this way.")
            print("Attempting to iterate H directly (less reliable if H[edge_uid] was problematic).")
            # Fallback attempt by iterating H (treats H like a dictionary of edge_uid: members)
            # This was the method that sometimes yielded None for H[edge_uid]
            edge_uids_from_H = list(H.edges)
            for edge_uid in edge_uids_from_H:
                try:
                    edge_members = H[edge_uid] # This is the part that might return None
                    if edge_members is not None and hasattr(edge_members, '__iter__'):
                        processed_hyperedges_list.append(sorted(list(map(int, edge_members))))
                    else:
                        print(f"Warning (fallback): Hyperedge UID {edge_uid} yielded None or non-iterable members via H[edge_uid]. Skipping.")
                except Exception as e_fallback_lookup:
                    print(f"Warning (fallback): Error looking up/processing edge UID {edge_uid} via H[edge_uid]: {e_fallback_lookup}. Skipping.")
            print(f"Fallback H[edge_uid] iteration extracted {len(processed_hyperedges_list)} hyperedges.")


        if not processed_hyperedges_list and len(H.edges) > 0 :
             print(f"Critical Warning: Successfully created H with {len(H.edges)} hyperedges, but failed to extract any for saving. The structure file will be incomplete.")
        elif not processed_hyperedges_list and len(H.edges) == 0:
             print("Information: H object has no edges, so no hyperedges will be saved to the structure file (as expected).")


        hypergraph_structure_data = {
            "nodes": nodes_list,
            "hyperedges": processed_hyperedges_list # This list might be shorter than len(H.edges) if some extractions failed
        }

        with open(HYPERGRAPH_STRUCTURE_FILE, 'w') as f_json_out:
            json.dump(hypergraph_structure_data, f_json_out, indent=2)
        
        print(f"Hypergraph structure (nodes and {len(processed_hyperedges_list)} hyperedges) saved to {HYPERGRAPH_STRUCTURE_FILE}.")
        print(f"In the next script (Script 4), you can load this file, and reconstruct H using:")
        print(f"  import json, hypernetx as hnx")
        print(f"  with open('{HYPERGRAPH_STRUCTURE_FILE}', 'r') as f:")
        print(f"      data = json.load(f)")
        print(f"  H_loaded = hnx.Hypergraph(data['hyperedges'])")

    except Exception as e_construct_or_save:
        print(f"An critical error occurred during HyperNetX Hypergraph processing or saving its structure: {e_construct_or_save}")
else:
    print("\nSkipping Hypergraph construction and saving as no valid hyperedges were loaded/processed.")

print("\nSCRIPT 3: Hypergraph construction and structure saving attempt complete.")x
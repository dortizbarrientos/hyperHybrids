# SCRIPT 2: Loading Data, Defining Hyperedges, and SAVING Hyperedges

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import json # Import json for saving the hyperedge list

# --- Input Filenames (must match output from Script 1) ---
INDIVIDUALS_FILE = 'simulated_individuals.csv'
TRAITS_FILE = 'simulated_traits.csv'
GENETIC_DIST_FILE = 'simulated_genetic_distances.csv'

# --- Output Filename for Hyperedges ---
HYPEREDGES_FILE = 'simulated_hyperedges.json'

# --- Load DataFrames ---
print("SCRIPT 2: Loading simulated data...")
try:
    individuals_df = pd.read_csv(INDIVIDUALS_FILE)
    traits_df = pd.read_csv(TRAITS_FILE)
    genetic_dist_df = pd.read_csv(GENETIC_DIST_FILE, index_col=0)
    genetic_dist_df.columns = genetic_dist_df.columns.astype(int)
    genetic_dist_df.index = genetic_dist_df.index.astype(int)
    print("Data loaded successfully.")
    # (Optional: print df.head() to verify)
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure Script 1 has been run and CSV files are in the correct location.")
    exit()
except Exception as e:
    print(f"An error occurred while loading data: {e}")
    exit()

# --- Helper Function to remove duplicate hyperedges ---
def unique_hyperedges(hyperedge_list):
    return list(set(hyperedge_list))

# --- Hyperedge Definition Functions (Identical to previous version) ---
def get_trait_knn_hyperedges(traits_df, individual_ids_col='individual_id', k=5, scale_traits=True):
    if traits_df.empty or individual_ids_col not in traits_df.columns:
        print("Traits DataFrame is empty or individual_ids_col is missing.")
        return []
    trait_feature_cols = [col for col in traits_df.columns if col != individual_ids_col]
    if not trait_feature_cols:
        print("No trait feature columns found in traits_df.")
        return []
    trait_values = traits_df[trait_feature_cols].values
    ids = traits_df[individual_ids_col].values
    if scale_traits:
        scaler = StandardScaler()
        trait_values = scaler.fit_transform(trait_values)
    nn = NearestNeighbors(n_neighbors=k + 1, algorithm='auto', metric='euclidean')
    nn.fit(trait_values)
    _, indices = nn.kneighbors(trait_values)
    hyperedges = [frozenset(ids[indices[i]]) for i in range(len(indices))]
    # print(f"Generated {len(hyperedges)} trait k-NN hyperedges (k={k}).") # Moved print to example usage
    return unique_hyperedges(hyperedges)

def get_trait_threshold_hyperedges(traits_df, trait_column, threshold, mode='above', individual_ids_col='individual_id'):
    if traits_df.empty or trait_column not in traits_df.columns or individual_ids_col not in traits_df.columns:
        print(f"Traits DataFrame error or column {trait_column} / {individual_ids_col} missing.")
        return []
    if mode == 'above': selected_individuals = traits_df[traits_df[trait_column] > threshold][individual_ids_col].values
    elif mode == 'below': selected_individuals = traits_df[traits_df[trait_column] < threshold][individual_ids_col].values
    else: print("Invalid mode for trait threshold. Choose 'above' or 'below'."); return []
    if len(selected_individuals) > 1:
        hyperedge = frozenset(selected_individuals)
        # print(f"Generated 1 trait threshold hyperedge for {trait_column} {mode} {threshold} with {len(hyperedge)} members.")
        return [hyperedge]
    # print(f"No individuals met trait threshold criteria for {trait_column} {mode} {threshold} or only one individual found.")
    return []

def get_genetic_knn_hyperedges(genetic_dist_df, k=5):
    if genetic_dist_df.empty: print("Genetic distance DataFrame is empty."); return []
    ids = genetic_dist_df.index.values
    hyperedges = []
    for i, _ in enumerate(ids): # individual_id is ids[i]
        distances_to_individual = genetic_dist_df.iloc[i].sort_values()
        neighbor_ids_series = distances_to_individual.head(k + 1).index
        hyperedges.append(frozenset(neighbor_ids_series.astype(int)))
    # print(f"Generated {len(hyperedges)} genetic k-NN hyperedges (k={k}).")
    return unique_hyperedges(hyperedges)

def get_family_hyperedges(individuals_df, family_id_col='family_id', individual_ids_col='individual_id', min_family_size=2):
    if individuals_df.empty or family_id_col not in individuals_df.columns or individual_ids_col not in individuals_df.columns:
        print("Individuals DataFrame error or column missing for family hyperedges."); return []
    hyperedges = []
    valid_families = individuals_df[individuals_df[family_id_col] != -1]
    grouped_by_family = valid_families.groupby(family_id_col)
    for _, group in grouped_by_family:
        if len(group) >= min_family_size:
            hyperedges.append(frozenset(group[individual_ids_col].values))
    # print(f"Generated {len(hyperedges)} family-based hyperedges (min_family_size={min_family_size}).")
    return unique_hyperedges(hyperedges)

def get_genetic_distance_threshold_hyperedges(genetic_dist_df, dist_threshold=0.2, min_size=2):
    if genetic_dist_df.empty: print("Genetic distance DataFrame is empty."); return []
    ids = genetic_dist_df.index.values
    hyperedges = []
    for i, _ in enumerate(ids): # individual_id_row is ids[i]
        close_neighbors_mask = genetic_dist_df.iloc[i] < dist_threshold
        close_neighbor_ids = genetic_dist_df.columns[close_neighbors_mask].tolist()
        if len(close_neighbor_ids) >= min_size:
            hyperedges.append(frozenset(close_neighbor_ids))
    # print(f"Generated {len(hyperedges)} genetic distance threshold hyperedges (threshold={dist_threshold}, min_size={min_size}).")
    return unique_hyperedges(hyperedges)

def get_environment_hyperedges(individuals_df, environment_col='environment', individual_ids_col='individual_id', min_env_size=2):
    if individuals_df.empty or environment_col not in individuals_df.columns or individual_ids_col not in individuals_df.columns:
        print("Individuals DataFrame error or column missing for environment hyperedges."); return []
    hyperedges = []
    grouped_by_environment = individuals_df.groupby(environment_col)
    for _, group in grouped_by_environment:
        if len(group) >= min_env_size:
            hyperedges.append(frozenset(group[individual_ids_col].values))
    # print(f"Generated {len(hyperedges)} environment-based hyperedges (min_env_size={min_env_size}).")
    return unique_hyperedges(hyperedges)

def get_family_in_env_hyperedges(individuals_df, individual_ids_col='individual_id', family_id_col='family_id', environment_col='environment', min_size=2):
    combined_hyperedges = []
    if family_id_col not in individuals_df.columns or environment_col not in individuals_df.columns or individual_ids_col not in individuals_df.columns:
        print("Individuals DataFrame missing required columns for family_in_env_hyperedges.")
        return []
    valid_families = individuals_df[individuals_df[family_id_col] != -1]
    for _, family_members in valid_families.groupby(family_id_col):
        for _, members_in_env in family_members.groupby(environment_col):
            if len(members_in_env) >= min_size:
                 combined_hyperedges.append(frozenset(members_in_env[individual_ids_col]))
    # print(f"Generated {len(combined_hyperedges)} family-in-environment hyperedges (min_size={min_size}).")
    return unique_hyperedges(combined_hyperedges)

# --- Example Usage: Generate various hyperedges from loaded data ---
print("\n--- Generating Hyperedges from Loaded Data ---")
all_hyperedges_from_loaded = []
generated_hyperedge_counts = {}

# Trait-based
if not traits_df.empty:
    trait_knn_h_loaded = get_trait_knn_hyperedges(traits_df, k=3, scale_traits=True)
    all_hyperedges_from_loaded.extend(trait_knn_h_loaded)
    generated_hyperedge_counts['trait_knn'] = len(trait_knn_h_loaded)
    
    # Example threshold - adjust based on your actual loaded traits_df['trait_0'] distribution
    # trait_0_median = traits_df['trait_0'].median()
    # trait_thresh_h_loaded = get_trait_threshold_hyperedges(traits_df, 'trait_0', threshold=trait_0_median, mode='above')
    # if trait_thresh_h_loaded: all_hyperedges_from_loaded.extend(trait_thresh_h_loaded); generated_hyperedge_counts['trait_thresh'] = len(trait_thresh_h_loaded)
else:
    print("Skipping trait-based hyperedges as traits_df is empty or not loaded correctly.")

# Genetic-based
if not genetic_dist_df.empty:
    genetic_knn_h_loaded = get_genetic_knn_hyperedges(genetic_dist_df, k=3)
    all_hyperedges_from_loaded.extend(genetic_knn_h_loaded)
    generated_hyperedge_counts['genetic_knn'] = len(genetic_knn_h_loaded)
    
    # Adjust threshold based on your actual loaded genetic_dist_df values
    # genetic_dist_thresh_h_loaded = get_genetic_distance_threshold_hyperedges(genetic_dist_df, dist_threshold=0.25, min_size=2)
    # if genetic_dist_thresh_h_loaded: all_hyperedges_from_loaded.extend(genetic_dist_thresh_h_loaded); generated_hyperedge_counts['genetic_dist_thresh'] = len(genetic_dist_thresh_h_loaded)
else:
    print("Skipping genetic k-NN/distance threshold hyperedges as genetic_dist_df is empty or not loaded correctly.")

if not individuals_df.empty:
    family_h_loaded = get_family_hyperedges(individuals_df, min_family_size=2)
    all_hyperedges_from_loaded.extend(family_h_loaded)
    generated_hyperedge_counts['family'] = len(family_h_loaded)
    
    env_h_loaded = get_environment_hyperedges(individuals_df, min_env_size=2)
    all_hyperedges_from_loaded.extend(env_h_loaded)
    generated_hyperedge_counts['environment'] = len(env_h_loaded)

    family_env_h_loaded = get_family_in_env_hyperedges(individuals_df)
    all_hyperedges_from_loaded.extend(family_env_h_loaded)
    generated_hyperedge_counts['family_in_env'] = len(family_env_h_loaded)
else:
    print("Skipping family, environment, and family-in-environment hyperedges as individuals_df is empty or not loaded correctly.")

# Print summary of generated hyperedges
print("\nSummary of generated hyperedge counts:")
for k, v in generated_hyperedge_counts.items():
    print(f"- {k}: {v}")

# Consolidate all unique hyperedges
final_hyperedge_list_loaded = unique_hyperedges(all_hyperedges_from_loaded)
print(f"\nTotal number of unique hyperedges generated from loaded data: {len(final_hyperedge_list_loaded)}")

if final_hyperedge_list_loaded:
    print(f"Example of a few hyperedges (sets of individual_ids):")
    for i, h_edge in enumerate(final_hyperedge_list_loaded[:min(3, len(final_hyperedge_list_loaded))]):
        print(f"Hyperedge {i}: {h_edge}")
else:
    print("No hyperedges were generated from loaded data. Check data loading and parameters.")

# In SCRIPT 2, modify the saving part:

# --- Save the final hyperedge list to a JSON file ---
hyperedges_for_json = [list(map(int, he)) for he in final_hyperedge_list_loaded] # Ensure all IDs are standard Python ints

print(f"\nAttempting to save {len(hyperedges_for_json)} hyperedges to {HYPEREDGES_FILE}.") # Added this line

if not hyperedges_for_json:
    print(f"Warning: The list of hyperedges to be saved ('hyperedges_for_json') is empty.")
    # Still save an empty list as valid JSON
    try:
        with open(HYPEREDGES_FILE, 'w') as f:
            json.dump([], f) # Explicitly save an empty list
        print(f"Saved an empty list as valid JSON to {HYPEREDGES_FILE} because no hyperedges were generated/consolidated.")
    except Exception as e:
        print(f"An error occurred while saving an empty hyperedge list to JSON: {e}")
else:
    try:
        with open(HYPEREDGES_FILE, 'w') as f:
            json.dump(hyperedges_for_json, f)
        print(f"Saved final list of {len(hyperedges_for_json)} hyperedges to {HYPEREDGES_FILE}")
    except TypeError as te:
        print(f"TypeError during JSON dump: {te}. This might indicate non-serializable data within the hyperedges.")
        # Try to identify problematic data
        for i, he in enumerate(hyperedges_for_json):
            for j, item in enumerate(he):
                if not isinstance(item, (int, float, str, bool, type(None))): # Check for common serializable types
                    print(f"Problematic item: {item} (type: {type(item)}) in hyperedge {i} at sub-index {j}")
                    break
            if i > 5: break # Only check first few hyperedges
    except Exception as e:
        print(f"An error occurred while saving hyperedges to JSON: {e}")
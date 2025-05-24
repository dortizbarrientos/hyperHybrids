# SCRIPT 5: Evaluating Hypergraph Clustering Results

import pandas as pd
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score
from sklearn.metrics import homogeneity_score, completeness_score, v_measure_score
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score, homogeneity_completeness_v_measure
# Ensure homogeneity_completeness_v_measure is included here ^
from collections import Counter

# --- Input Filenames ---
CLUSTER_ASSIGNMENTS_FILE = 'hypergraph_cluster_assignments.csv' # From Script 4
INDIVIDUALS_INFO_FILE = 'simulated_individuals.csv'      # From Script 1

# --- Load Data ---
print("SCRIPT 5: Evaluating clustering results...")
try:
    cluster_assignments_df = pd.read_csv(CLUSTER_ASSIGNMENTS_FILE)
    individuals_df = pd.read_csv(INDIVIDUALS_INFO_FILE)
    print(f"Loaded cluster assignments for {len(cluster_assignments_df)} individuals.")
    print(f"Loaded original info for {len(individuals_df)} individuals.")
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure necessary CSV files are in the correct location.")
    print(f"Required: '{CLUSTER_ASSIGNMENTS_FILE}' from Script 4 and '{INDIVIDUALS_INFO_FILE}' from Script 1.")
    exit()
except Exception as e:
    print(f"An error occurred while loading data: {e}")
    exit()

# --- Merge Data for Comparison ---
if 'individual_id' not in cluster_assignments_df.columns or 'individual_id' not in individuals_df.columns:
    print("Error: 'individual_id' column missing in one of the files. Cannot merge.")
    exit()

# Ensure individual_id is of the same type for merging, if necessary
# cluster_assignments_df['individual_id'] = cluster_assignments_df['individual_id'].astype(int)
# individuals_df['individual_id'] = individuals_df['individual_id'].astype(int)

merged_df = pd.merge(individuals_df, cluster_assignments_df, on='individual_id', how='inner')

if len(merged_df) != len(individuals_df):
    print(f"Warning: Merge resulted in {len(merged_df)} rows, but expected {len(individuals_df)}. Check for ID mismatches or duplicates.")
    if len(merged_df) == 0:
        print("Merge failed or resulted in an empty DataFrame. Cannot proceed with evaluation.")
        exit()

print(f"\nSuccessfully merged original info with cluster assignments for {len(merged_df)} individuals.")
print("Merged DataFrame (first 5 rows):")
print(merged_df.head())

# --- Define True Labels and Predicted Cluster Labels ---
true_labels = merged_df['true_group']
predicted_labels = merged_df['cluster_id']

# --- Calculate Clustering Evaluation Metrics ---
print("\n--- Clustering Performance Metrics (compared to 'true_group') ---")
try:
    ari = adjusted_rand_score(true_labels, predicted_labels)
    ami = adjusted_mutual_info_score(true_labels, predicted_labels)
    homogeneity, completeness, v_measure = homogeneity_completeness_v_measure(true_labels, predicted_labels)

    print(f"Adjusted Rand Index (ARI): {ari:.4f}")
    print(f"Adjusted Mutual Information (AMI): {ami:.4f}")
    print(f"Homogeneity: {homogeneity:.4f}")
    print(f"Completeness: {completeness:.4f}")
    print(f"V-measure: {v_measure:.4f}")
except ValueError as ve:
    print(f"Error calculating metrics: {ve}. This can happen if labels are problematic (e.g., all unique).")
except Exception as e:
    print(f"An unexpected error occurred during metrics calculation: {e}")

# --- Contingency Table (Cross-Tabulation) ---
print("\n--- Contingency Table (True Groups vs. Found Clusters) ---")
contingency_table = pd.crosstab(merged_df['true_group'], merged_df['cluster_id'], rownames=['True Group'], colnames=['Found Cluster'])
print(contingency_table)

# --- Characterize Clusters ---
print("\n--- Cluster Characterization ---")
found_clusters = sorted(merged_df['cluster_id'].unique())
print(f"Found {len(found_clusters)} clusters: {found_clusters}")

for cluster_val in found_clusters:
    print(f"\n--- Details for Found Cluster {cluster_val} ---")
    cluster_data = merged_df[merged_df['cluster_id'] == cluster_val]
    print(f"  Number of individuals: {len(cluster_data)}")
    
    print("  True Group Distribution:")
    true_group_counts = cluster_data['true_group'].value_counts(normalize=True).sort_index()
    for group, prop in true_group_counts.items():
        print(f"    - {group}: {prop:.2%} ({cluster_data['true_group'].value_counts()[group]} individuals)")
        
    print("  Environment Distribution:")
    env_counts = cluster_data['environment'].value_counts(normalize=True).sort_index()
    for env, prop in env_counts.items():
        print(f"    - {env}: {prop:.2%} ({cluster_data['environment'].value_counts()[env]} individuals)")

    # Family representation (show if any family is significantly represented)
    # Only consider families with more than one member in this cluster for brevity
    family_counts_in_cluster = cluster_data[cluster_data['family_id'] != -1]['family_id'].value_counts()
    significant_families = family_counts_in_cluster[family_counts_in_cluster > 1]
    if not significant_families.empty:
        print("  Significant Family Representation (families with >1 member in this cluster):")
        for fam_id, count in significant_families.items():
            total_fam_members = len(individuals_df[individuals_df['family_id'] == fam_id])
            print(f"    - Family {fam_id}: {count} members (out of {total_fam_members} total in family)")
    else:
        print("  No small families significantly represented (or only single members present).")


# --- Analysis of Special Cases (Hybrids, Convergent Evolution, Plasticity) ---
print("\n--- Analysis of Special Cases ---")

# 1. Hybrids
hybrid_individuals = merged_df[merged_df['true_group'] == 'Hybrid_G1G2']
if not hybrid_individuals.empty:
    print("\nHybrid (Hybrid_G1G2) Individuals:")
    print(f"  Total hybrids: {len(hybrid_individuals)}")
    print("  Cluster assignments for hybrids:")
    hybrid_cluster_counts = hybrid_individuals['cluster_id'].value_counts().sort_index()
    for cluster_id, count in hybrid_cluster_counts.items():
        print(f"    - Found Cluster {cluster_id}: {count} hybrid individuals")
else:
    print("\nNo 'Hybrid_G1G2' individuals found in the merged data (check simulation settings or data loading).")

# 2. Convergent Evolution
# Recall: G1 and G3 in E2 were made similar for Trait 1.
# Let's see if individuals from G1 in E2 and G3 in E2 tend to cluster together.
conv_G1_E2 = merged_df[(merged_df['true_group'] == 'G1') & (merged_df['environment'] == 'E2')]
conv_G3_E2 = merged_df[(merged_df['true_group'] == 'G3') & (merged_df['environment'] == 'E2')]

if not conv_G1_E2.empty or not conv_G3_E2.empty:
    print("\nConvergent Evolution Scenario (G1 in E2 vs. G3 in E2 for Trait 1):")
    if not conv_G1_E2.empty:
        print("  Cluster assignments for G1 individuals in Environment E2:")
        print(conv_G1_E2.groupby('cluster_id').size().reset_index(name='count'))
    if not conv_G3_E2.empty:
        print("  Cluster assignments for G3 individuals in Environment E2:")
        print(conv_G3_E2.groupby('cluster_id').size().reset_index(name='count'))
    # Further analysis here could involve looking at the specific clusters these individuals fall into
    # and seeing if they overlap more than expected by chance given their different true_group.
else:
    print("\nNo individuals found for the convergent evolution scenario (check simulation or group definitions).")


# 3. Phenotypic Plasticity
# Recall: G1 individuals had Trait 0 affected by environment (E1 vs E2).
# Do G1 individuals from E1 cluster differently from G1 individuals in E2?
plast_G1_E1 = merged_df[(merged_df['true_group'] == 'G1') & (merged_df['environment'] == 'E1')]
plast_G1_E2 = merged_df[(merged_df['true_group'] == 'G1') & (merged_df['environment'] == 'E2')]

if not plast_G1_E1.empty or not plast_G1_E2.empty:
    print("\nPhenotypic Plasticity Scenario (G1 individuals, Trait 0, by Environment):")
    if not plast_G1_E1.empty:
        print(f"  Cluster assignments for G1 individuals in Environment E1 ({len(plast_G1_E1)} individuals):")
        print(plast_G1_E1.groupby('cluster_id').size().reset_index(name='count'))
    if not plast_G1_E2.empty:
        print(f"  Cluster assignments for G1 individuals in Environment E2 ({len(plast_G1_E2)} individuals):")
        print(plast_G1_E2.groupby('cluster_id').size().reset_index(name='count'))
    # Here, you'd look to see if the distribution of G1_E1 vs G1_E2 across clusters is different.
else:
    print("\nNo G1 individuals found for the phenotypic plasticity scenario (check simulation or group definitions).")


print("\nSCRIPT 5: Evaluation complete.")
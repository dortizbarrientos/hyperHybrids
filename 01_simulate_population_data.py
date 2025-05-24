# SCRIPT 1: Data Simulation and Saving

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances # Not directly used in this version, but good for context

# --- Simulation Parameters ---
N_INDIVIDUALS = 120
N_TRUE_GROUPS = 3
N_TRAITS = 5
N_ENVIRONMENTS = 2
N_FAMILIES = 15
FAMILY_SIZE_MIN = 3
FAMILY_SIZE_MAX = 5
GROUP_PROPORTIONS = [0.35, 0.35, 0.20]
N_HYBRIDS = int(N_INDIVIDUALS * 0.10)

TRAIT_BASE_MEAN = 0.0
TRAIT_GROUP_EFFECT_SCALE = 1.5
TRAIT_ENV_EFFECT_SCALE = 1.0
TRAIT_PLASTICITY_EFFECT = 2.0
TRAIT_CONVERGENCE_EFFECT = 1.8
TRAIT_NOISE_STD = 0.5

GENETIC_DIST_BASE = 0.8
GENETIC_DIST_SAME_GROUP_EFFECT = -0.3
GENETIC_DIST_SAME_FAMILY_EFFECT = -0.4
GENETIC_DIST_HYBRID_FACTOR = 0.5

# --- Output Filenames ---
INDIVIDUALS_FILE = 'simulated_individuals.csv'
TRAITS_FILE = 'simulated_traits.csv'
GENETIC_DIST_FILE = 'simulated_genetic_distances.csv'

# --- Helper Functions ---
def assign_groups_and_hybrids(n_individuals, group_proportions, n_hybrids, n_true_groups):
    assignments = []
    counts = [int(p * (n_individuals - n_hybrids)) for p in group_proportions]
    current_sum = sum(counts)
    diff = (n_individuals - n_hybrids) - current_sum
    if diff != 0:
        idx_to_adjust = np.random.choice(len(counts), size=abs(diff), replace=True)
        for i_adj in idx_to_adjust:
            counts[i_adj] += np.sign(diff)
            
    for i_grp, count in enumerate(counts):
        assignments.extend([f"G{i_grp+1}"] * count)
    
    assignments.extend(["Hybrid_G1G2"] * n_hybrids)
    # Ensure correct number of individuals if there were rounding issues with proportions
    while len(assignments) < n_individuals:
        assignments.append(np.random.choice([f"G{i+1}" for i in range(n_true_groups)])) # Add to a random group
        
    np.random.shuffle(assignments)
    return assignments[:n_individuals]

# --- Main Simulation ---
print("SCRIPT 1: Simulating data...")
np.random.seed(42) # For reproducibility

# 1. Individual IDs and True Group Assignments
individual_ids = np.arange(N_INDIVIDUALS)
true_group_assignments = assign_groups_and_hybrids(N_INDIVIDUALS, GROUP_PROPORTIONS, N_HYBRIDS, N_TRUE_GROUPS)

individuals_df = pd.DataFrame({
    'individual_id': individual_ids,
    'true_group': true_group_assignments
})

# 2. Assign Families (Kin Groups)
family_ids = np.full(N_INDIVIDUALS, -1, dtype=int)
current_family_id = 0
individual_indices_pool = list(range(N_INDIVIDUALS))
np.random.shuffle(individual_indices_pool)

for _ in range(N_FAMILIES):
    if len(individual_indices_pool) < FAMILY_SIZE_MIN:
        break
    family_size = np.random.randint(FAMILY_SIZE_MIN, FAMILY_SIZE_MAX + 1)
    if len(individual_indices_pool) < family_size:
        continue

    current_family_members_indices = [individual_indices_pool.pop() for _ in range(family_size)]
    for member_idx in current_family_members_indices:
        family_ids[member_idx] = current_family_id
    current_family_id += 1
individuals_df['family_id'] = family_ids

# 3. Assign Environments
env_assignments = np.empty(N_INDIVIDUALS, dtype=object)
for i, row in individuals_df.iterrows():
    group = row['true_group']
    prob_e1 = 0.5
    if group == "G1": prob_e1 = 0.8
    elif group == "G2": prob_e1 = 0.2
    elif group == "G3": prob_e1 = 0.6
    elif group == "Hybrid_G1G2": prob_e1 = np.random.choice([0.8,0.2,0.5], p=[0.4,0.4,0.2])
    env_assignments[i] = "E1" if np.random.rand() < prob_e1 else "E2"
individuals_df['environment'] = env_assignments

# 4. Simulate Traits
traits_data = np.zeros((N_INDIVIDUALS, N_TRAITS))
trait_means_by_group = { f"G{i+1}": np.random.uniform(-TRAIT_GROUP_EFFECT_SCALE, TRAIT_GROUP_EFFECT_SCALE, N_TRAITS) for i in range(N_TRUE_GROUPS)}
trait_means_by_group["Hybrid_G1G2"] = (trait_means_by_group.get("G1", np.zeros(N_TRAITS)) + trait_means_by_group.get("G2", np.zeros(N_TRAITS))) / 2.0

for i in range(N_INDIVIDUALS):
    group = individuals_df.loc[i, 'true_group']
    env = individuals_df.loc[i, 'environment']
    base_traits = trait_means_by_group.get(group, np.zeros(N_TRAITS)).copy()
    if env == "E1": base_traits += np.random.uniform(-TRAIT_ENV_EFFECT_SCALE, TRAIT_ENV_EFFECT_SCALE, N_TRAITS) / 2
    else: base_traits -= np.random.uniform(-TRAIT_ENV_EFFECT_SCALE, TRAIT_ENV_EFFECT_SCALE, N_TRAITS) / 2
    traits_data[i, :] = base_traits + np.random.normal(0, TRAIT_NOISE_STD, N_TRAITS)

plasticity_trait_idx, plasticity_group = 0, "G1"
for i in individuals_df[individuals_df['true_group'] == plasticity_group].index:
    traits_data[i, plasticity_trait_idx] += TRAIT_PLASTICITY_EFFECT if individuals_df.loc[i, 'environment'] == "E1" else -TRAIT_PLASTICITY_EFFECT
print(f"Introduced plasticity for {plasticity_group} on Trait {plasticity_trait_idx}.")

convergence_trait_idx, convergence_groups, convergence_env = 1, ["G1", "G3"], "E2"
for i in individuals_df[individuals_df['true_group'].isin(convergence_groups) & (individuals_df['environment'] == convergence_env)].index:
    traits_data[i, convergence_trait_idx] += TRAIT_CONVERGENCE_EFFECT
print(f"Introduced convergent evolution for {convergence_groups} on Trait {convergence_trait_idx} in {convergence_env}.")

traits_df = pd.DataFrame(traits_data, columns=[f'trait_{j}' for j in range(N_TRAITS)])
traits_df['individual_id'] = individual_ids
traits_df = traits_df[['individual_id'] + [f'trait_{j}' for j in range(N_TRAITS)]]

# 5. Simulate Genetic Distance Matrix
genetic_distance_matrix = np.random.uniform(GENETIC_DIST_BASE - 0.1, GENETIC_DIST_BASE + 0.1, (N_INDIVIDUALS, N_INDIVIDUALS))
np.fill_diagonal(genetic_distance_matrix, 0)

for i in range(N_INDIVIDUALS):
    for j in range(i + 1, N_INDIVIDUALS):
        dist = genetic_distance_matrix[i, j]
        group_i, group_j = individuals_df.loc[i, 'true_group'], individuals_df.loc[j, 'true_group']
        family_i, family_j = individuals_df.loc[i, 'family_id'], individuals_df.loc[j, 'family_id']

        if group_i == group_j and "Hybrid" not in group_i : dist += GENETIC_DIST_SAME_GROUP_EFFECT
        if family_i != -1 and family_i == family_j: dist += GENETIC_DIST_SAME_FAMILY_EFFECT
        
        is_hybrid_i, is_hybrid_j = "Hybrid" in group_i, "Hybrid" in group_j
        g1_i, g1_j = group_i == "G1", group_j == "G1"
        g2_i, g2_j = group_i == "G2", group_j == "G2"

        if (is_hybrid_i and (g1_j or g2_j)) or (is_hybrid_j and (g1_i or g2_i)): # Hybrid to G1 or G2
            dist = (GENETIC_DIST_BASE + GENETIC_DIST_SAME_GROUP_EFFECT/2) * GENETIC_DIST_HYBRID_FACTOR + np.random.uniform(-0.05, 0.05)
        elif is_hybrid_i and is_hybrid_j: # Hybrid to Hybrid
            dist = (GENETIC_DIST_BASE + GENETIC_DIST_SAME_GROUP_EFFECT/2) * (GENETIC_DIST_HYBRID_FACTOR + 0.1) + np.random.uniform(-0.05, 0.05)

        dist = max(0.01, dist)
        genetic_distance_matrix[i, j] = genetic_distance_matrix[j, i] = dist

genetic_dist_df = pd.DataFrame(genetic_distance_matrix, index=individual_ids, columns=individual_ids)
genetic_dist_df.index.name = 'individual_id_row' # Clarify index name for CSV
genetic_dist_df.columns.name = 'individual_id_col' # Clarify column name for CSV


# --- Save DataFrames to CSV ---
individuals_df.to_csv(INDIVIDUALS_FILE, index=False)
print(f"\nSaved individuals data to {INDIVIDUALS_FILE}")
traits_df.to_csv(TRAITS_FILE, index=False)
print(f"Saved traits data to {TRAITS_FILE}")
genetic_dist_df.to_csv(GENETIC_DIST_FILE, index=True) # Save index for genetic distance matrix
print(f"Saved genetic distance matrix to {GENETIC_DIST_FILE}")

print("\nSCRIPT 1: Data simulation and saving complete.")
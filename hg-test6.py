# SCRIPT 6: Plotting PCA of Traits with Different Groupings

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# --- Input Filenames ---
INDIVIDUALS_FILE = 'simulated_individuals.csv'      # From Script 1
TRAITS_FILE = 'simulated_traits.csv'                # From Script 1
CLUSTER_ASSIGNMENTS_FILE = 'hypergraph_cluster_assignments.csv' # From Script 4

# --- Output Plot Filenames ---
PCA_PLOT_TRUE_GROUPS_FILE = 'pca_plot_true_groups.png'
PCA_PLOT_FOUND_CLUSTERS_FILE = 'pca_plot_found_clusters.png'
PCA_PLOT_ENVIRONMENT_FILE = 'pca_plot_environment.png'

# --- Load Data ---
print("SCRIPT 6: Generating PCA plots...")
try:
    individuals_df = pd.read_csv(INDIVIDUALS_FILE)
    traits_df = pd.read_csv(TRAITS_FILE)
    cluster_assignments_df = pd.read_csv(CLUSTER_ASSIGNMENTS_FILE)
    print("Data loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure necessary CSV files are in the correct location.")
    print(f"Required: '{INDIVIDUALS_FILE}', '{TRAITS_FILE}', '{CLUSTER_ASSIGNMENTS_FILE}'.")
    exit()
except Exception as e:
    print(f"An error occurred while loading data: {e}")
    exit()

# --- Merge Data ---
# Merge traits with individual info
merged_df = pd.merge(individuals_df, traits_df, on='individual_id', how='inner')
# Merge with cluster assignments
full_merged_df = pd.merge(merged_df, cluster_assignments_df, on='individual_id', how='inner')

if len(full_merged_df) != len(individuals_df):
    print(f"Warning: Merge resulted in {len(full_merged_df)} rows, but expected {len(individuals_df)}. Check for ID mismatches.")
    if len(full_merged_df) == 0:
        print("Merge failed or resulted in an empty DataFrame. Cannot proceed with plotting.")
        exit()
print(f"Data merged for {len(full_merged_df)} individuals.")

# --- Perform PCA on Trait Data ---
trait_columns = [col for col in traits_df.columns if col.startswith('trait_')]
if not trait_columns:
    print("Error: No trait columns found in traits_df (expected columns starting with 'trait_').")
    exit()

x_traits = full_merged_df[trait_columns].values

# 1. Scale the data
scaler = StandardScaler()
x_scaled = scaler.fit_transform(x_traits)

# 2. Apply PCA
pca = PCA(n_components=2, random_state=42) # Reduce to 2 principal components
principal_components = pca.fit_transform(x_scaled)

pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
# Add the grouping columns for plotting
pca_df['individual_id'] = full_merged_df['individual_id']
pca_df['true_group'] = full_merged_df['true_group']
pca_df['cluster_id'] = full_merged_df['cluster_id'].astype('category') # Treat as category for distinct colors
pca_df['environment'] = full_merged_df['environment']

print(f"\nPCA performed. Explained variance ratio by PC1: {pca.explained_variance_ratio_[0]:.3f}, PC2: {pca.explained_variance_ratio_[1]:.3f}")
print(f"Total variance explained by first 2 PCs: {np.sum(pca.explained_variance_ratio_):.3f}")

# --- Create PCA Plots ---

# Plot 1: Colored by True Group
plt.figure(figsize=(10, 8))
sns.scatterplot(x='PC1', y='PC2', hue='true_group', data=pca_df, palette='viridis', s=70, alpha=0.8)
plt.title('PCA of Traits - Colored by True Group')
plt.xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
plt.ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
plt.legend(title='True Group', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend
plt.savefig(PCA_PLOT_TRUE_GROUPS_FILE)
print(f"\nSaved PCA plot colored by true groups to {PCA_PLOT_TRUE_GROUPS_FILE}")
# plt.show() # Uncomment if you want to display plots interactively

# Plot 2: Colored by Found Cluster ID
plt.figure(figsize=(10, 8))
# Ensure cluster_id is treated as categorical for distinct colors
# Using a qualitative palette suitable for categorical data
num_clusters = len(pca_df['cluster_id'].unique())
palette_clusters = sns.color_palette("Paired", n_colors=num_clusters) if num_clusters <= 12 else sns.color_palette("tab20", n_colors=num_clusters)

sns.scatterplot(x='PC1', y='PC2', hue='cluster_id', data=pca_df, palette=palette_clusters, s=70, alpha=0.8)
plt.title('PCA of Traits - Colored by Found Hypergraph Cluster ID')
plt.xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
plt.ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
plt.legend(title='Found Cluster ID', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig(PCA_PLOT_FOUND_CLUSTERS_FILE)
print(f"Saved PCA plot colored by found clusters to {PCA_PLOT_FOUND_CLUSTERS_FILE}")
# plt.show()

# Plot 3: Colored by Environment
plt.figure(figsize=(10, 8))
sns.scatterplot(x='PC1', y='PC2', hue='environment', data=pca_df, palette='Set2', s=70, alpha=0.8)
plt.title('PCA of Traits - Colored by Environment')
plt.xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
plt.ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
plt.legend(title='Environment', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig(PCA_PLOT_ENVIRONMENT_FILE)
print(f"Saved PCA plot colored by environment to {PCA_PLOT_ENVIRONMENT_FILE}")
# plt.show()

print("\nSCRIPT 6: PCA plotting complete.")
print("Check your current directory for the saved PNG image files.")
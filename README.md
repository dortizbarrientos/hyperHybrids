# hyperHybrids
**Hypergraph Analysis Pipeline for Hybrid Identification **

## Introduction

This repository provides a modular pipeline of Python scripts to demonstrate a hypergraph-based approach for analyzing population structure. It uses the **HyperNetX (HNX)** library to construct, cluster, and visualize hypergraphs.

The primary example focuses on a simulated dataset representing two parent populations, a third distinct population, and a zone of F1 hybrids between two of the parent populations. The analysis primarily uses simulated multi-dimensional trait data, environmental information, and family structures to define relationships (hyperedges) among individuals.

The goal of this pipeline is to:
1.  Illustrate how hypergraphs can capture complex, multi-way relationships beyond simple pairwise similarities.
2.  Provide a step-by-step workflow from data simulation to clustering, evaluation, and visualization.
3.  Offer a template that users can adapt for their own datasets (e.g., real trait data, environmental data, or by incorporating genetic data).
4.  Help demystify the application of hypergraph methods by breaking down the process into manageable, independent scripts.

## Background on Hypergraphs and Hybrid Detection

### What are Hypergraphs?
A hypergraph is a generalization of a graph. In a simple graph, an edge connects a *pair* of nodes (vertices). In contrast, in a hypergraph, a **hyperedge** can connect *any number* of nodes. This fundamental difference allows hypergraphs to model more complex, higher-order, and multi-way relationships that are difficult to represent with traditional graphs.

Formally, as defined in the HyperNetX documentation, a hypergraph can be seen as a tuple of three sets, $H = (V, E, \mathcal{I})$:
* $V$: A set of *nodes* (or vertices), distinguished by unique identifiers. In our case, these are individual organisms.
* $E$: A set of *hyperedges*, also distinguished by unique identifiers. Each hyperedge represents a specific relationship or shared characteristic among a group of nodes.
* $\mathcal{I}$: A set of *incidences*, which are pairs of edge and node identifiers, indicating which nodes belong to which hyperedges.

### Why are Hypergraphs Useful for Hybrid Detection and Population Structure?
Detecting and characterizing hybrids and complex population structures often involves understanding nuanced patterns across multiple data types. Hypergraphs offer several advantages here:

* **Modeling Complex Trait Combinations:** Hybrid individuals frequently exhibit a mosaic of traits from parental populations, or even novel (transgressive) traits. Simple pairwise similarity might not capture this. Hyperedges can be defined to represent groups of individuals that share specific *combinations* of multiple trait values (e.g., high trait A, low trait B, intermediate trait C), which could be uniquely characteristic of certain hybrid classes or introgression patterns.
* **Integrating Diverse Data Types:** Hybridization and population structure are shaped by genetics, phenotype, environment, and behavior. Hypergraphs provide a flexible framework to integrate these diverse data sources. For example, different types of hyperedges can be defined based on:
    * Shared phenotypic profiles (as demonstrated in this pipeline).
    * Genetic similarity or shared ancestry blocks (a powerful future extension for this pipeline).
    * Co-occurrence in specific ecological niches or geographic hybrid zones.
    * Shared family/kinship ties.
* **Capturing Higher-Order Relationships:** The identity of a hybrid, or individuals belonging to a subtle population subgroup, might not be defined by a single distinguishing feature but by a collective pattern across many features that a group of individuals shares. Hypergraphs excel at representing these "group memberships" based on multifaceted criteria. An individual's inclusion in multiple, diverse hyperedges contributes to its overall "hypergraph identity."
* **Identifying Intermediate or Bridging Individuals:** Hybrids, by their nature, often bridge parental groups. In a hypergraph context, they might be identified by their membership in hyperedges characteristic of *both* parental populations, or they might form their own distinct set of hyperedges defined by their unique combination of properties. The successful isolation of the "Hybrid_G1G2" group into its own cluster in Script 5 of this pipeline demonstrates this potential.
* **Beyond Pairwise Similarity:** Many traditional clustering methods rely on pairwise distance or similarity metrics. Hypergraphs allow relationships to be defined based on set theory – specifically, the co-membership of nodes within hyperedges defined by complex, multi-attribute criteria. This can be more powerful for uncovering groups that are not necessarily "globular" or easily separable by pairwise comparisons alone.

By defining hyperedges thoughtfully, based on biological hypotheses, we can create a rich representation of potential relationships, allowing hypergraph clustering algorithms to then identify cohesive groups of individuals that share multiple complex characteristics.

## Pipeline Overview

The pipeline consists of 8 Python scripts, designed to be run sequentially. Each script performs a specific task and (typically) saves its output, which then serves as input for the next script.

* **Script 1: `01_simulate_population_data.py`** 
    * Generates a simulated dataset including individuals, their true group assignments (e.g., Parent1, Parent2, Parent3, Hybrid), family structures, environmental assignments, and multi-dimensional trait data.
    * Introduces complexities like phenotypic plasticity and convergent evolution.
    * Outputs: `simulated_individuals.csv`, `simulated_traits.csv`, `simulated_genetic_distances.csv`.

* **Script 2: `02_define_hyperedges.py`**
    * Loads the simulated data.
    * Defines various types of hyperedges based on traits (k-NN, thresholds), genetic relatedness (k-NN, family IDs), environmental co-occurrence, and combinations of these. This script is highly customizable.
    * Outputs: `simulated_hyperedges.json` (a list of all defined hyperedges).

* **Script 3: `03_build_hypergraph_structure.py`**
    * Loads the list of hyperedges from `simulated_hyperedges.json`.
    * Constructs a `HyperNetX.Hypergraph` object in memory.
    * Extracts and saves the essential structure of this hypergraph (list of nodes and list of hyperedge compositions).
    * Outputs: `hypergraph_structure.json`.

* **Script 4: `04_perform_hypergraph_clustering.py`**
    * Loads `hypergraph_structure.json` and reconstructs the `HyperNetX.Hypergraph` object.
    * Applies a hypergraph clustering algorithm (e.g., Kumar's algorithm from `hypernetx.algorithms.hypergraph_modularity` ).
    * Outputs: `hypergraph_cluster_assignments.csv` (mapping each individual to a found cluster ID).

* **Script 5: `05_evaluate_clustering_results.py`**
    * Loads cluster assignments (from Script 4) and true individual information (from Script 1).
    * Calculates clustering performance metrics (ARI, AMI, Homogeneity, Completeness, V-measure).
    * Generates a contingency table (True Groups vs. Found Clusters).
    * Provides detailed characterization of each found cluster (distribution of true groups, environments, families).
    * Analyzes how special cases (hybrids, convergence, plasticity) were handled by the clustering.
    * Outputs: Primarily console output with evaluation details.

* **Script 6: `06_plot_pca_analysis.py`**
    * Loads trait data, true individual info, and cluster assignments.
    * Performs PCA on the trait data.
    * Generates scatter plots of the first two principal components, with points colored by:
        * True Group
        * Found Cluster ID
        * Environment
    * Outputs: `pca_plot_true_groups.png`, `pca_plot_found_clusters.png`, `pca_plot_environment.png`.

* **Script 7: `07_visualize_hypergraph_euler.py`**
    * Loads `hypergraph_structure.json` and reconstructs the `HyperNetX.Hypergraph` object.
    * Uses `HyperNetX` drawing functions to create a visual representation of the hypergraph (e.g., Euler diagram style with "rubber bands").
    * Attempts to color nodes by their true group.
    * Outputs: `hypergraph_visualization.png`.
    * *Note: Visualizing dense hypergraphs can be challenging. This plot provides one perspective.*

* **Script 8: `08_plot_2section_graph.py`**
    * Loads `hypergraph_structure.json`, true individual info, and cluster assignments.
    * Constructs a 2-section graph (where nodes are individuals, and an edge connects individuals if they share a hyperedge).
    * Uses `NetworkX` to plot this simpler graph, with nodes colored by:
        * True Group
        * Found Cluster ID
    * Outputs: `2section_plot_true_groups.png`, `2section_plot_found_clusters.png`.

## Features of the Simulated Data (Script 1)

The simulation is designed to create a dataset with realistic complexities, allowing for a thorough test of the hypergraph approach:
* **True Groups:** Multiple distinct ancestral groups (G1, G2, G3).
* **Hybrids:** A designated group of F1 hybrids (Hybrid_G1G2).
* **Family Structure:** Small kin groups (families) are defined, with higher genetic similarity within families.
* **Environmental Association:** True groups have preferential (but not exclusive) associations with different environments.
* **Trait Variation:** Traits are influenced by true group, environment, and random noise.
* **Phenotypic Plasticity:** One trait for one group is explicitly made to vary depending on the environment.
* **Convergent Evolution:** One trait for two genetically distinct groups is made to converge when those groups are in a specific shared environment.

## Prerequisites

* Python 3.x (developed with Python 3.9)
* The following Python libraries:
    * `pandas`
    * `numpy`
    * `scikit-learn`
    * `matplotlib`
    * `seaborn`
    * `hypernetx`
    * `python-igraph` (often a dependency for `hypernetx.algorithms.hypergraph_modularity`)
    * `networkx` (used for layouts and 2-section graph plotting)

You can install these using pip:
```bash
python3 -m pip install pandas numpy scikit-learn matplotlib seaborn hypernetx python-igraph networkx

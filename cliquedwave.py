# -*- coding: utf-8 -*-

import dimod
from dwave.system import DWaveSampler, EmbeddingComposite
import networkx as nx

# Define constants based on the given conditions
delta = 3  # Maximum degree of the graph, example value
B = 1.0  # Example constant
A = (delta + 2) * B
C = B  # Ensure that C < A - nB

N = 5  # Number of nodes in the graph
p = 0.5 #probability of edge creation
#edges = [(0, 1), (1, 2), (2, 3), (3, 4)]  # Example edges of the graph
# Define the graph (example)
G = nx.gnp_random_graph(N,p)
edges = list(G.edges)
# Initialize the linear and quadratic coefficients
h = {}
J = {}

# Compute the coefficients for H_A
for i in range(2, N+1):
    h[f'y_{i}'] = 2 * A * (1 - i)
    for j in range(2, N+1):
        if i != j:
            J[(f'y_{i}', f'y_{j}')] = J.get((f'y_{i}', f'y_{j}'), 0) + 2 * A
'''.get method is used to retrieve the current value associated
 with a key in the dictioanry J, and if the key does not exist, it initializes the value to 0.'''

#setting the linear coefficients h for variable x_v
for v in range(N):
    h[f'x_{v}'] = -2 * A * (N - 1)

#setiing the quadratic coefficients J between y_i and x_v variables
for v in range(N):
    for i in range(2, N+1):
        J[(f'y_{i}', f'x_{v}')] = J.get((f'y_{i}', f'x_{v}'), 0) - 2 * A #uses the existing value or initializes it to 0, then substracts 2*A

# Compute the coefficients for H_B
for i in range(2, N+1):
    h[f'y_{i}'] += B * (i / 2)
    for j in range(2, N+1):
        if i != j:
            J[(f'y_{i}', f'y_{j}')] = J.get((f'y_{i}', f'y_{j}'), 0) + B / 4

for v in range(N):
    h[f'x_{v}'] += -B / 2

for u, v in edges:
    J[(f'x_{u}', f'x_{v}')] = J.get((f'x_{u}', f'x_{v}'), 0) - B / 4

# Compute the coefficients for H_C
for v in range(N):
    h[f'x_{v}'] += -C / 2
    '''for each x_v we add the coefficient C/2'''

# Combine coefficients into a BinaryQuadraticModel
bqm = dimod.BinaryQuadraticModel(h, J, 0.0, dimod.SPIN)

# Solve the problem using a D-Wave sampler
sampler = EmbeddingComposite(DWaveSampler())
response = sampler.sample(bqm, num_reads=100)

# Print the results
print(response)

# Decode the result to find the cliques
samples = response.first.sample
clique = [v for v in range(N) if samples[f'x_{v}'] == 1] #extracts the nodes that form the largest clique in this first sample.

print(f"Largest clique found: {clique}")
print(f"Size of the largest clique: {len(clique)}")

# Determine the number of cliques of the same size found
num_cliques = 0
for sample in response.data(['sample']): # iterates through each sample in the response.
    temp_clique = [v for v in range(N) if sample.sample[f'x_{v}'] == 1]
    if len(temp_clique) == len(clique):  #extracts the nodes that form a clique for the current sample.
        num_cliques += 1 

print(f"Number of cliques of the same size: {num_cliques}")

# An implementation of the community detection algorithm in
# "An efficient and principled method for detecting communities in networks"
# Brian Ball, Brian Karrer, M. E. J. Newman. 2011.
# https://arxiv.org/abs/1104.3590

import numpy as np
from collections import OrderedDict

# the algorithm stops if the increase in log-likelihood
# for an iteration is less than this value
epsilon = 1.0

'''
Calculate the log-likelihood of a given community assignment.

Input:
	edge_to_weight: dict from vertex index pair (u, v) to number of edges between u and v
	theta: community probabilities
Output:
	log_likelihood: log-likelihood that this community assignment produced the fixed input graph
'''
def log_likelihood(edge_to_weight, theta):
	left_term = 0
	right_term = 0
	for (i, j), weight in edge_to_weight.items():
		theta_dot = np.dot(theta[i,:], theta[j,:])
		# catch errors
		if theta_dot == 0:
			print('theta_dot is zero for edge ({}, {})'.format(i, j))
			exit()
		left_term += weight * np.log(theta_dot)
		right_term += theta_dot
	return left_term - right_term

'''
Run the community detection algorithm once.

Input:
	edge_to_weight: dict from vertex index pair (u, v) to number of edges between u and v
	   i.e. edge_to_weight[(u, v)] = number of edges between u and v
	vertex_to_neighbors: dict from vertex index to a list of all neighboring vertex indices
	n: number of vertices in the graph
    K: number of communities
    verbose: if true, print additional error messages
Output:
	ll: log-likelihood of returned community assignment
	C: dict from edge to most likely community for that edge
	   i.e. C[(i, j)] = most likely community for edge (i, j)
'''
def ball_karrer_newman_algorithm(edge_to_weight, vertex_to_neighbors, n, K, verbose):
	m = len(edge_to_weight)

	rng = np.random.default_rng()

	# randomly initialize: theta: n * K matrix
	#                      q: (n * n) * K matrix
	theta = np.abs(rng.uniform(size=(n, K)))
	q = np.abs(rng.uniform(size=(m, K)))

	# index of each edge in q
	edge_indices = {(i,j): idx for idx, (i,j) in enumerate(edge_to_weight.keys())}
	edges_in_order = list(edge_to_weight.keys())
	edge_weights_in_order = np.array(list(edge_to_weight.values()))
	
	delta = float('Inf')
	iteration = 0
	ll = log_likelihood(edge_to_weight, theta)
	# iterate until the change in log-likelihood is less than epsilon
	while np.abs(delta) >= epsilon:
		iteration += 1
		print('Iteration {}'.format(iteration))
		# update q
		print('\tUpdating q.')
		for idx, (i, j) in enumerate(edges_in_order):
			denom = np.dot(theta[i,:], theta[j,:])
			if verbose and denom == 0:
				print("Denominator in q is zero: ({}, {})".format(i, j))
			for z in range(K):
				if denom == 0:
					q[idx,z] = 0
				else:
					q[idx,z] = (theta[i, z] * theta[j, z]) / denom
		# update theta
		print('\tUpdating theta.')
		for z in range(K):
			denom = np.sqrt(np.dot(edge_weights_in_order, q[:, z]))
			for i in range(n):
				ends = vertex_to_neighbors[i]
				start_idx = edge_indices[(i, ends[0])]
				end_idx = edge_indices[(i, ends[-1])] + 1
				dot = np.dot(edge_weights_in_order[start_idx:end_idx], q[start_idx:end_idx, z])
				if verbose and dot == 0:
				 	print("theta[{},{}] is zero.".format(i, z))
				theta[i,z] = dot / denom
		
		# calculate how much the log-likelihood has changed
		new_ll = log_likelihood(edge_to_weight, theta)
		delta = new_ll - ll
		ll = new_ll
		print('\tlog_likelihood: {:.8f} ({:.2f} delta)'.format(ll, delta))

	# get community of each edge (i,j) by taking community z with largest q[i,j,z]
	C_list = np.argmax(q, axis=1)
	C = {}
	for idx, (i,j) in enumerate(edges_in_order):
		C[(i,j)] = C_list[idx]
	return ll, C


'''
Runs the community detection algorithm multiple times and returns
the community assignment that achieves the lowest log-likelihood.

Input:
	edge_to_weight: dict from vertex index pair (u, v) to number of edges between u and v
	   i.e. edge_to_weight[(u, v)] = number of edges between u and v
	vertex_to_neighbors: dict from vertex index to a list of all neighboring vertex indices
	n: number of vertices in the graph
    K: number of communities
    num_trials: number of times to run the algorithm
Output:
	C: dict from edge to most likely community for that edge
	   i.e. C[(i, j)] = most likely community for edge (i, j)
'''
def get_communities(edge_to_weight, vertex_to_neighbors, n, K, num_trials, verbose):
	max_ll = float('-Inf')
	best_C = None
	for trial in range(num_trials):
		ll, C = ball_karrer_newman_algorithm(edge_to_weight, vertex_to_neighbors, n, K, verbose)
		if ll > max_ll:
			max_ll = ll
			best_C = C
	print('Max log-likelihood in {} trials: {:.4f}'.format(num_trials, max_ll))
	return best_C





"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Srimithra Bingi
:Version: 1.0
"""

class Bellman(object):

	def __init__(self, init_graph):

		self.graph = init_graph
		self.vertices = len(init_graph)

	def shortest_path(self, start, tolerance = 0):

		"""
		Finds shortets paths and checks for negative cycle.
		"""

		previous = {}
		distance = {}

		for vertex in self.graph:
			distance[vertex] = float('Inf')
			previous[vertex] = None

		distance[start] = 0
		
		for i in range(self.vertices - 1):
			for currency1 in self.graph:
				for currency2 in self.graph[currency1]:
					weight = self.graph[currency1][currency2]['rate']
					if distance[currency1] != float('Inf') and (distance[currency1] + weight + tolerance < distance[currency2] and distance[currency1] + weight - tolerance < distance[currency2]):
						distance[currency2] = distance[currency1] + weight
						previous[currency2] = currency1
						
		
		for currency1 in self.graph:
			for currency2 in self.graph[currency1]:
				weight = self.graph[currency1][currency2]['rate']
				if distance[currency1] != float('Inf') and (distance[currency1] + weight + tolerance < distance[currency2] and distance[currency1] + weight - tolerance < distance[currency2]):
					return distance, previous, (currency1, currency2)
					
		return distance, previous, None

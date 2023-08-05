from django.db import models
from random import random

class GenerativeFeedbackManager(models.Manager):
	"""
	This is a Django Manager that implements the generative
	algorithm for feedback networks described by D. R. White,
	N. Kejzar, C. Tsallis, J. D. Farmer, and S. D. White. in
	"A Generative Model for Feedback Networks.", 2006
	http://www.santafe.edu/~jdf/papers/05-08-034.pdf
	"""
	__decay__ = {}
	def start(self, a):
		"""
		Implementation of eq. 1 for selecting a starting
		node. The argument a, is the parameter alpha.
		"""
		nodes = self.filter()
		count = nodes.count()

		if count == 0:
			return self.create()
		elif count == 1:
			return nodes.get()

		denom = 0.0
		probabilities = []
		for node in nodes:
			probability = node.outdegree() ** a
			probabilities.append(probability)
			denom = denom + probability

		selector = random()
		addition = 0.0
		for i in range(count):
			addition = addition + (probabilities[i] / denom)
			if addition > selector:
				break
		return nodes[i]

	def distance(self, b):
		"""
		Implementation of eq. 2 for assignment of search distance.
		The argument b is the parameter beta.
		"""
		if b in self.__decay__:
			denom = self.__decay__[b]
		else:
			print "Calculating denominator for decay", b
			denom = sum(map(lambda x: x ** -b, range(1, 100000)))
			print "Done:", denom
			self.__decay__[b] = denom

		selector = random()
		addition = 0.0
		distance = 0
		while True:
			distance = distance + 1
			addition = addition + (distance ** -b) / denom
			if addition > selector:
				break
		return distance

	def findpath(self, start, distance, g):
		"""
		Implementation of eq. 3 for finding a path to a node
		with which to create a link, subject to the routing	
		paramater g, which corresponds to gamma.
		"""
		def udegree(nodes):
			"""
			utility function to calculate the unused
			degree
			"""
			unused = 0
			for n in nodes:
				if n not in visited:
					unused = unused + 1
			return unused

		print "Starting at", start
		r = start
		visited = [start]

		for step in range(distance):
			neighbours = []
			probabilities = []
			denom = 0.0
			for l in r.neighbours():
				if l in visited:
					continue
				neighbours.append(l)
				probability = 1 + udegree(l.neighbours()) ** g
				probabilities.append(probability)
				denom = denom + probability
			if not neighbours:
				r = self.create()
				print "Created", r
				break
			selector = random()
			addition = 0.0
			for i in range(len(neighbours)):
				addition = addition + probabilities[i] / denom
				if addition > selector:
					r = neighbours[i]
					print "Selected", r
					break
		print "Found", r
		print

		return r

	def generate(self, a, b, g, N):
		"""
		Entry point for graph generation. Repeats the algorithm
		using parameters (a,b,g) = (alpha, beta, gamma) until 
		the network contains N nodes.
		"""
		while self.count() < N:
			start = self.start(a)
			distance = self.distance(b)
			finish = self.findpath(start, distance, g)
			start.link(finish)


# Python Service Egg: Mathomatic prime numbers generation
#
# -*- coding: utf-8 -*-

import os

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers.primitive import String, Integer, Array
from soaplib.serializers.binary import Attachment

class MathomaticPrimes(SimpleWSGISoapApp):
	def __init__(self):
		SimpleWSGISoapApp.__init__(self)
		self.limit = 10000000

	@soapmethod(Integer, Integer, _returns = Array(Integer))
	def getprimes(self, lowerbound, upperbound):
		if upperbound > self.limit:
			print "Limit boundary to %i" % self.limit
			upperbound = self.limit
		print "calculate primes from %i to %i" % (lowerbound, upperbound)

		primestr = os.popen("matho-primes %i %i" % (lowerbound, upperbound)).read()

		primelines = primestr.split("\n")
		primes = []
		for line in primelines:
			if line:
				primes.append(int(line))

		return primes

if __name__ == "__main__":
	mp = MathomaticPrimes()
	print mp.getprimes(0, 1200)


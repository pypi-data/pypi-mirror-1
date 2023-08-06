#!/usr/bin/env python

import collections
import string
import sys

from stream import *

alphanum = string.letters + string.digits
trans = range(256) >> map(chr) >> map(lambda c: c.lower() if c in alphanum else ' ') >> ''.join

def tokenize(file):
	for line in open(file):
		for word in line.translate(trans).split():
			if len(word) > 5:
				yield word

@Filter
def count(input):
	d = collections.defaultdict(int)
	for word in input:
		d[word] += 1
	for word in sorted(d, key=d.get):
		yield d[word], word

if __name__ == '__main__':
	


#!/usr/bin/env python

import _hidraw

class Info(object):
	def __init__(self, bustype = None, vendor = None, product = None):
		self.bustype = bustype
		self.vendor = vendor
		self.product = product

	def __str__(self):
		return "(:bustype %s :vendor 0x%04X :product 0x%04X)" % (self.bustype, self.vendor, self.product)

	def __repr__(self):
		return "%s.%s(%d, 0x%04X, 0x%04X)" % (self.__class__.__module__, self.__class__.__name__, self.bustype, self.vendor, self.product)

def get_info(FD):
	result = Info()
	result.bustype, result.vendor, result.product = _hidraw.get_info(FD)
	return result

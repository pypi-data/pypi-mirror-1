#!/usr/bin/env python
# coding=utf-8
"""


"""
__docformat__ = "restructuredtext en"

import sys


class DeQueueUnderflowError( Exception ):
	pass


class DeQueue():
	"""
	Implements a simple double-ended queue mechanism.

	Operations available are:

	queue( item )
		Place the item on the end of the queue.
	push( item )
		Place the item on the front of the queue.
	pop
		Remove the first item from the queue and return it.
	unqueue
		Remove the last item from the queue and return it.
	empty?
		Check if there are any items in the queue.

	"""

	def __init__( self, queue=[], stack=[] ):
		"""
		Create a new dequeue and optionally load it with a list of items.

		Parameters
		----------

		queue : *tuple/list*
			A list of items to be queued when the queue is created.
		stack : *tuple/list*
			A list of items to be pushed when the queue is created.

		"""

		self.dequeue = []
		for item in queue:
			self.queue( item )
		for item in stack:
			self.push( item )


	def queue( self, item ):
		"""
		Place an item on the tail of the dequeue.

		Parameters
		----------

		item : *any*
			The item to queue.

		"""

		self.dequeue = self.dequeue + [ item ]


	def push( self, item ):
		"""
		Place an item on the head of the dequeue.

		Parameters
		----------

		item : *any*
			The item to push.

		"""

		self.dequeue = [ item ] + self.dequeue


	def pop( self ):
		"""
		Remove the item from the head of the dequeue and return it.

		Returns
		-------

		any
			The first item from the queue.

		Side-Effects
		------------

		The item is removed from the queue.

		Raises
		------

		DeQueueUnderflow
			Pop was called on an empty dequeue.

		"""

		if not self.isEmpty():
			item, self.dequeue = self.dequeue[0], self.dequeue[1:]
			return item
		else:
			raise DeQueueUnderflowError, "Attempt to pop head of an empty dequeue"


	def unqueue( self ):
		"""
		Remove the item from the tail of the dequeue and return it.

		Returns
		-------

		any
			The last item from the queue.

		Side-Effects
		------------

		The item is removed from the queue.

		Raises
		------

		DeQueueUnderflow
			Unqueue was called on an empty dequeue.

		"""

		if not self.isEmpty():
			item, self.dequeue = self.dequeue[-1], self.dequeue[:-2]
			return item
		else:
			raise DeQueueUnderflowError, "Attempt to unqueue tail of an empty dequeue"


	def isEmpty( self ):
		"""
		Test whether the dequeue contains any items.

		Returns
		-------

		boolean
			True if the dequeue contains no items, False otherwise.

		"""

		return not self.dequeue

## Script (Python) "constructBatch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sequence
##title=construct a batch from a given sequence
##
from Products.CMFPlone import Batch
b_start = context.REQUEST.get('b_start', 0)
batch = Batch(sequence, 100, int(b_start), orphan=0)
return batch

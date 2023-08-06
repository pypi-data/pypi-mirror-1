from Products.ZCTextIndex.PipelineFactory import element_factory
from qi.GRSplitter.GRSplitter import GRSplitter
def initialize(context):
	"""Initializer called when used as a Zope 2 product."""
	try:
		element_factory.registerFactory('Word Splitter',
			  'GR splitter', GRSplitter)
	except ValueError:
		# in case the splitter is already registered, ValueError is raised
		pass
	
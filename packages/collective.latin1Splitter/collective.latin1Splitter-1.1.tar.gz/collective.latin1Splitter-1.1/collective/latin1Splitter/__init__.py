from Products.ZCTextIndex.PipelineFactory import element_factory
from collective.latin1Splitter.latin1_splitter import Latin1Splitter

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    try:
        element_factory.registerFactory('Latin1 Word Splitter', 'Latin1 splitter', Latin1Splitter)
    except ValueError:
        # in case the splitter is already registered, ValueError is raised
        pass

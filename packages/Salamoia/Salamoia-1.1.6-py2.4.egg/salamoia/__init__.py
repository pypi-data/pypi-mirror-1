"""
salamoia
"""

__all__ = []

from protocols import IBasicSequence, declareImplementation
from types import GeneratorType

# monkey path PyProtocols
declareImplementation(GeneratorType, instancesProvide=[IBasicSequence])

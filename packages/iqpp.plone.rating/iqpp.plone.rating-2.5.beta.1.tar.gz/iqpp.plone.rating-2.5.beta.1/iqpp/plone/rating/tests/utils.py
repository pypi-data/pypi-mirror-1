# zope imports 
from zope.component import provideUtility
from zope.interface import implements

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRateable
from iqpp.plone.rating.interfaces import IRatingDefinition
from iqpp.plone.rating.content.definition import RatingDefinition

def createDefinition():
    """
    """
    sc = [("1", "One", 1.0), ("2", "Two", 2.0), ("3", "Three", 3.0), ("4", "Four", 4.0),  ("5", "Five", 5.0),  ("6", "Six", 6.0)]

    score = RatingDefinition(
        title="Score", 
        scores=sc, 
        description="The Score for a Paper")
        
    provideUtility(score, IRatingDefinition, name='score')
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements


ad_unit_sizes =[
  ( (120,240), '120x240', '120x240 - Vertical banner' ),
  ( (120,600), '120x600', '120x600 - Skyscraper' ),
  ( (125,125), '125x125', '125x125 - Button' ),
  ( (160,600), '160x600', '160x600 - Wide skyscraper' ),
  ( (180,150), '180x150', '180x150 - Small rectangle' ),
  ( (200,200), '200x200', '200x200 - Small square' ),
  ( (234,60),  '234x60',  '234x60 - Half banner' ),
  ( (250,250), '250x250', '250x250 - Square' ),
  ( (300,250), '300x250', '300x250 - Medium rectangle' ),
  ( (336,280), '336x280', '336x280 - Large rectangle' ),
  ( (468,60),  '468x60',  '468x60 - Banner' ),
  ( (728,90),  '728x90',  '728x90 - Leaderboard' ),
]

ad_unit_terms = [
    SimpleTerm(value, token, title) for value, token, title in ad_unit_sizes
]


class AdUnitSizesVocabulary(object):
  """ Ad Unit sizes """

  implements(IVocabularyFactory)

  def __call__(self, context):
      return SimpleVocabulary(ad_unit_terms)


AdUnitSizesVocabularyFactory = AdUnitSizesVocabulary()
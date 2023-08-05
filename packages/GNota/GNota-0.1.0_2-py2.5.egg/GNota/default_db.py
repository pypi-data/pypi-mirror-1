from elixir import create_all, metadata, objectstore
from model import *
from controller import GNotaController
import os
import os.path
from datetime import date
from decimal import Decimal
import sys

def _(s):
    return s

try:
    delete = (sys.argv[1] == 'delete')
except IndexError:
    delete = False

gnota_homedir = os.path.join(os.path.expanduser('~'), '.gnota')
dbpath = os.path.join(gnota_homedir, 'gnota.sqlite')
if not delete and os.path.exists(dbpath):
    sys.exit(0)

create_and_connect_to_default_database(delete)

gc = GNotaController()

## Create some scoresystems

pass_ = ScoreSymbolValue(symbol=_(u'Pass'), value=1)
fail  = ScoreSymbolValue(symbol=_(u'Fail'), value=0)

PassFail = DiscreteValuesScoreSystem(
    name=_(u'Pass/Fail'),
    description=_(u'Pass or Fail score system.'),
    scores=[pass_, fail],
    cls='DiscreteValuesScoreSystem',
)

ala = ScoreSymbolValue(symbol=u'A', value=4)
alb = ScoreSymbolValue(symbol=u'B', value=3)
alc = ScoreSymbolValue(symbol=u'C', value=2)
ald = ScoreSymbolValue(symbol=u'D', value=1)
alf = ScoreSymbolValue(symbol=u'F', value=0)

AmericanLetterScoreSystem = DiscreteValuesScoreSystem(
    name=_(u'Letter Grade'), 
    description=_(u'American Letter Grade'),
    scores=[ala, alb, alc, ald, alf],
    cls='DiscreteValuesScoreSystem',
)

ealaplus  = ScoreSymbolValue(symbol=u'A+', value=4)
eala      = ScoreSymbolValue(symbol=u'A', value=4)
ealaminus = ScoreSymbolValue(symbol=u'A-', value=3.7)

ealbplus  = ScoreSymbolValue(symbol=u'B+', value=3.3)
ealb      = ScoreSymbolValue(symbol=u'B', value=3)
ealbminus = ScoreSymbolValue(symbol=u'B-', value=2.7)

ealcplus  = ScoreSymbolValue(symbol=u'C+', value=2.3)
ealc      = ScoreSymbolValue(symbol=u'C', value=2)
ealcminus = ScoreSymbolValue(symbol=u'C-', value=1.7)

ealdplus  = ScoreSymbolValue(symbol=u'D+', value=1.3)
eald      = ScoreSymbolValue(symbol=u'D', value=1)
ealdminus = ScoreSymbolValue(symbol=u'D-', value=0.7)

ealf      = ScoreSymbolValue(symbol=u'F', value=0)


ExtendedAmericanLetterScoreSystem = DiscreteValuesScoreSystem(
    name=_(u'Extended Letter Grade'),
    description=_(u'American Extended Letter Grade'),
    scores = [ealaplus, eala, ealaminus,
              ealbplus, ealb, ealbminus,
              ealcplus, ealc, ealcminus,
              ealdplus, eald, ealdminus,
              ealf ],
    cls='DiscreteValuesScoreSystem',
    )

zero = ScoreSymbolValue(symbol='0', value=0.0)
ten = ScoreSymbolValue(symbol='10', value=10.0)

zeroten = RangedValuesScoreSystem(
     name=_(u'Zero/Ten scoresystem'),
     description=_(u'Zero/Ten ranged scoresystem'),
     min=zero,
     max=ten,
     cls='RangedValuesScoreSystem',
     )

objectstore.flush()
     
five = ScoreSymbolValue(symbol='5', value=5.0, scoresystem=zeroten)


dac = DummyApprovationCriterion(name='Dummy Criterion',
                                passing_score=[eala],
                                cls='DummyApprovationCriterion')

sa = SimpleAverage(name='Simple average (Average C)',
                                passing_score=[ealc],
                                cls='SimpleAverage')

sa_five = SimpleAverage(name='Simple average (Average 5)',
                                passing_score=[five],
                                cls='SimpleAverage')

sa_best_2_five = SimpleAverageOfBestN(name='Simple average of best 2 (Average 5)',
                                passing_score=[five],
                                N=2,
                                cls='SimpleAverageOfBestN')


## Create some ActivityCategories
activity_categories = [_(u'Assignment'),
                   _(u'Essay'),
                   _(u'Exam'),
                   _(u'Homework'),
                   _(u'Journal'),
                   _(u'Lab'),
                   _(u'Presentation'),
                   _(u'Project'),]
                
for ac in activity_categories:
    gc.add_category(name=ac)
    
objectstore.flush()


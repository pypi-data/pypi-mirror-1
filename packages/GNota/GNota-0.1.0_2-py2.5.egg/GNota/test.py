import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.curdir))

from model import *
from controller import GNotaController
from nose import with_setup
from datetime import date

create_and_connect_to_default_database(True)


gc = GNotaController()
    
    
def nop():
    pass

def su():
    metadata.create_all()
    objectstore.flush()

def td():
    for ss in gc.scoresystems:
        AbstractScoreSystem.delete(ss)
    objectstore.flush()
    
    for ssv in ScoreSymbolValue.select():
        ScoreSymbolValue.delete(ssv)
    objectstore.flush()
    
    for crit in gc.criteria:
        ApprovationCriterion.delete(crit)
    objectstore.flush()
    
    for cls in gc.classes:
        Class.delete(cls)
    objectstore.flush()
    
    for s in gc.students:
        Student.delete(s)
    objectstore.flush()    
    
    
    objectstore.flush()
    
    metadata.drop_all()
    objectstore.flush()

if __name__ == '__main__':
    import nose
    assert nose.main()

### Simple tests

@with_setup(su, td)
def test_insert_scoresymbolvalue():    
    s1 = gc.create_scoresymbolvalue(symbol='Symbol 1', value=42)
    s2 = gc.create_scoresymbolvalue(symbol='Symbol 2', value=0)
    objectstore.flush()
    ssv_all = ScoreSymbolValue.select()
    
    assert s1.symbol == 'Symbol 1'
    assert s2.symbol == 'Symbol 2'
    assert s1.value == 42
    assert s2.value == 0
    
    assert len(ssv_all) == 2
    assert s1 in ssv_all
    assert s2 in ssv_all
    

### Complete tests
@with_setup(su, td)                              
def test_american_extended_letter_scoresystem():
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
    
    objectstore.flush()

    ExtendedAmericanLetterScoreSystem = DiscreteValuesScoreSystem(
                              name='Extended Letter Grade',
                              description='American Extended Letter Grade',
                              scores = [ealaplus, eala, ealaminus,
                                        ealbplus, ealb, ealbminus,
                                        ealcplus, ealc, ealcminus,
                                        ealdplus, eald, ealdminus,
                                        ealf ],
                              cls='DiscreteValuesScoreSystem',
                              )
    objectstore.flush()
    
    assert ExtendedAmericanLetterScoreSystem in gc.scoresystems
    assert len(gc.scoresystems) == 1
    



@with_setup(su, td)                              
def test_complete_rangedscoresystem_simpleaverageofbestn():
    
    zero = gc.create_scoresymbolvalue(symbol='0', value=0)
    ten = gc.create_scoresymbolvalue(symbol='10', value=10)
    five = gc.create_scoresymbolvalue(symbol='5', value=5)
    
    zeroten = gc.create_ranged_scoresystem(
                                      name='Zero/Ten scoresystem',
                                      desc='Zero/Ten ranged scoresystem',
                                      min_ssv=zero,
                                      max_ssv=ten,
                                      )
    objectstore.flush()
    
    
    sa_best_2_five = gc.create_simple_average_of_best_N_criterion(
                              name='Simple average of best 2 (Average 5)',
                              min_passing_score=five.symbol,
                              ss=zeroten,
                              N=2,
                              )
            
        
    homework = gc.add_category(name='Homework')
                        
    cls = gc.add_class(name='Arts', course_id='ART-1234', description='Da Vinci\nPicasso\nSalvador Dali\n', website='http://www.foobararts.org', scoresystem=zeroten, criterion=sa_best_2_five)
    
    foo = gc.add_student(first_name='Foo 1', last_name="Quux", code='1', photograph='/home/lameiro/photo-foo.jpg', notes='Foo student', year=2007, phone='(12) 3456-7890')
    gc.add_class_to_student(cls, foo)
    ac = gc.add_activity(name='Arts homework 1', category=homework, activity_class=cls,
              description='Painting', date=date.today(), scoresystem=zeroten)
    gc.add_activity_to_class(ac, cls)
    gc.add_activity_to_student(ac, foo)
    gc.set_student_grade_in_activity(foo, ac, '0')
    
    objectstore.flush()
    
    assert len(foo.classes) == 1
    assert len(foo.activities) == 1
    assert len(foo.grades) == 1
    foo.grades[0].assert_grade_type_matches()
    assert foo.grades[0].score.symbol == '0'
    assert foo.grades[0].score.value == 0
    
@with_setup(su,td)
def test_complete_discretevaluesscoresystem_weightedaverage():
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
      name='Extended Letter Grade',
      description='American Extended Letter Grade',
      scores = [ealaplus, eala, ealaminus,
              ealbplus, ealb, ealbminus,
              ealcplus, ealc, ealcminus,
              ealdplus, eald, ealdminus,
              ealf ],
      cls='DiscreteValuesScoreSystem',
    )
    
    project = gc.add_category(name='Project')
    homework = gc.add_category(name='Homework')
    
    cat_weight1 = CategoryWeight(category=project, weight=2)
    cat_weight2 = CategoryWeight(category=homework, weight=4)
    
    wa = WeightedAverage(name='Weighted Average (C+ average)', cls='WeightedAverage',
                         passing_score=[ealcplus])
    wa.category_weights.append(cat_weight1)
    wa.category_weights.append(cat_weight2)
    objectstore.flush()
    cls = gc.add_class(name='Calculus 1', course_id='MAT-2453', description='Basic Calculus.\nDerivatives.', website='http://www.foobarmath.org', scoresystem=ExtendedAmericanLetterScoreSystem, criterion=wa)
    
    foo = gc.add_student(first_name='Foo 1', last_name="Quux", code='1', photograph='/home/lameiro/photo-foo.jpg', notes='Foo student', year=2007, phone='(12) 3456-7890')
    gc.add_class_to_student(cls, foo)
    
    ac = gc.add_activity(name='Calculus homework 1', category=homework, activity_class=cls,
              description='Foobar', date=date.today(), scoresystem=ExtendedAmericanLetterScoreSystem, weight=1)
    #gc.add_activity_to_class(ac, cls)
    gc.add_activity_to_student(ac, foo)
    gc.set_student_grade_in_activity(foo, ac, 'B')
    
    objectstore.flush()
    
    # Uncomment this print to make the test fail. Yes, a read-only operation will make it fail
    #print cls.activities
    
    ac2 = gc.add_activity(name='Calculus project 1', category=project, activity_class=cls,
          description='Spam', date=date.today(), scoresystem=ExtendedAmericanLetterScoreSystem, weight=15)
    #gc.add_activity_to_class(ac2, cls)
    gc.add_activity_to_student(ac2, foo)
    gc.set_student_grade_in_activity(foo, ac2, 'F')
    
    objectstore.flush()
    
    assert len(foo.classes) == 1
    assert len(foo.activities) == 2
    assert len(cls.activities) == 2
    assert len(foo.grades) == 2
    foo.grades[0].assert_grade_type_matches()
    assert gc.get_student_overall_score_on_class(foo, cls).symbol == 'C'
    
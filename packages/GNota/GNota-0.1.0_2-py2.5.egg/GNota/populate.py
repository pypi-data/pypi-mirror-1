from elixir import create_all, metadata, objectstore
from model import *
from controller import GNotaController
import os
import os.path
from datetime import date
from decimal import Decimal

def _(s):
    return s

#os.chdir(os.path.dirname(os.path.abspath(__file__)))

create_and_connect_to_default_database(delete=True)

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
seven_point_five = ScoreSymbolValue(symbol='7.5', value=7.5, scoresystem=zeroten)


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
    
project = ActivityCategory.select()[-1]
homework = ActivityCategory.select()[-5]

cat_weight1 = CategoryWeight(category=project, weight=1)
cat_weight2 = CategoryWeight(category=homework, weight=2)
    
wa = WeightedAverage(name='Weighted Average (C+ average)',
                     cls='WeightedAverage',
                     passing_score=[ealcplus])
wa.category_weights.append(cat_weight1)
wa.category_weights.append(cat_weight2)
wa.use_missed_classes = True
wa.maximum_missed_classes = 4

objectstore.flush()

## Create some classes
phys = Class(name='Introduction to Physics', course_id='PHY-0123', description='Basic Physics.\nNewton\'s law.', website='http://www.foobarphysics.org', scoresystem=ExtendedAmericanLetterScoreSystem, criterion=wa)
calculus = Class(name='Calculus 1', course_id='MAT-2453', description='Basic Calculus.\nDerivatives.', website='http://www.foobarmath.org', scoresystem=ExtendedAmericanLetterScoreSystem, criterion=sa)
arts = Class(name='Arts', course_id='ART-1234', description='Da Vinci\nPicasso\nSalvador Dali\n', website='http://www.foobararts.org', scoresystem=zeroten, criterion=sa_best_2_five)

objectstore.flush()

## Create some students
foo = Student(first_name='John', last_name='Foo', code='4895031', photograph='/home/lameiro/photo-foo.bmp', notes='Foo student', year=2007, phone='(12) 3456-7890')
bar = Student(first_name='Mary', last_name='Bar', code='9999999', photograph='/home/lameiro/photo-bar.bmp', notes='Bar student', year=2005, phone='(00) 0000-0000')
baz = Student(first_name='Richard', last_name='Baz', code='42', photograph='/home/lameiro/photo-baz.bmp', notes='Baz student', year=1991, phone='(00) 0000-0000')

print 'Creating students'

for i in range(18):
    Student(first_name='Foo %d' % i, last_name="Quux", code=str(i), photograph='/home/lameiro/photo-foo.jpg', notes='Foo student', year=2007, phone='(12) 3456-7890')

print "Flushing"
objectstore.flush()
print "Done"
    

## Add some students to some classes

#student.classes.add(class)
foo.classes.append(phys)
foo.classes.append(calculus)
foo.classes.append(arts)

# or class.students.add(student)!
phys.students.append(bar)
arts.students.append(baz)

# add the rest of students to physics
for s in Student.select():
    s.classes.append(phys)


## Let's do some physics homework now.
activity_names=[_(u'Homework 1'),
                _(u'Homework 2'),
                _(u'Homework 3'),
                ]
                
for an in activity_names:
    a = Activity(name=an, category=homework, activity_class=phys,
                description='A simple homework', date=date.today(), scoresystem=PassFail)
    foo.activities.append(a)

# Flush...
objectstore.flush()

# Now, i will grade the student

for ac in foo.activities:
    ac.grade = g = Grade()
    g.activity = ac
    g.student = foo
    g.score = pass_
    pass_.grades.append(g) #TODO: Shouldnt need that. But wont work without.
    g.assert_grade_type_matches()
    ac.weight = 1
objectstore.flush()


### Calculus homework

ac = Activity(name='Calculus homework 1', category=homework, activity_class=calculus,
              description='Integrals', date=date.today(), scoresystem=AmericanLetterScoreSystem)

ac.grade = g = Grade()
g.activity = ac
g.student = foo
foo.grades.append(g) #TODO: Shouldnt need that. But wont work without.
g.score = alb
alb.grades.append(g)
g.assert_grade_type_matches()
foo.activities.append(ac)
objectstore.flush()

ac = Activity(name='Calculus homework 2', category=homework, activity_class=calculus,
              description='Taylor series', date=date.today(), scoresystem=AmericanLetterScoreSystem)

ac.grade = g = Grade()
g.activity = ac
g.student = foo
foo.grades.append(g) #TODO: Shouldnt need that. But wont work without.
g.score = alc
alc.grades.append(g)
g.assert_grade_type_matches()
foo.activities.append(ac)

objectstore.flush()



### Arts homework

ac = Activity(name='Arts homework 1', category=homework, activity_class=arts,
              description='Painting', date=date.today(), scoresystem=zeroten)

ac.grade = g = Grade()
g.activity = ac
g.student = foo
foo.grades.append(g) #TODO: Shouldnt need that. But wont work without.
g.score = five
five.grades.append(g)
g.assert_grade_type_matches()
foo.activities.append(ac)

objectstore.flush()

ac = Activity(name='Arts homework 2', category=homework, activity_class=arts,
              description='Sculpture', date=date.today(), scoresystem=zeroten)

ac.grade = g = Grade()
g.activity = ac
g.student = foo
foo.grades.append(g) #TODO: Shouldnt need that. But wont work without.
g.score = seven_point_five
seven_point_five.grades.append(g)
g.assert_grade_type_matches()
foo.activities.append(ac)

objectstore.flush()

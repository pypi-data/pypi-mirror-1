from elixir import *
from gnota_exceptions import *
import os
import sqlalchemy
import sqlalchemy.exceptions

try:
    sqlalchemy.__version__
    typechecks_declaration_needed = True
except AttributeError:
    typechecks_declaration_needed = False
    

def create_and_connect_to_default_database(delete=False):
    gnota_homedir = os.path.join(os.path.expanduser('~'), '.gnota')
    if not os.path.exists(gnota_homedir):
        os.makedirs(gnota_homedir)
    
    dbpath = os.path.join(gnota_homedir, 'gnota.sqlite')
    
    if delete and os.path.exists(dbpath):
        print "Deleting old ~/.gnota/gnota.sqlite database"
        os.remove(dbpath)
    
    connect(dbpath)
    return dbpath

def connect(dbpath, force_create=False):
    #metadata.connect("postgres://user:pass@host:5432/db")
    #os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        engine = create_engine('sqlite:///' + dbpath)

        # create MetaData 
        meta = MetaData()

        # bind to an engine
        meta.bind = engine
    except:
        metadata.connect("sqlite:///" + dbpath)
        meta = metadata
    
    if not os.path.exists(dbpath) or force_create:
        meta.create_all()
    
    #metadata.engine.echo = True


### TODO: Move all the logic to the controller
def get_all_subclassed_scoresystems():
    result = []
    for x in globals().itervalues():
        try:
            if AbstractScoreSystem in x.__mro__:
                for ss in x.select():
                    if ss.cls == ss.__class__.__name__:
                        result.append(ss)
        except:
            pass
    
    return result


def get_subclassed_scoresystem(ss):
    for subclassed_ss in get_all_subclassed_scoresystems():
        if ss.id == subclassed_ss.id:
            return subclassed_ss
    raise GNotaException('Huhn?! Couldnt find subclassed scoresystem')

class GNotaConfig(Entity):
    has_field('runs_since_last_backup', Integer)
    has_field('max_runs_since_last_backup', Integer)
    has_field('dontask_for_gradebook_backups', Boolean) # Maybe I should use GConf for this...

class Grade(Entity):
    belongs_to('activity', of_kind='Activity', inverse='grades')
    belongs_to('student', of_kind='Student', inverse='grades')
    belongs_to('overall_grade_of_class', of_kind='Class', inverse='overall_grades')
    belongs_to('score', of_kind='ScoreSymbolValue', inverse='grades') #TODO: Inverted relation to make Elixir happy.
    has_field('missed_classes', Integer)
    
    def assert_grade_type_matches(self):
        if self.activity is not None:
            assert self.score.scoresystem.id == self.activity.scoresystem.id # Subclassing problems...
        elif self.overall_grades_of_class is not None:
            assert self.score.scoresystem.id == self.overall_grades_of_class.scoresystem.id # Subclassing problems...
        else:
            raise GNotaDatabaseInconsistencyException('activity or class must be non-null')
    
class ActivityCategory(Entity):
    has_field('name', Unicode)
    has_many('activities', of_kind='Activity', inverse='category')
    has_many('weights', of_kind='CategoryWeight', inverse='category')
    
    def __repr__(self):
        return '<ActivityCategory name: %s>' % self.name

class Activity(Entity):
    has_field('name', Unicode)
    has_field('description', Unicode)
    has_field('weight', Float)
    belongs_to('category', of_kind='ActivityCategory', inverse='activities')
    belongs_to('activity_class', of_kind='Class', inverse='activities')
    has_and_belongs_to_many('students', of_kind='Student', inverse='activities')
    has_many('grades', of_kind='Grade', inverse='activity')
    
    if typechecks_declaration_needed:
        belongs_to('scoresystem', of_kind='AbstractScoreSystem', inverse='activities', enable_typechecks=False)
    else:
        belongs_to('scoresystem', of_kind='AbstractScoreSystem', inverse='activities')
    
    has_field('date', Date)
    
    def __repr__(self):
        return '<Activity name: %s category: %s date: %s>' % (self.name, self.category, self.date)

class Student(Entity):
    has_field('first_name', Unicode)
    has_field('last_name', Unicode)
    has_field('code', Unicode)
    has_field('photograph', Unicode)
    has_field('notes', Unicode)
    has_field('year', Integer)
    has_field('phone', String)
    has_and_belongs_to_many('classes', of_kind='Class', inverse='students')
    has_and_belongs_to_many('activities', of_kind='Activity', inverse='students')
    has_many('grades', of_kind='Grade', inverse='student')
    
    @property
    def name(self):
        return "%s, %s" % (self.last_name, self.first_name) 
    
    def __repr__(self):
        return '<Student name: %s code: %s>' % (self.name, self.code)

class Class(Entity):
    has_field('name', Unicode)
    has_field('course_id', Unicode)
    has_field('description', Unicode)
    has_field('website', Unicode)
    has_and_belongs_to_many('students', of_kind='Student', inverse='classes')
    has_many('activities', of_kind='Activity', inverse='activity_class')
    has_many('overall_grades', of_kind='Grade', inverse='overall_grade_of_class')
    if typechecks_declaration_needed:
        belongs_to('criterion', of_kind='ApprovationCriterion', inverse='classes', enable_typechecks=False) #TODO: While elixir doesnt support poly inheritance...
        belongs_to('scoresystem', of_kind='AbstractScoreSystem', inverse='classes', enable_typechecks=False)
    else:
        belongs_to('criterion', of_kind='ApprovationCriterion', inverse='classes') #TODO: While elixir doesnt support poly inheritance...
        belongs_to('scoresystem', of_kind='AbstractScoreSystem', inverse='classes')
    
    
    def __repr__(self):
        return '<Class name: %s course_id: %s>' % (self.name, self.course_id)


#### Scoresystems

class ScoreSymbolValue(Entity):
    has_field('symbol', Unicode)
    has_field('value', Float) #Decimal here and Python decimal.Decimal didnt work. File bug report with SQLAlchemy or SQLite
    if typechecks_declaration_needed:
        belongs_to('scoresystem', of_kind='AbstractScoreSystem', inverse='scores', enable_typechecks=False)
    else:
        belongs_to('scoresystem', of_kind='AbstractScoreSystem', inverse='scores')
    
    belongs_to('min_of_scoresystem', of_kind='AbstractScoreSystem', inverse='min')
    belongs_to('max_of_scoresystem', of_kind='AbstractScoreSystem', inverse='max')
    
    if typechecks_declaration_needed:
        has_and_belongs_to_many('approvation_criteria', of_kind='ApprovationCriterion', inverse='passing_score', enable_typechecks=False)  # to make Elixir happy
    else:
        has_and_belongs_to_many('approvation_criteria', of_kind='ApprovationCriterion', inverse='passing_score')  # to make Elixir happy

    has_many('grades', of_kind='Grade', inverse='score')
    
    def __str__(self):
        return self.symbol
    
    def __ge__(self, other):
        if type(other) != type(self):
            return NotImplemented
        else:
            #assert self.scoresystem == other.scoresystem
            return self.value >= other.value
    
class AbstractScoreSystem(Entity):
    has_field('name', Unicode)
    has_field('description', Unicode)
    has_field('cls', Unicode)  #TODO: Remove this Workaround when elixir supports polymorphic inheritance
    has_one('min', of_kind='ScoreSymbolValue', inverse='min_of_scoresystem')
    has_one('max', of_kind='ScoreSymbolValue', inverse='max_of_scoresystem')
    has_many('activities', of_kind='Activity', inverse='scoresystem')
    has_many('classes', of_kind='Class', inverse='scoresystem')
    has_many('scores', of_kind='ScoreSymbolValue', inverse='scoresystem')
    

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

class AbstractValuesScoreSystem(AbstractScoreSystem):
    def getFractionalValue(self, score):
        # get maximum and minimum score to determine the range
        if self.max is None:
            maximum = self.getNumericalValue(self.scores[0])
            minimum = self.getNumericalValue(self.scores[-1])
        else:
            maximum = self.getNumericalValue(self.max)
            minimum = self.getNumericalValue(self.min)
        # normalized numerical score
        value = self.getNumericalValue(score) - minimum
        return (value*1.0) / (maximum - minimum)
    
    def getNumericalValue(self, score):
        return score.value

class DiscreteValuesScoreSystem(AbstractValuesScoreSystem):
    """Discrete Values Score System"""

    def isValidSymbol(self, score):
        return symbol in [score.symbol for score in self.scores]

    def fromFractionalValue(self, frac):
        l = [self.getFractionalValue(score) for score in self.scores]
        
        if frac in l:
            return self.scores[l.index(frac)]
        else:
            l.append(frac)
            l = list(reversed(sorted(l)))
            frac_down_index = l.index(frac) + 1
            frac_up_index = l.index(frac) - 1

            if frac_up_index < 0:
                return self.scores[0]
            
            frac_down = l[frac_down_index]
            frac_up = l[frac_up_index]
                
            score_up = self.scores[frac_up_index]
            score_down = self.scores[frac_down_index-1] # frac was not appended to self.scores
            
            if frac >= (frac_up + frac_down)/2.0:
                return score_up
            else:
                return score_down
        
class RangedValuesScoreSystem(AbstractValuesScoreSystem):
    def isValidSymbol(self, symbol):
        return self.getNumericalValue(self.min) <= float(symbol) <= self.getNumericalValue(self.max)
            
    def fromFractionalValue(self, frac):
        ssv = ScoreSymbolValue(scoresystem=self)
        value = frac * (self.getNumericalValue(self.max) - self.getNumericalValue(self.min))
        ssv.symbol = str(float(value))
        ssv.value = float(value)
        objectstore.flush()
        return ssv
    
#### Approvation Criteria

class ApprovationCriterion(Entity):
    has_field('name', Unicode)
    has_field('description', Unicode)
    has_field('cls', Unicode) #TODO: Remove this Workaround when elixir supports polymorphic inheritance
    has_and_belongs_to_many('passing_score', of_kind='ScoreSymbolValue', inverse='approvation_criteria') # Has one, but Elixir wont let me do. Dont know why!!
    has_many('classes', of_kind='Class', inverse='criterion')
    has_field('maximum_missed_classes', Integer)
    has_field('use_missed_classes', Boolean)
    
    def is_passing_score(self, score):
        assert self.is_valid_score(score)
        return score >= self.passing_score[0]
    
    def is_valid_score(self, score):
        return type(score) == type(self.passing_score[0])
    
    def calculate_final_score(self, grades, ss):
        raise NotImplementedError
    
    def is_passing_missed_classes(self, cm):
        if self.use_missed_classes:
            return cm <= self.maximum_missed_classes
        else:
            return True
    
class DummyApprovationCriterion(ApprovationCriterion):
    def is_passing_score(self, score):
        return True
    
    def calculate_final_score(self, grades, ss):
        return self.passing_score[0]

class SimpleAverage(ApprovationCriterion):
    def calculate_final_score(self, grades, ss):
        result = 0
        for grade in grades:
            grade_ss = get_subclassed_scoresystem(grade.score.scoresystem)
            result += grade_ss.getFractionalValue(grade.score)
        
        n = len(grades)
        if n != 0:
            result = (result * 1.0)/n
        else:
            result = 0
        return ss.fromFractionalValue(result)    

class SimpleAverageOfBestN(ApprovationCriterion):
    has_field('N', Integer)
    
    def calculate_final_score(self, grades, ss):
        result = []
        for grade in grades:
            grade_ss = get_subclassed_scoresystem(grade.score.scoresystem)
            result.append(grade_ss.getFractionalValue(grade.score))
        
        result = list(reversed(sorted(result)))[:self.N]
        
        result = sum(result)
        
        result = (result * 1.0)/self.N
        return ss.fromFractionalValue(result)

class CategoryWeight(Entity):
    belongs_to('category', of_kind='ActivityCategory', inverse='weight')
    has_field('weight', Float)
    belongs_to('weighted_average', of_kind='WeightedAverage', inverse='category_weights')


class WeightedAverage(ApprovationCriterion):
    has_many('category_weights', of_kind='CategoryWeight', inverse='weighted_average')
    
    def calculate_final_score(self, grades, class_ss):
        result = 0
        cat_weight_sum = 0
        for cw in self.category_weights:
            cat = cw.category
            cat_grades = [grade for grade in grades if grade.activity.category == cat]
            cat_weight = cw.weight
            cat_result = 0
            weight_sum = 0
            for grade in cat_grades:
                weight = grade.activity.weight
                weight_sum += weight
                ss = grade.activity.scoresystem
                ss = get_subclassed_scoresystem(ss)
                cat_result += ss.getFractionalValue(grade.score)*weight
            if weight_sum != 0:
                cat_result = (cat_result * 1.0)/weight_sum
            else:
                cat_result = 0
            result += cat_result * cat_weight
            cat_weight_sum += cat_weight
        result = (result * 1.0)/cat_weight_sum
        
        return class_ss.fromFractionalValue(result)
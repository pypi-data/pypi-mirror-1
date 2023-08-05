from model import *
from gnota_exceptions import *

import csv
import datetime
import tempfile
import shutil
import os

class GNotaController(object):
    def __init__(self):
        self.observer_list = []
        self.scoresystems_observer_list = []
        self.criteria_observer_list = []
        self.categories_observer_list = []
        self.classes_observer_list = []
        
        self.real_dbpath = None
        self.work_dbpath = None
        
        self.saved = False
    
    ### Notification code
    def add_observer(self, observer):
        self.observer_list.append(observer)
    
    def remove_observer(self, observer):
        self.observer_list.remove(observer)
    
    
    def add_scoresystems_observer(self, ob):
        self.scoresystems_observer_list.append(ob)
        
    def remove_scoresystems_observer(self, observer):
        self.scoresystems_observer_list.remove(observer)
    
    
    def add_criteria_observer(self, ob):
        self.criteria_observer_list.append(ob)
        
    def remove_criteria_observer(self, observer):
        self.criteria_observer_list.remove(observer)
    
    
    def add_categories_observer(self, ob):
        self.categories_observer_list.append(ob)
        
    def remove_categories_observer(self, observer):
        self.categories_observer_list.remove(observer)
        
    def add_classes_observer(self, observer):
        self.classes_observer_list.append(observer)
        
    def remove_classes_observer(self, observer):
        self.classes_observer_list.remove(observer)
        
    
    
    # Notification
    def notify_observers(self):
        for observer in self.observer_list:
            observer.notify_model_changed()
    
    def notify_criteria_observers(self):
        for observer in self.criteria_observer_list:
            observer.notify_criteria_model_changed()
    
    def notify_categories_observers(self):
        for observer in self.categories_observer_list:
            observer.notify_categories_model_changed()
    
    def notify_scoresystems_observers(self):
        for observer in self.scoresystems_observer_list:
            observer.notify_scoresystems_model_changed()
    
    def notify_classes_observers(self):
        for observer in self.classes_observer_list:
            observer.notify_classes_model_changed()
            

    @property
    def activity_categories(self):
        return ActivityCategory.select()
        
    @property
    def students(self):
        return Student.select()
    
    @property
    def classes(self):
        return Class.select()
    
    @property
    def scoresystems(self):
        #TODO: Eliminate this workaround when Elixir provides polymorphic inheritance
        #return AbstractScoreSystem.select()
        result = []
        import model
        for x in model.__dict__.itervalues():
            try:
                if AbstractScoreSystem in x.__mro__:
                    for ss in x.select():
                        if ss.cls == ss.__class__.__name__:
                            result.append(ss)
            except:
                pass
        
        return result
    
    @property
    def criteria(self):
        #TODO: Eliminate this workaround when Elixir provides polymorphic inheritance
        #return ApprovationCriterion.select()
        result = []
        import model
        for x in model.__dict__.itervalues():
            try:
                if ApprovationCriterion in x.__mro__:
                    for crit in x.select():
                        if crit.cls == crit.__class__.__name__:
                            result.append(crit)
            except:
                pass
        
        return result
    
    def get_subclassed_criterion(self, crit):
        for subclassed_criterion in self.criteria:
            if crit.id == subclassed_criterion.id:
                return subclassed_criterion
        raise GNotaException('Huhn?! Couldnt find subclassed criterion')
    
    def get_subclassed_scoresystem(self, ss):
        for subclassed_ss in self.scoresystems:
            if ss.id == subclassed_ss.id:
                return subclassed_ss
        raise GNotaException('Huhn?! Couldnt find subclassed scoresystem')


    def set_real_dbpath(self, dbpath):
        self.real_dbpath = dbpath

    def get_real_dbpath(self):
        return self.real_dbpath
    
    def set_work_dbpath(self, dbpath):
        self.work_dbpath = dbpath

    def get_work_dbpath(self):
        return self.work_dbpath
    
    def flush_and_set_dirty(self):
        objectstore.flush()
        self.set_dirty()

    
    def add_category(self, name):
        cat = ActivityCategory(name=name)
        print "[Controller] - Adding category name = %s" % cat.name
        objectstore.flush()
        self.set_dirty()
        self.notify_categories_observers()
        return cat
    
    def remove_category(self, cat):
        print "[Controller] - Removing category name = %s" % cat.name
        ActivityCategory.delete(cat)
        objectstore.flush()
        self.set_dirty()
        self.notify_categories_observers()
    
    def set_category_name(self, cat, name):
        print "[Controller] - Setting category name = %s to new name = %s" % (cat.name, name)
        cat.name = name
        objectstore.flush()
        self.set_dirty()
        self.notify_categories_observers()
        
    
    def add_student(self, **kwargs):
        s = Student(**kwargs)
        print "[Controller] - Adding student name = %s" % s.name
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        return s
    
    def remove_student(self, s):
        print "[Controller] - Removing student name = %s" % s.name
        Student.delete(s)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
            
    
    def get_students_like(self, first_name='', last_name='', code='', year=''):
        like_clause_first_name = Student.c.first_name.like("%%%s%%" % first_name)
        like_clause_last_name = Student.c.last_name.like("%%%s%%" % last_name)
        like_clause_code = Student.c.code.like("%%%s%%" % code)
        like_clause_year = Student.c.year.like("%%%s%%" % year)
        
        return Student.select( like_clause_first_name & like_clause_last_name & like_clause_code & like_clause_year )
    
    def get_classes_like(self, name='', course_id='', description='', website='', student=None):
        like_clause_name = Class.c.name.like("%%%s%%" % name)
        like_clause_course_id = Class.c.course_id.like("%%%s%%" % course_id)
        like_clause_description = Class.c.description.like("%%%s%%" % description)
        like_clause_website = Class.c.website.like("%%%s%%" % website)
        
        classes = Class.select( like_clause_name & like_clause_course_id & like_clause_description & like_clause_website)
        if student is None:
            return classes
        else:
            # TODO: Ugly ugly ugly! Use SQLAlchemy instead!!
            return [c for c in classes if student in c.students]        
    
    def add_class(self, **kwargs):
        cls = Class(**kwargs)
        print "[Controller] - Adding class name = %s" % cls.name
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
        return cls 
    
    def remove_class(self, cls):
        print "[Controller] - Removing class name = %s from database" % cls.name
        Class.delete(cls)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
    
    def add_class_to_student(self, cls, student):
        print "[Controller] - Adding class name = %s to student %s" % (cls.name, student.name)
        student.classes.append(cls)
        cls.students.append(student)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
    
    def remove_class_from_student(self, cls, student):
        print "[Controller] - Removing class name = %s from student %s" % (cls.name, student.name)
        student.classes.remove(cls)
        cls.students.remove(student) # TODO: Shouldnt need that. But wont work without. Maybe elixir fault, dont know...
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
    
    def modify_class(self, cls, **kwargs):
        for k,v in kwargs.items():
            cls.__setattr__(k, v)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
        
    def modify_activity(self, ac, **kwargs):
        for k,v in kwargs.items():
            ac.__setattr__(k, v)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        
    def modify_student(self, s, **kwargs):
        for k,v in kwargs.items():
            s.__setattr__(k, v)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
    
    def create_scoresymbolvalue(self, symbol, value):
        print "[Controller] - Creating scoresymbolvalue symbol = %s value = %s" % (symbol, value)
        try:
            ssv = ScoreSymbolValue(symbol=symbol, value=float(value))
        except ValueError:
            raise GNotaConversionException('value %s cannot be converted to float' % value)
        
        return ssv
    
    def remove_scoresymbolvalue(self, ssv):
        print "[Controller] - Removing scoresymbolvalue symbol = %s value = %s" % (ssv.symbol, ssv.value)
        ScoreSymbolValue.delete(ssv)
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
    
    def create_ranged_scoresymbolvalue(self, symbol, ranged_ss):
        print "[Controller] - Creating scoresymbolvalue = %s in scoresystem %s" % (symbol, ranged_ss.name)
        try:
            ssv = ScoreSymbolValue(symbol=symbol, value=float(symbol), scoresystem=ranged_ss)
            objectstore.flush()
            self.set_dirty()
            return ssv
        except ValueError:
            raise GNotaException('Could not convert symbol %s to a number.' % symbol)
    
    def get_scoresymbolvalue(self, symbol, scoresystem):
        ss = self.get_subclassed_scoresystem(scoresystem)
        try:
            return ScoreSymbolValue.select_by(symbol=symbol, scoresystem=ss)[0]
        except IndexError:
            if isinstance(ss, RangedValuesScoreSystem):
                return self.create_ranged_scoresymbolvalue(symbol, ss)
            else:
                raise GNotaException('No such symbol in scoresystem')
    
    def get_student_grade_in_activity(self, student, activity):
        try:
            return Grade.select_by(student=student, activity=activity)[0]
        except IndexError:
            raise NoSuchGradeException()
        #Maybe get_by?
    
    def set_student_grade_in_activity(self, student, activity, text):
        print '[Controller] - Setting student grade in activity'
        try:
            grade = self.get_student_grade_in_activity(student, activity)
        except NoSuchGradeException:
            grade = Grade(activity=activity, student=student)
            student.grades.append(grade)
            activity.grades.append(grade)
            objectstore.flush()
            self.set_dirty()
        grade.score = self.get_scoresymbolvalue(text, activity.scoresystem)
        self._calculate_student_average_grade_on_class(student, activity.activity_class)
        objectstore.flush()
        self.set_dirty()
    
    def _get_student_grades_in_class(self, student, cls):
        #TODO: Use SQLAlchemy instead!
        return [grade for grade in Grade.select_by(student=student) if ((grade.activity is not None) and (grade.activity.activity_class == cls))]
    
    def _fetch_student_overall_grade_in_class(self, student, cls):
        try:
            return Grade.select_by(student=student, overall_grade_of_class=cls)[0]
        except IndexError:
            raise NoSuchGradeException
        
    def _calculate_student_average_grade_on_class(self, student, cls):
        try:
            g = self._fetch_student_overall_grade_in_class(student, cls)
        except NoSuchGradeException:
            g = Grade(student=student, overall_grade_of_class=cls)
            cls.overall_grades.append(g)
            objectstore.flush()
            self.set_dirty()
        
        grades = self._get_student_grades_in_class(student, cls)
        criterion = self.get_subclassed_criterion( cls.criterion ) #TODO: Remove workaround when elixir supports polymorphic inheritance
        
        ss = self.get_subclassed_scoresystem(cls.scoresystem)
        
        score = criterion.calculate_final_score(grades, ss)
        g.score = score
        g.missed_classes = 0
        score.grades.append(g) # Shouldnt need that
        
        g.overall_grade_of_class = cls
        objectstore.flush()
        self.set_dirty()
        return g

    def get_student_average_grade_on_class(self, student, cls):
        try:
            result = self._fetch_student_overall_grade_in_class(student, cls)
        except NoSuchGradeException:
            result = self._calculate_student_average_grade_on_class(student, cls)
        
        return result
    
    def get_students_in_class_orderby(self, cls):
        from sqlalchemy import select
        result = []
        s = select([Student.c.id])
        s.order_by(Student.c.last_name)
        result = []
        for result_tuple in s.execute().fetchall():
            s = Student.get_by(id = result_tuple[0])
            if cls in s.classes:
                result.append(s)
        return result
            
        
    
    def get_student_overall_score_on_class(self, student, cls):
        return self.get_student_average_grade_on_class(student, cls).score
    
    def is_passing_score(self, score, cls):
        criterion = self.get_subclassed_criterion( cls.criterion ) #TODO: Remove workaround when elixir supports polymorphic inheritance
        return criterion.is_passing_score(score)
    
    def get_activities_like_in_class(self, cls, name=''):
        like_clause_name = Activity.c.name.like("%%%s%%" % name)
        in_class_clause = Activity.c.activity_class_id == cls.id
        #like_clause_description = Class.c.description.like("%%%s%%" % description)
        #TODO: More searchable fields
        return Activity.select( like_clause_name & in_class_clause)

    def add_activity(self, **kwargs):
        ac = Activity(**kwargs)
        if ac.activity_class is not None:
            ac.activity_class.activities.append(ac)
        print "[Controller] - Adding activity name = %s" % ac.name
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
        return ac
        
    def add_activity_to_class(self, ac, cls):
        ac.activity_class = cls
        objectstore.flush()
        self.set_dirty()
        #print cls.activities
        self.notify_observers()
        self.notify_classes_observers()
    
    def add_activity_to_student(self, activity, student):
        print "[Controller] - Adding activity name = %s to student name %s" % (activity.name, student.name)
        student.activities.append(activity)
        activity.students.append(student) # Shouldn't need. But wont work without

        objectstore.flush()
        self.set_dirty()
        self.notify_observers()

    def remove_activity(self, ac):
        print "[Controller] - Removing activity name = %s" % ac.name
        ac.activity_class.activities.remove(ac) # Shouldn't need. But wont work without
        ac.delete()
        objectstore.flush()
        self.set_dirty()
        self.notify_observers()
        self.notify_classes_observers()
    
    ### Weighted average
    
    def add_category_weight(self, cat, weight):
        print "[Controller] - Created category weight = %d to category %s" % (weight, cat)
        cw = CategoryWeight(category=cat, weight=float(weight))
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
        return cw
    
    def add_category_weight_to_criterion(self, wa, cw):
        print "[Controller] - Adding category weight = %s to criterion %s" % (cw, wa)
        wa.category_weights.append(cw)
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
    
    def set_category_weight(self, cw, weight):
        print "[Controller] - Setting weight = %d to category %s" % (weight, cw.category)
        cw.weight = weight        
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
        return cw
    
    def create_weighted_average_criterion(self):
        print "[Controller] - Creating weighted average criterion"
        crit = WeightedAverage(cls='WeightedAverage')
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
        return crit
    
#    def create_weighted_average_of_best_N_criterion(self, N):
#        print "[Controller] - Creating weighted average of best N criterion"
#        crit = WeightedAverageOfBestN(cls='WeightedAverageOfBestN', N=N)
#        objectstore.flush()
#         self.set_dirty()
#        self.notify_criteria_observers()
#        return crit
    
    def get_category_weight_in_criterion(self, wa, cat):
        for cw in wa.category_weights:
            if cw.category == cat:
                return cw.weight
        raise GNotaException('Could not find category weight in Weighted Average')
    
    def get_category_weight_object_in_criterion(self, wa, cat):
        for cw in wa.category_weights:
            if cw.category == cat:
                return cw
        raise CategoryWithNoWeightException('Could not find category weight in Weighted Average')
    
    def get_category_weight(self, cw):
        return cw.weight
    
    def get_activity_weight(self, activity):
        return activity.weight
    
    def set_activity_weight(self, activity, weight):
        print "[Controller] - Setting activity =", activity, "weight =", weight
        activity.weight = float(weight)
        objectstore.flush()
        self.set_dirty()
    
    def create_simple_average_of_best_N_criterion(self, name, min_passing_score, ss, N):
        print "[Controller] - Creating simple average of best N criterion"
        score = self.get_scoresymbolvalue(min_passing_score, ss)
        crit = SimpleAverageOfBestN(
                                name=name,
                                passing_score=[score],
                                N=N,
                                cls='SimpleAverageOfBestN')
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
        return crit
    
    def create_simple_average_criterion(self, name, min_passing_score, ss):
        print "[Controller] - Creating simple average criterion"
        score = self.get_scoresymbolvalue(min_passing_score, ss)
        crit = SimpleAverage(name=name,
                             passing_score=[score],
                             cls='SimpleAverage')
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
        return crit
    
    def set_criterion_name(self, criterion, name):
        print "[Controller] - Setting criterion name =", name
        criterion.name = name
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
    
    def set_min_passing_score_as_text(self, criterion, min_passing_score, scoresystem):
        score = self.get_scoresymbolvalue(min_passing_score, scoresystem)
        criterion.passing_score = [score]
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
    
    def set_weighted_average_class(self, wa, cls):
        print "[Controller] - Setting weighted average class to", cls
        wa.classes = [cls]
        cls.criterion = wa
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()        
    
    def remove_criterion(self, crit):
        print "[Controller] - Deleting criterion name =", crit.name
        ApprovationCriterion.delete(crit)
        objectstore.flush()
        self.set_dirty()
        self.notify_criteria_observers()
    
    def create_ranged_scoresystem(self, name, desc, min_ssv, max_ssv):
        print "[Controller] - Creating scoresystem name =", name
        ss = RangedValuesScoreSystem(
                          name=name,
                          description=desc,
                          min=min_ssv,
                          max=max_ssv,
                          cls='RangedValuesScoreSystem',
                          )
        min_ssv.scoresystem = ss
        max_ssv.scoresystem = ss
        
        
        objectstore.flush()
        self.set_dirty()
        self.notify_scoresystems_observers()
        return ss
    
    def create_discrete_scoresystem(self, name, desc, scores):
        print "[Controller] - Creating scoresystem name =", name
        ss  = DiscreteValuesScoreSystem(name=name,
                                        description=desc,
                                        scores = scores,
                                        cls='DiscreteValuesScoreSystem',
                                        )
        for score in scores:
            score.scoresystem = ss
        objectstore.flush()
        self.set_dirty()
        self.notify_scoresystems_observers()
        return ss
    
    def remove_scoresystem(self, ss):
        print "[Controller] - Deleting scoresystem name =", ss.name
        AbstractScoreSystem.delete(ss)
        objectstore.flush()
        self.set_dirty()
        self.notify_scoresystems_observers()
    
    def get_scores_of_discrete_scoresystem(self, ss):
        return ss.scores
    
    def set_student_missed_classes_in_class(self, student, cls, missed_classes):
        g = self.get_student_average_grade_on_class(student, cls)
        g.missed_classes = missed_classes
        objectstore.flush()
        self.set_dirty()
    
    def get_student_missed_classes_in_class(self, student, cls):
        g = self.get_student_average_grade_on_class(student, cls)
        return g.missed_classes
    
    def set_maximum_missed_classes(self, crit, maximum_missed_classes):
        crit.use_missed_classes = True
        crit.maximum_missed_classes = maximum_missed_classes
        objectstore.flush()
        self.set_dirty()
    
    def is_passing_missed_classes(self, classes_missed, cls):
        crit = self.get_subclassed_criterion(cls.criterion)
        return crit.is_passing_missed_classes(classes_missed)        
    
    def student_approved_in_class(self, student, cls):
        overall_score = self.get_student_overall_score_on_class(student, cls)
        is_passing_score = self.is_passing_score(overall_score, cls)
        classes_missed = self.get_student_missed_classes_in_class(student, cls)
        is_passing_missed_classes = self.is_passing_missed_classes(classes_missed, cls)
        if is_passing_score and is_passing_missed_classes:
            return True
        else:
            return False
        
    def get_gnota_config(self):
        try:
            config = GNotaConfig.select()[0]
        except IndexError:
            config = GNotaConfig(
                                 runs_since_last_backup = 0,
                                 max_runs_since_last_backup=15,
                                 dontask_for_gradebook_backups=False,
                                 )
            
            objectstore.flush()
            self.set_dirty()
            
        return config
    
    def add_run(self, gc):
        gc.runs_since_last_backup += 1
        objectstore.flush()
    
    def reset_runs_since_last_backup(self, gc):
        gc.runs_since_last_backup = 0
        objectstore.flush()
        self.set_dirty()
    
    def check_backup_needed(self):
        gc = self.get_gnota_config()
        if gc.dontask_for_gradebook_backups:
            return False
        else:
            return gc.runs_since_last_backup > gc.max_runs_since_last_backup
    
    def add_run_to_current_config(self):
        gc = self.get_gnota_config()
        self.add_run(gc)
        return self.check_backup_needed()
    
    def reset_runs_in_current_config(self):
        gc = self.get_gnota_config()
        self.reset_runs_since_last_backup(gc)    
    
    def set_dont_ask(self, dontask):
        gc = self.get_gnota_config()
        gc.dontask_for_gradebook_backups = dontask
        objectstore.flush()
        self.set_dirty()
    
    def export_csv(self, filename):
        f = open(filename, 'wb')
        w = csv.writer(f, dialect='excel', delimiter=';')
        for cls in self.classes:
            w.writerow((cls.name, ))
            l = [_(u'Last name'), _(u'First name')]
            for ac in cls.activities:
                l.append(ac.name)
            l += [_(u'Overall score'), _(u'Missed classes'), _(u'Approved?')]
            w.writerow(l)
            for student in self.get_students_in_class_orderby(cls):
                l = [student.last_name, student.first_name]
                for activity in cls.activities:
                    if activity in student.activities: # if student participated in the activity
                        grade = self.get_student_grade_in_activity(student, activity)
                        l.append(str(grade.score))
                    else:
                        l.append('')
                l.append(str(self.get_student_overall_score_on_class(student, cls)))
                l.append(str(self.get_student_missed_classes_in_class(student, cls)))
                if self.student_approved_in_class(student, cls):
                    approved = _(u'Yes')
                else:
                    approved = _(u'No')
                    
                l.append(approved)
                w.writerow(l)
            w.writerow((None, ))
    
    
    def set_view(self, view):
        self.view = view
    
    def import_csv(self, filename):
        f = open(filename, 'r')
        reader = csv.reader(f, delimiter=';')
        view = self.view
        while True:
            try:
                row = reader.next()
                class_name = row[0]
                cls = self.add_class(name=class_name)
                view.edit_class(cls=cls)
                
                
                row = reader.next()
                activity_names = row[2:-1]
                activities = []
                for ac_name in activity_names:
                    ac = self.add_activity(name=ac_name, activity_class=cls, date=datetime.date.today())
                    view.edit_activity(activity=ac)
                    activities.append(ac)                                      
                
                while True:
                    row = reader.next()
                    if len(row) != 1:
                        last_name, first_name = row[0:2]
                        student = self.add_student(last_name=last_name, first_name=first_name)
                        self.add_class_to_student(cls, student)
                        scores = row[2:-1]
                        for i in range(len(scores)):
                            if scores[i] != '':
                                self.add_activity_to_student(activities[i], student)
                                self.set_student_grade_in_activity(student, activities[i], scores[i])
                        missed_classes = row[-1]
                    else:
                        break
            except StopIteration:
                break
        
    def is_saved(self):
        return self.saved
        
    
    def set_saved(self, saved):
        self.saved = saved
    
    def set_dirty(self):
        self.set_saved(False)
    
    def is_new(self):
        return self.get_real_dbpath() is None
    
    def _do_close(self):
        self.set_real_dbpath(None)
        self.set_work_dbpath(None)
        self.set_saved(True)
        try:
            metadata.dispose() #SQLAlchemy 0.3.4
            metadata.clear()
        except AttributeError:
            metadata.bind = None        
        objectstore.session.close()
        self.view.close_gradebook()
        
    
    def _do_new_gradebook(self):
        f = tempfile.NamedTemporaryFile()
        name = f.name
        del f
        connect(name, force_create=True)
        self.set_real_dbpath(None)
        self.set_work_dbpath(name)
        self.set_saved(False)
    
    def _do_save_gradebook(self):
        self.set_saved(True)
        shutil.copy(self.get_work_dbpath(), self.get_real_dbpath())
        
    def _do_open_gradebook(self, dbpath):
        self.set_real_dbpath(dbpath)
        f = tempfile.NamedTemporaryFile()
        name = f.name
        del f
        shutil.copy(dbpath, name)
        connect(name)
        self.set_work_dbpath(name)
        self.set_saved(True)
        try: # Delayed till window creation...
            self.view.populate_main_window()
            self.view.change_title(dbpath)
            #self.view.change_title(self.get_work_dbpath())
        except AttributeError:
            pass
    
    # Callbacks from view
    def close_gradebook(self):
        save = True
        if not self.is_saved():
            save = self.view.show_close_confirmation_dialog()
            if save is True:
                self.save_gradebook()
        
        if save is not None:
            self._do_close()
        
    def save_gradebook_as(self):
        dbpath = self.view.show_save_as()
        if dbpath:
            self.set_real_dbpath(dbpath)
            self._do_save_gradebook()
    
    def save_gradebook(self):
        if not self.is_new():
            self._do_save_gradebook()
        else:
            self.save_gradebook_as()
    
    def new_gradebook(self):
        self.close_gradebook()
        self._do_new_gradebook()
    
    def open_gradebook(self):
        dbpath = self.view.show_open()
        if dbpath:
            self.close_gradebook()
            self._do_open_gradebook(dbpath)
    
    def open_about_dialog(self):
        self.view.show_about_dialog()
    
    def quit_application(self):
        self.close_gradebook()
        self.view.quit_application()
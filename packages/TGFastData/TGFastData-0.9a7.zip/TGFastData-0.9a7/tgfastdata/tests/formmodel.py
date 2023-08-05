from sqlobject import *
from sqlobject.inheritance import InheritableSQLObject
from turbogears.database import PackageHub

hub = PackageHub("turbogears.widgets.tests.formmodel")
__connection__ = hub

class Person(SQLObject):
    
    form_order = ["name", "age", "date", "friends","company", "status", "salary"]
    
    name = StringCol(title='Full Name')
    age = IntCol(default=30)
    date = DateCol()
    friends = RelatedJoin('Person', otherColumn="friend_id")
    company = ForeignKey('Company', title='Company', default=None)
    status = EnumCol(enumValues=['Employed','Unemployed'], default='Unemployed', title='Status')
    salary = FloatCol()
    

    def __unicode__(self):
        return unicode(self.name)


class Company(SQLObject):

    name = UnicodeCol(title='Company name')
    employees = MultipleJoin('Person')

    def __unicode__(self):
        return self.name

class TestStringColWithTitle(SQLObject):
    """ Test model for ticket #272 and #300 """
    name = StringCol(title="This is the name")
    age = IntCol(title='Edad')

class BaseSO(InheritableSQLObject):
    parent_col = StringCol()

class ChildSO(BaseSO):
    child_col = StringCol()

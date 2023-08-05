from turbogears.testutil import DBTest
import formencode
from tgfastdata import formmaker
from turbogears import validators
from turbogears import widgets
import formmodel

class TestSQLObjectWidgets(DBTest):
    model = formmodel

    def test_simpleWidgets(self):
        fields = formmaker.fields_for(formmodel.Person)
        assert len(fields) == 7
        assert fields[1].name == "age"
        assert fields[1].default == 30
        assert isinstance(fields[1].validator, validators.Int)
        assert fields[0].label == "Full Name"
        assert isinstance(fields[2], widgets.CalendarDatePicker)
        assert fields[3].name == "friends"
        assert isinstance(fields[3].validator, formencode.ForEach)
        assert fields[4].name == "company"
        assert len(fields[4].options) > 0
        assert fields[5].name == "status"
        assert isinstance(fields[5], widgets.SingleSelectField)
        assert isinstance(fields[5].validator, validators.OneOf)
        assert fields[6].name == "salary"
        assert isinstance(fields[6].validator, validators.Number)

    def test_inheritable_so(self):
        fields = formmaker.fields_for(formmodel.ChildSO)
        assert len(fields) == 2

# Quick test of name capitalization
ltests = (
	('first_name', "First Name"),
	('firstName', "First Name"),
	('ADDRESS1', "Address1"),
	('email', "Email"),
	('secureID', "Secure Id"),
	('PhoneNO', "Phone No"),
	('floor1id', "Floor1id"),
)

for ltest in ltests:
#    print "'%s' --> '%s (%s)'" % (ltest[0], formmaker.name2label(ltest[0]), ltest[1])
    assert formmaker.name2label(ltest[0]) == ltest[1]


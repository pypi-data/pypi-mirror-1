import turbogears
import cherrypy
import formmodel
import turbogears.testutil as testutil
import tgfastdata as fastdata

class TestDataController(testutil.DBTest):
    model = formmodel

    class MyRoot(turbogears.controllers.RootController):
        test = fastdata.DataController(
                                sql_class = formmodel.TestStringColWithTitle)

    def test_string_col_with_title(self):
        """ Test case for ticket #272 """
        root = self.MyRoot()
        cherrypy.root = root
        cherrypy.tree.mount_points = {}
        
        print "\n\nRequest 1"
        testutil.createRequest("/test/")
        print cherrypy.response.body[0]
        assert "This is the name" in cherrypy.response.body[0]

        print "\n\nRequest 2"
        testutil.createRequest("/test/add")
        print cherrypy.response.body[0]
        assert "This is the name" in cherrypy.response.body[0]


        formmodel.TestStringColWithTitle(name="testName", age=25)
        testutil.createRequest("/test/1/edit")
        print cherrypy.response.body[0]
        assert "This is the name" in cherrypy.response.body[0]
        assert "testName" in cherrypy.response.body[0]

        testutil.createRequest("/test/1/show")
        print cherrypy.response.body[0]
        assert "testName" in cherrypy.response.body[0]

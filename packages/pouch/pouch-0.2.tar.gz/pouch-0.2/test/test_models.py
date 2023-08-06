import pouch

def setup_module(module):
    pouch.set_globals('http://127.0.0.1:5984', 'test')
    
def test_simple():
    class TestModel(pouch.Model): pass
    t = TestModel(test='blah', somethingelse='yup')
    t.save() ; tid = t._id
    assert t.__dict__ == TestModel.get(tid).__dict__
    assert t == TestModel.get(tid)
    t.another_value = 'testing'
    t.save()

def test_model_restrictions():
    class TestModelTwo(pouch.Model):
        unicode_test = pouch.Unicode()
        int_test = pouch.Int()
        float_test = pouch.Float()
        list_test = pouch.List()
        dict_test = pouch.Dict()
        bool_test = pouch.Bool()
    
    t = TestModelTwo()
    assert len(t.__restrictions__) is 6
    testvals = {int:1, float:1.5, str:'asdf', bool:True, unicode:u'asdf', dict:{'asdf':5}, list:[1]}
    for key, restriction in t.__restrictions__.items():
        setattr(t, key, testvals[restriction.type])

def test_views():
    result = pouch.GLOBAL_DB.views.company.all()   
    assert len(result['rows']) > 2

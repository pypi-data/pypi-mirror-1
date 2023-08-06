
from zoner import model
from zoner.tests.utils_database import SADBTest

class TestModel(SADBTest):
    model = model
    
    def test_user_creation(self):
        "User object creation should set display_name"
        
        obj = model.User(user_name='creosote',
            email_address = "spam@python.not",
            display_name = "Mr Creosote",
            password = "Wafer-thin Mint")
        obj.flush()
        obj = model.User.get_by(email_address='spam@python.not')
        assert obj.display_name == "Mr Creosote"
    


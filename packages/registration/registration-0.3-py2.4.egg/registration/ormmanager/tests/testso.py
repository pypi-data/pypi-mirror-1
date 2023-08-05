from registration.ormmanager.tests.somodel import User, Group
from registration.ormmanager.tests.generic import GeneralTests, set_user_class

class TestSqlObject(GeneralTests):
    
    def __init__(self):
        super(TestSqlObject, self).__init__()
        set_user_class(User)
    
    def setUp(self):
        # Create tables
        User.createTable()
        Group.createTable()
        self.user1 = User(user_name='bobvilla', 
            email_address='bob@homedepot.com',
            display_name='Bob Villa',
            password='toughasnails')     
        User(user_name='bobathome',
            email_address='bob@home.com',
            display_name='Bob Villa',
            password='hammertime')   
        
    def tearDown(self):
        User.dropTable()
        Group.dropTable()
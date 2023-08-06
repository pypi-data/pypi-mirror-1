import sqlalchemy
from turbogears import database
from turbogears.util import get_model
from turbogears import testutil

# from turbogears import config
# from pprint import pformat
# raise "config:"+pformat(config.config.configMap)

#database.set_db_uri("sqlite:///:memory:")

class SADBTest(object):
    model = None

    def setUp(self):
        # bind metadata/engine to model
        #database.bind_meta_data()
        if not self.model:
            self.model = get_model()
            if not self.model:
                raise "Unable to run database tests without a model"

        # drop all model tables
        for item in self.model.__dict__.values():
            if isinstance(item, sqlalchemy.Table):
                item.drop(checkfirst=True)
        # create all model tables
        for item in dir(self.model):
            item = getattr(self.model, item)
            if isinstance(item, sqlalchemy.Table):
                item.create(checkfirst=True)

    def tearDown(self):
        import sys
        sys.stderr.write( "tearDown.")
        database.rollback_all()
        # drop all model tables
        # for item in self.model.__dict__.values():
        #     if isinstance(item, sqlalchemy.Table):
        #         item.drop(checkfirst=True)


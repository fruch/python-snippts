from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

class ResourceBusy(Exception): pass

class ObjectPool:
    """ Resource manager."""
    def __init__(self, database='sqlite:///resources.db?check_same_thread=False'):
        self.engine = create_engine(database, echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def addResource(self, resource):
        try:
            self.session.add(resource)
            platform = self.session.query(Platform).filter_by(name=resource.type).first()
            if not platform:
                p = Platform(name=resource.type)
                self.session.add(p)
            self.session.commit()
        except IntegrityError as exp:
            self.session.rollback()
            raise exp
        
    def getResource(self, type, taken_by=None):
        res = self.session.query(Resource).filter_by(type=type, in_use=False).first()
        if res:
            res.in_use = True
            if taken_by: res.taken_by = taken_by
            self.session.commit()
            return res
        else:
            raise ResourceBusy("Free Resource of type [%s] wasn't found" % type)
    
    def returnResource(self, resource=None, id=None):
        if id is not None:
            resource = self.session.query(Resource).get(id)
        resource.in_use = False
        resource.taken_by = None
        self.session.commit()

    def emptyAllResources(self):
        con = self.engine.connect()
        trans = con.begin()
        for name, table in Base.metadata.tables.items():
            con.execute(table.delete())
        trans.commit()
        
    def deleteResource(self, resource=None, id=None):
        if id is not None:
            resource = self.session.query(Resource).get(id)
        self.session.delete(resource)
        self.session.commit()

    def allResourcesGenerator(self):
        for res in self.session.query(Resource):
            yield res

    def getPlatformList(self):
        for res in self.session.query(Platform):
            yield res

class Platform(Base):
    """Hold the possible platfroms"""
    __tablename__ = 'platforms'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Platform ('%s')>" % self.name

class Resource(Base):
    """Hold the information of an STB"""
    __tablename__ = 'resources'
    #__table__ = None # for pylint issues

    id = Column(Integer, primary_key=True)
    type = Column(String)
    ip_address = Column(String, unique=True)
    location = Column(String)

    avds_server = Column(String)
    rpc_ip_address = Column(String)
    mac_address = Column(String)
    NDS_barcode = Column(String)
    in_use = Column(Boolean)
    taken_by = Column(String)
    
    def __init__(self, type="", ip_address=""):
        self.type = type
        self.ip_address = ip_address

    def __repr__(self):
        return "<STB ('%s','%s', '%s')>" % (self.type, self.ip_address, self.location)

import unittest

class TestPool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = ObjectPool("sqlite:///:memory:")
        cls.pool.emptyAllResources()
        
    def test_01_adding_resources(self):
        self.pool.addResource(Resource("GPVR", "10.64.62.45"))
        a = self.pool.getResource("GPVR")
        self.pool.returnResource(a)

    def test_02_resource_not_found(self):
        a = self.pool.getResource("GPVR")
        self.assertRaises(Exception, self.pool.getResource, ("GPVR") )
        self.pool.returnResource(a)

    def test_03_return_resources(self):
        self.pool.addResource(Resource("UPC", "10.64.62.111"))
        a = self.pool.getResource("UPC")
        print a
        self.pool.returnResource(a)
        
        b = self.pool.getResource("UPC")
        print b
        self.pool.returnResource(b)

        c = self.pool.getResource("GPVR")
        print c
        self.pool.returnResource(c)

    def test_04_check_unique(self):
        self.assertRaises(IntegrityError, self.pool.addResource, (Resource("UPC", "10.64.62.111")))

    def test_05_platfroms(self):
        self.assertEqual("[<Platform ('GPVR')>, <Platform ('UPC')>]",
                        str([i for i in self.pool.getPlatformList()]))

def main(): # pragma: no cover
    pool = ObjectPool()
    # TODO: load all resources from config file
    # TODO: make a better option parser
    try:
        pool.addResource(Resource("UPC", "10.64.62.111"))
    except IntegrityError:
        pass
    a = pool.getResource("UPC")
    a.location = "In Lab 1999"
    pool.returnResource(a)
    del a

    a = pool.getResource("UPC")
    print a
    pool.returnResource(a)

if __name__ == "__main__":
    main() # pragma: no cover
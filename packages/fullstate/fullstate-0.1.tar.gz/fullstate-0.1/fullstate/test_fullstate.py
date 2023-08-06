# --*-- coding:iso8859-1 --*--
# Date: $Date: 2009-10-31 14:25:36 +0200 (La, 31 Lok 2009) $
# Revision: $Revision: 4 $
# Author: $Author: eino.makitalo $
# Url:  $HeadURL: https://fullstate.googlecode.com/svn/trunk/test_fullstate.py $


import unittest
from fullstate import *
import tempfile
from os import walk,remove,rmdir,listdir
from os.path import join

from os import mkdir


# Data classes need for tests

class DBROOT(object):
    pass

class Cat(object):
    def __init__(self,petname):
        self.petname=petname
        
class Dog(object):
    def __init__(self,colour):
        self.colour=colour;

class ZoolikeHome(object):
    def __init__(self):
        self.dog=[]
        self.cat=[]
        
class CreateDogCommand(object):
    def __init__(self,colour):
        self._dog_colour=colour
    def run(self,root):
        d=Dog(self._dog_colour)
        root.dog.append(d)
        return d

class CreateCatCommand(object):
    def __init__(self,petname):
        self.petname=petname
    def yep(self,root):
        c=Cat(self.petname)
        root.cat.append(c)
        return c
    fullstate_exec=yep
    

class testDB(unittest.TestCase):
    def setUp(self):
        self.testdir=tempfile.mkdtemp(suffix="fullstate_test",prefix="db")
    def tearDown(self):
        for root,dirs,files in walk(self.testdir,topdown=False):
            for f in [join(root,a) for a in files]:
                remove(f)
            rmdir(root)
            
    def testTearDown(self):
        d1=join(self.testdir,"A")
        mkdir(d1)
        d2=join(self.testdir,"B")
        mkdir (d2)
        with open(join(d1,"stupidhellofile.txt"),"w") as f:
            f.write("hello \n")
    def testSimpleDb(self):
        with DB(root=DBROOT,directory=self.testdir,dbname="simple") as db:
            self.assertTrue(isinstance(db,DB))
            self.assertTrue(isinstance(db.root,DBROOT))
            nofiles=listdir(self.testdir)
            self.assertEqual(0,len(nofiles))
        # no files is created if no need
        nofiles=listdir(self.testdir)
        self.assertEqual(0,len(nofiles))
    def createDogs(self,db):
            db.execute(CreateDogCommand("Red"))
            db.execute(CreateDogCommand("White"))
            db.execute(CreateDogCommand("Brown"))
    def createCats(self,db):
            db.execute(CreateCatCommand("Nasse"))
            db.execute(CreateCatCommand("Nuppu"))        
    def testZooicHomeDb(self):
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db:
            self.createCats(db)
            self.createDogs(db)
            self.assertEqual(3,len(db.root.dog))
            self.assertEqual(2,len(db.root.cat))
            nofiles=listdir(self.testdir)
            self.assertEqual(1,len(nofiles))
            self.assertEqual("C_zoo_",nofiles[0][:6])  # there is one C_zoo beginning file
            self.assertEqual(".trx",nofiles[0][-4:])  # and it's ending with .trx
            mname=nofiles[0][6:-4]  # should be timestamp....
            year=int(mname[0:4])
            month=int(mname[4:6])
            day=int(mname[6:8])
            hh=int(mname[8:10])
            mm=int(mname[10:12])
            ss=int(mname[12:14])
            self.assertTrue((year>2008)and (year<2200)) # life time
            self.assertTrue((month>0) and (month<=12))
            self.assertTrue((day>0) and (day<32))
            self.assertTrue((hh>=0) and (hh<24))
            self.assertTrue((mm>=0) and (mm<60))
            self.assertTrue((ss>=0) and (ss<60))
        nofiles=listdir(self.testdir)
        self.assertEqual(1,len(nofiles))
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db2:
            self.assertEqual(3,len(db2.root.dog))
            self.assertEqual(2,len(db2.root.cat))
            colours,names=self.collectDogsAndCats(db2)
            self.assertEqual(["Red","White","Brown"],colours)
            self.assertEqual(["Nasse","Nuppu"],names)
    def collectDogsAndCats(self,db):
        colours=[]
        for d in db.root.dog:
            colours.append(d.colour)
        names=[]
        for c in db.root.cat:
            names.append(c.petname)
        return (colours,names)
    def testSnapshot(self):
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db:
            self.createCats(db)
            self.createDogs(db)
            self.assertEqual(3,len(db.root.dog))
            self.assertEqual(2,len(db.root.cat))
            nofiles=listdir(self.testdir)
            self.assertEqual(1,len(nofiles))
            self.assertEqual("C_zoo_",nofiles[0][:6])  # there is one C_zoo beginning file
            self.assertEqual(".trx",nofiles[0][-4:])  # and it's ending with .trx
            db.takeSnapshot()
        nofiles=listdir(self.testdir)
        self.assertEqual(3,len(nofiles))
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db2:
            self.assertEqual(3,len(db2.root.dog))
            self.assertEqual(2,len(db2.root.cat))
            colours,names=self.collectDogsAndCats(db2)
            self.assertEqual(["Red","White","Brown"],colours)
            self.assertEqual(["Nasse","Nuppu"],names)
    def doTestData(self):
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db2:
            self.assertEqual(3,len(db2.root.dog))
            self.assertEqual(2,len(db2.root.cat))
            colours,names=self.collectDogsAndCats(db2)
            self.assertEqual(["Red","White","Brown"],colours)
            self.assertEqual(["Nasse","Nuppu"],names)        
    def testCleaning(self):
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db:
            self.createCats(db)
            db.takeSnapshot()
            self.createDogs(db)
            self.doTestData()
            nofiles=listdir(self.testdir)
            self.assertEqual(4,len(nofiles))  # 2 C file and S and Z file
            db.clean()   # 1 C file can be deleted
            nofiles=listdir(self.testdir)
            self.assertEqual(3,len(nofiles))  # 2 C file and S and Z file
            self.doTestData()

            db.takeSnapshot()
            nofiles=listdir(self.testdir)
            self.assertEqual(5,len(nofiles))  # + 2 files from snapshot
            self.doTestData()

            db.clean()
            nofiles=listdir(self.testdir)
            self.assertEqual(2,len(nofiles))  # only snapshot is left
        self.doTestData()

            
            
    def tamperFile(self,fx0):
        with open(join(self.testdir,fx0),"rb") as f1:
            data=f1.read()
        data2=data[:-40]+b'0'+data[-41:]
        with open(join(self.testdir,fx0),"wb") as f1:
            f1.write(data2)        
    def testChksumError(self):
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db:
            self.createCats(db)
            self.createDogs(db)
            self.assertEqual(3,len(db.root.dog))
            self.assertEqual(2,len(db.root.cat))
        fx0=listdir(self.testdir)[0]
        # let's change  -40 character at end
        self.tamperFile(fx0)
        try:
            with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db2:
                fail("chksum error waited")
        except RuntimeError:
            # last dog should be missing....
            return
        self.fail("unexpected control flow")
    def testSimpleFix(self):
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo") as db:
            self.createCats(db)
            self.createDogs(db)
            self.assertEqual(3,len(db.root.dog))
            self.assertEqual(2,len(db.root.cat))
        fx0=listdir(self.testdir)[0]
        # let's change  -40 character at end
        self.tamperFile(fx0)
        with DB(root=ZoolikeHome,directory=self.testdir,dbname="zoo",fix=True) as db2:
            #Brown dog is missing 
            self.assertEqual(2,len(db2.root.dog))
            self.assertEqual(2,len(db2.root.cat))
            colours,names=self.collectDogsAndCats(db2)
            self.assertEqual(["Red","White"],colours)
            self.assertEqual(["Nasse","Nuppu"],names)

if __name__=='__main__':
    unittest.main()
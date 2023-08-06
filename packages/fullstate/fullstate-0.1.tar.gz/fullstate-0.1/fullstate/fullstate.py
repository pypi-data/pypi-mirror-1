# --*-- coding:iso8859-1 --*--
# Date: $Date: 2009-11-01 12:46:43 +0200 (Su, 01 Mar 2009) $
# Revision: $Revision: 11 $
# Author: $Author: eino.makitalo $
# Url:  $HeadURL: https://fullstate.googlecode.com/svn/trunk/fullstate.py $

#Copyright (c) 2009 Eino Mäkitalo, Oy Netitbe Ltd
#
#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the
#"Software"), to deal in the Software without restriction, including
#without limitation the rights to use, copy, modify, merge, publish,
#distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so, subject to
#the following conditions:
#
#The above copyright notice and this permission notice shall be included
#in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
Fullstate in minimalistic implementation prevayler.
Motivation of this is just because pypersyst seems to be dead
You can use any pickleable python object as root object of your data tree

 Data root  is root of your data.. all data items must be accessible from it 
   When system takes snapshot, it creates checksummed pickle of this data root
   Because python is greate, we do not care what kind of object it is.
   we do not check this either so, if you create objects without connection direct or indirect (accessed by pickle)
   you state is not saved ok.  If you want 2 data roots, you must create tuple to collect them
   real_dataroot= (dataroot1,dataroot2)  

 Command is very simple object having at least run()-method. When 
   you want to modify state of system, you must create Command to do that.
   Command object must be pickleable too. It's written transaction log
   You must initialize all data into attributes before run-method. You can do it
   using __init__-method or any other suitable way for you.
   Only criteria is that Command can be unpickled and after executing run-method
   it creates deteministically same result as in first place.
   If you like more some other method than run(), you can specify it using class attribut fullstate_exec
   Example:
   class MyNormalCommand(Command):
      def run():
         do somethin here

      or


   class MyCommand(Command):
      fullstate_exec=exec
      def exec():
         do something here
   Because python is great, you do not need to use my Command class at all as long as your object has method run()

 Snapshots, cleaning and database directories...
 I do not create any scheduler here, but you can call fullstate.DB.snapshot() when you want to take snapshot
 Snapshots are named using naming standard      S_databasename_yyyymmddhhmmss.dbs. Timestamps are in UTC
 Command files are named using naming standard  C_databasename_yyyymmddhhmmss.trx 
 All command files created after snapshot are readed when system starts
 If system has earlier time in UTC than C-files, warning is given
 when cleaning/archiving all older snapshots and command files than latest snapshot can be removed/ archived
"""

import pickle
import datetime
from hashlib import sha256 as chksum
from os.path import join,split
from os import listdir,remove



class DB(object):
    """ Minimalistic prevalyer (aka Pypersyst) like memory based ACID-system
        Share for everybody what wants to use it
    """
    def __init__(self,root,directory,dbname="fullstate",fix=False):
        self.__root=root()
        self.__directory=directory
        self.__dbname=dbname
        self.commandfile=None
        self.__fix=fix
        self.__lastfnum=0
        self.__loadState()
    def __key(self,c):
        """ Extract date part of file name for sorting """
        return c[self.sl:]
    def __getRoot(self):
        """ used by property root  returns data root"""
        return self.__root
    def __enter__(self):
        """ with guarded statements """
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        if self.commandfile!=None:
            try:
                self.commandfile.flush()
            finally:
                try:
                    self.commandfile.close()
                finally:
                    self.commandfile=None
    def __SCfilename(self,C_or_S):
        """ creates next file name based on UTC time. If same file name is already given increments 'one second' """
        start=C_or_S
        if start=="C": 
            ending=".trx"
        else:
            ending=".dbs"
        fnum=datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        if (int(fnum)<=self.__lastfnum):
            self.__lastfnum=self.__lastfnum+1
            fnum=str(self.__lastfnum)  
        else:
            self.__lastfnum=int(fnum)
        #print("FNUM= ",fnum," Lastfnum",self.__lastfnum," C or S ",C_or_S)
        return join(self.__directory,C_or_S+"_"+self.__dbname+"_"+fnum+ending)
    def __Zfilename(self,fx):
        dir01, fx01= split(fx)
        return join(dir01,fx01.replace("S","Z",1)) 
    def __realfiles(self):
        """ Sort C and S files so that newest is index 0 and oldest one at last position
            Return list of file names """
        statefiles=listdir(self.__directory)
        realones=[]
        self.sl=3+len(self.__dbname)
        for filt in statefiles:
            if (filt[:self.sl].lower() == ("C_"+self.__dbname+"_").lower()) and (filt[-4:].lower()==".trx"):
                realones.append(filt)
            if (filt[:self.sl].lower() == ("S_"+self.__dbname+"_").lower()) and (filt[-4:].lower()==".dbs"):
                realones.append(filt)
        realones.sort(key=self.__key,reverse=True)
        return realones
    def __loadState(self):
        """ helper function to load files """
        realones=self.__realfiles()
        if (len(realones)>0):
            self.__lastfnum=int(self.__key(realones[0])[:14])
        # let's fetch latest S-file 
        ind=0
        while((ind<len(realones)) and (realones[ind][0].lower()!="s")):
            ind=ind+1
        if (ind<len(realones)):
            try:
                self.__loadSnapshot(join(self.__directory,realones[ind]))
            except RuntimeError as e:
                if self.__fix:
                    # we should try to get previous snapshot and run all command files for that - not implented yet
                    raise
                else:
                    raise
        ind=ind-1
        # now we must handle all command files
        try:
            while(ind>=0):
                self.__loadCommandFile(join(self.__directory,realones[ind]))
                ind=ind-1
        except RuntimeError as e:
            if self.__fix:
                # just silently return here
                return
            else:
                raise
            

    def __loadSnapshot(self,fn):
        """ loads one snapshot fx is full path """
        fn2=self.__Zfilename(fn)
        with open(fn2,"rb") as f2:
            chk=f2.read()
        c=chksum()
        with open(fn,"rb") as f:
            data=" "
            while(len(data)>0):                
                data = f.read(1024)
                c.update(data)
        if chk==c.digest():
            with open(fn,"rb") as f:
                r=pickle.load(f)
                self.__root=r
        else:
            raise RuntimeError("Chksum error in file "+fx)
    def __loadCommandFile(self,fx):
        """loads one command file when loading state """
        with open(fx,"rb") as f:
            while(1):
                try:
                    length=pickle.load(f)
                except EOFError:
                    break;
                data=f.read(length)
                chk=f.read(32)
                c=chksum()
                c.update(data)
                if chk==c.digest():
                    comm=pickle.loads(data)
                    self.execute(comm,loadstate=True)
                else:
                    raise RuntimeError("Checksum error in file "+fx)      

    def takeSnapshot(self):
        """ Makes snapshot file S_dbname_YYYYMMDDHHMMSS.dbs and checksum file Z_dbname_YYYYMMDDHHMMSS.dbs """
        if self.commandfile!=None:
            self.commandfile.close()
            self.commandfile=None
            fn=self.__SCfilename("S")
            with open(fn,"wb") as fx:
                pickle.dump(self.__root,fx)
            c=chksum()
            with open(fn,"rb") as fx:
                data=" "
                while(len(data)>0):
                    data=fx.read(1024)
                    c.update(data)
            fn2=self.__Zfilename(fn)
            with open(fn2,"wb") as fx2:
                fx2.write(c.digest())
    def clean(self):
        """ delete all files before last snapshot """
        realones=self.__realfiles()
        ind=0
        while((ind<len(realones)) and (realones[ind][0].lower()!="s")):
            ind=ind+1
        if (ind<len(realones)):
            ind=ind+1
            while(ind<len(realones)):
                rem=realones[ind]
                if rem[0].lower()=="s":
                    rem2="Z"+rem[1:]
                    remove(join(self.__directory,rem2))
                remove(join(self.__directory,rem))
                ind=ind+1
          
    root=property(__getRoot) # read only property
    def execute(self,command,loadstate=False):
        """ executes one Command. to alter data root.  Logs command into C-file
            When loading state back into memory from existing files loadstate=True """
        if ((not loadstate) and (self.commandfile==None)):
            self.commandfile=open(self.__SCfilename("C"),"wb")
        try:
            ok=False
            if hasattr(command,"fullstate_exec"):
                f=getattr(command,"fullstate_exec")
                f(self.__root)
            else:
                command.run(self.__root)
            ok=True
        finally:
            if (not loadstate):
                c=chksum()
                
                data=pickle.dumps(command)
                c.update(data)
                self.commandfile.write(pickle.dumps(len(data)))
                self.commandfile.write(data)
                self.commandfile.write(c.digest())
                self.commandfile.flush()

                

"""
This module implements facilities used to manage Exospace objects. Exospace
objects are used to store objects being associated to a compiled module.

Requirements:
-------------

Often a source transformation of a module M alone isn't sufficient. In the course
of transformation objects are created that shall be associated with the bytecode of M.
We refuse to express those objects as CSTs being weaved into the transfomed code.
Instead we want to link those objects to function calls being generated. This requires
the connection of a compiled module M.pyc and a set of persistent objects M.pkl .

Design:
-------

Consider the following link-structure

     M (transformed)                            exo_module
     ------------------------                   -----------

     def foo():
         return exospace.m.bar  o------------>  exospace.m.bar


The idea behind the notion of 'exospace.m.bar' in the function 'foo' is that this
call is generated at 'transformation time'. The related object 'exospace.m.bar' in the
exo_module is created at transformation time as well. When foo() is called it shall refer
to this object.

Only the reference to exospace has been generated into M at transformation time. It is
expressed by the following sequence of statements:

   from EasyExtend.exotools import exoload; exospace = exoload(__file__)

The __file__ object stores the path to M.


Caveats
-------

When moving M.pyc around the connection to the exo.space archive will be broken unless
exo.space is moved with M.pyc as well. However it is more likely that M is moved in source
form or the whole directory containing M.py and M.pyc and the exo.space archive is moved.

I considered the alternative of putting M.pyc together with M.pkl into one zip-archive but
stumbled on technical problems. Most notably the __file__ parameter passed to exoload()
points to the archive. So all we get know is that M.pyc is included into M.zip. This is not
sufficient information for exoload() to access M.pkl and return the unpickled value.


TODO:
1) Where is exo information stored during transformation?
2) What happens with the __publish__ attribute? Is it necessary and shall it be preserved?
3) Which events lead to
   - pickling of exo objects
   - creation of exo.py
   - wrapping modules int xxx.pyz
   ?
4) Import of *.pyz modules
5) What happens when *.pyc and *.pyz are in the same directory?
-------------------------------------------------------------------------

   The exo module is associated with a CST.

   cst_power = exospace.wire("a.b", value) .

   On transformation exotools creates a new object called exospace. It is initialized with the id of the
   CST being transformed. The exospace object is passed to the langlet s.t. it can be used uniformly.

   The exospace object has a method serialize that creates both a new exo.py module and exo.pickle.

"""
from __future__ import with_statement
import EasyExtend
import os
from EasyExtend.util.path import path
import string
import zipfile
import pickle
from csttools import power, atom, trailer, Name
import random
import parser


import_exoload = parser.suite("from EasyExtend.exotools import exoload; exospace = exoload(__file__)").tolist()[1]

def random_name(strn):
    return strn+"_"+str(random.randrange(1000000))

class any_obj(object): pass



class Exospace(object):
    def __init__(self, tid):
        self.tid = tid
        self.wired = False
        self.exo   = any_obj()

    def wire(self, attr, value):
        '''
        This method connects a function call and an exospace attribute.
        '''
        self.wired = True
        if attr.endswith(";"):
            exoattrname = attr[:-1]
        else:
            exoattrname = random_name(attr)
        exoattr_call = power(*([atom(Name("exospace")), trailer(".", Name("exo"))]+[trailer(".", Name(a)) for a in exoattrname.split(".")]))
        attr = self.exo
        exonamesplit = exoattrname.split(".")
        while True:
            name = exonamesplit.pop(0)
            if exonamesplit:
                setattr(attr, name, any_obj())
                attr = getattr(attr, name)
            else:
                setattr(attr, name, value)
                break
        return exoattr_call

    def dump(self, where):
        '''
        @param where: location of module to be wired with exospace.
        '''
        zip_module = path(where).dirname().joinpath("exo.space")
        pkl_name   = str(path(where).namebase+".pkl")
        f = open(pkl_name,"wb")
        pickle.dump(self.exo, f)
        f.close()
        zf = zipfile.ZipFile(zip_module, "w")
        zf.write(pkl_name)
        zf.close()
        path(pkl_name).remove()


def test_exospace():
    exospace = Exospace(0)
    exospace.wire("a.b", 2**23)
    exospace.wire("f;", path(__file__))
    exospace.dump(__file__)
    exo = exoload(__file__)
    assert exo.f == __file__

def exoload(where):
    '''
    @param where: location of module to be wired with exospace.
    '''
    p_module = path(where)
    modname  = str(p_module.namebase)
    exo_pickle = p_module.dirname().joinpath("exo.space")
    if not zipfile.is_zipfile(exo_pickle):
        return
    zf = zipfile.ZipFile(exo_pickle, 'r')
    # print "MODNAME", modname+".pkl"
    # print "NAMELIST", zf.namelist()
    if modname+".pkl" in zf.namelist():
        bytes = zf.read(modname+".pkl")
        return pickle.loads(bytes)


def dump_exo_obj(obj, pth):
    import pickle
    with open(path(pth).joinpath("exo.pickle"),"wb") as f:
        pickle.dump(obj, f)

# dump_exo_obj({"0": 1}, path(EasyExtend.__file__).dirname())

def move_to_archive(modpath):
    zip_module = path(modpath).splitext()[0]+".pyz"
    zf = zipfile.ZipFile(zip_module, 'w')
    mod_dir  = path(modpath).dirname()
    mod_name = path(modpath).basename()
    os.chdir(mod_dir)
    zf.write(str(mod_name))
    zf.write("exo.py")
    zf.write("exo.pickle")
    zf.close()
    path(modpath).remove()
    mod_dir.joinpath("exo.py").remove()
    mod_dir.joinpath("exo.pickle").remove()


# move_to_archive(path(EasyExtend.__file__).dirname().joinpath("bla.pyc"))

def test_exospace():
    exospace = Exospace(0)
    exospace.wire("a.b", 2**23)
    exospace.wire("a.b;", 2**24)
    exospace.wire("f;", path(__file__))
    exospace.dump(__file__)
    exo = exoload(__file__)
    assert exo.f == __file__
    assert exo.a.b == 2**24

#test_exospace()

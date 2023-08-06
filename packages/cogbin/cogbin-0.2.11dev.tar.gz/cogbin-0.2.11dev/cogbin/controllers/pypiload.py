import os

import cPickle
f=open(os.path.join(os.path.dirname(__file__),'../public/pypi.cPickle'),'r')
pypi_list_packages = cPickle.load(f)
pypi_packages = cPickle.load(f)
f.close()

list_of_packages=[]
#tg2 session--------
import os
from paste.deploy import appconfig
import transaction
from sqlalchemy import create_engine
from cogbin.model import *

conf_dict = appconfig('config:%s' % os.path.join(os.getcwd(),
'development.ini'))
engine = create_engine(conf_dict['sqlalchemy.url'])
engine.echo=False
init_model(engine)
#end of tg2 session

from cogbin.model import DBSession, metadata
from cogbin.model.pypi import PyPIPackages
import transaction
DBSession.query(PyPIPackages).delete()

for i in pypi_packages:
    new=PyPIPackages()
    #print i
    try:
        for k,v in pypi_packages[i].items():
            #print k,':',v
            if k=='classifiersc':
                setattr(new,unicode(k),unicode(v))
            else:
                setattr(new,unicode(k),unicode(v))
            
        new.name=unicode(i[0])
        #new.version=i[1]
        #print 'name',i[0],new.name
        #print 'ver',i[1],new.version
    except AttributeError:
        #print 'this eerrrr'
        continue

    if i[0]!=None and i[1]!=None:
        DBSession.add(new)

transaction.commit()



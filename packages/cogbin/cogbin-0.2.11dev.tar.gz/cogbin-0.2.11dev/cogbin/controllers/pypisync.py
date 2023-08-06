#!/usr/bin/env python
import cPickle
import time
import os
#Get existing cPickle file and load data.
try:
    f=open(os.path.join(os.path.dirname(__file__),'../public/pypi.cPickle'),'r')
    pypi_list_packages = cPickle.load(f)
    pypi_packages = cPickle.load(f)
    f.close()
except IOError:
    pypi_list_packages = []
    pypi_packages = {}
    pypi_packages['pypi_lastupdate']=int(time.time())
except EOFError:
    pypi_list_packages = []
    pypi_packages = {}
    pypi_packages['pypi_lastupdate']=int(time.time())
    


import xmlrpclib
XML_RPC_SERVER = 'http://pypi.python.org/pypi'
pypi=xmlrpclib.ServerProxy(XML_RPC_SERVER)
pypi2=xmlrpclib.ServerProxy(XML_RPC_SERVER)

print 'Getting list of packages'
new_pypi_list_packages=pypi.list_packages()
print 'Got a list of packages'
new_pypi_packages={}
import time
new_pypi_packages['pypi_lastupdate']=int(time.time())

#Campare two lists, and get a list of new packages.Returns [package1,package2]
missing_packages=[i for i in new_pypi_list_packages if i not in pypi_list_packages]

print 'Need to get information on %s new packages' % len(missing_packages)

#Download data for new packages
for package in missing_packages:
    try:
        version=''
        metadata=''
        version=pypi.package_releases(package)
        if len(version)==1:
            version=version[0]
            metadata=pypi2.release_data(package ,version)
        else:
            print 'Package has no version %s' %package
            version=''
        pypi_list_packages.append(package)        
        pypi_packages[package,version]=metadata
        #print package,version,metadata
        print package,version
        #time.sleep(1)
    except IndexError:
        print 'Package has no version: %s' %package
    except Exception ,e:
        print e
        print 'Lost connection?'


#start = time.time()

#Update metadata since last update.Returns [package_name,version]
to_update_packages=pypi.updated_releases(int(pypi_packages['pypi_lastupdate']))
#to_update_packages=pypi.updated_releases(int(1235350891.9877839))
print 'Need to get information on %s updated packages' % len(to_update_packages)

for package,version in to_update_packages:
        #time.sleep(1)
    try:
        #version=pypi.package_releases(package)[0]
        #metatdata=''
        #time.sleep(1)
        metadata=pypi2.release_data(package ,version)        
        pypi_packages[package,version]=metadata
        #print package,version,metadata
        print package,version
        #time.sleep(1)
        pypi_packages['pypi_lastupdate']=new_pypi_packages['pypi_lastupdate']
    except IndexError:
        print 'Package has no version: %s' %package
    except Exception ,e:
        print e
        print 'Lost connection?'

#print "Elapsed Time: %s" % (time.time() - start)

import cPickle
f=open(os.path.join(os.path.dirname(__file__),'../public/pypi.cPickle'),'w')
cPickle.dump(pypi_list_packages,f)
cPickle.dump(pypi_packages,f)
f.close()


#zw.mail.incoming 0.1.2.3
#zw.schema 0.3.0b2.1
#zw.widget 0.1.6.2
#Elapsed Time: 3963.42923498
#zw.mail.incoming 0.1.2.3
#zw.schema 0.3.0b2.1
#zw.widget 0.1.6.2
#Elapsed Time: 9456.79680395


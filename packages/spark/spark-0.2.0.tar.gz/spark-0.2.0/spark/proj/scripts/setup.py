#!/usr/bin/env python
#

import sys,os,time
spark_dir   = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))
spark_updir = os.path.realpath(os.path.join(spark_dir,".."))
etc_dir     = os.path.realpath(os.path.join(spark_dir,"etc"))

def setup():
	print "Creating __init__.py"
	f = open(os.path.join(spark_dir,"__init__.py"),'w')
	f.write('')
	f.close()
	time.sleep(0.1)

	sys.path.insert(0,spark_updir)
	from spark.lib.sprite import Sprite
	
	print "Creating etc/apache_modpython.conf"
	f = open(os.path.join(spark_dir,"etc","apache_modpython.conf"),'w')
	tmpl = Sprite("apache_modpython.conf",os.path.join(etc_dir,"tmpl"))
	tmpl.assign_vars({'spark_dir':spark_dir,
			'spark_updir':spark_updir,
			'public_dir':os.path.join(spark_dir,'public')
			})
	f.write("\n".join(tmpl.display(1)))
	f.close()
	
	print "Creating etc/lighttpd-python.conf"
	f = open(os.path.join(spark_dir,"etc","lighttpd-python.conf"),'w')
	tmpl = Sprite("lighttpd-python.conf",os.path.join(etc_dir,"tmpl"))
	tmpl.assign_vars({'spark_dir':spark_dir})
	f.write("\n".join(tmpl.display(1)))
	f.close()

	print "creating etc/python.fcgi"

	print "Creating etc/modpython.py"


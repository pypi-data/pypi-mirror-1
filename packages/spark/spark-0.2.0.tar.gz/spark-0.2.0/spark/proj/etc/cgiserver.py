#!/usr/bin/env python
import os, sys
import cgitb; cgitb.enable()

spark_proj = os.path.join(os.path.dirname(__file__),'..')
sys.path.insert(0,spark_proj)
#os.putenv('spark_proj',spark_proj)
from spark.ReqBase import ReqBase
ReqBase().run()

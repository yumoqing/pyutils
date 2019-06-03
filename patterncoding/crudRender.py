# template engine adapter
import os
import sys
from jinja2 import Environment,FileSystemLoader
from appPublic.dictObject import DictObject
from xlsxData import CRUDData

from myTemplateEngine import MyTemplateEngine

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print("Usage:\n%s xlsxfile templete_file\n" % sys.argv[0])
    sys.exit(1)
  #print( "......................")
  a = CRUDData(sys.argv[1])
  data = a.read()
  #print( type(data['summary'][0]['primary']),data['summary'][0]['primary'])
  e = MyTemplateEngine(os.path.dirname(sys.argv[2]))
  e.set('crudObject',a)
  s = e.render(os.path.basename(sys.argv[2]),data)
  print("%s\n" % s)
  sys.exit(0)

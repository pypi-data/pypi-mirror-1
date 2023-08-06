import sys, string
import SwishE

"""
Usage:
   python a.py t/swish.idx madrid
   python a.py t/swish.idx madrid and lluita
   ...
   
"""

def main():
   """
   python a.py t/swish.idx madrid
   python a.py t/swish.idx madrid and lluita
   ..."""
   
   if len(sys.argv) < 3:
      sys.stderr.write('Usage:  a.py <index file> <query>')
      sys.exit(1)
      pass
      
   indexfile = sys.argv[1]
   query = string.join(sys.argv[2:], ' ')
   sw = SwishE.new(indexfile)
  
   for k in sw.headerNames():
      print k, '->', sw.headerValue('t/swish.conf',k)
   print '----'  
   search = sw.search('')
   search.setSort("swishtitle desc")
   results = search.execute(query)
   
   for r in results:
      print r.getproperty('swishtitle')

if __name__ == '__main__':
   main()

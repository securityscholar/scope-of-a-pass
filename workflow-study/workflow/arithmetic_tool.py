"""Isolated, time-bounded arithmetic worker; no scientific-answer oracle used."""
import json,sys
from workflow import execute_local
if __name__=='__main__':
    item=json.load(sys.stdin);print(json.dumps(execute_local(item['code'],item['rows']),allow_nan=False))

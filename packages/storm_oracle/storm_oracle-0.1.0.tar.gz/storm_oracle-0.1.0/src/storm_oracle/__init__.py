import sys
import oracle
import storm.databases

sys.modules['storm.databases.oracle'] = oracle

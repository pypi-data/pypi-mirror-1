import sys
import storm.databases
import mssql2005
import mssql_connector
sys.modules['storm.databases.mssql2005'] = mssql2005
sys.modules['storm.databases.mssql_connector'] = mssql_connector

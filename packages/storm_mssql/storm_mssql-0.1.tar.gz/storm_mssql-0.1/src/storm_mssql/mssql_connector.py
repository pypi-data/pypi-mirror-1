#!/usr/bin/env python
"""
Module to allow selecting among MS SQL Server database connectors
such mxODBC, pyodbc, pymssql, and pyado.
"""

from platform import platform

from storm.databases import dummy
from storm.exceptions import install_exceptions

def initialize_connector (connector_name='mxODBC'):
    global MsSQLdbapi
    try:
        if connector_name == 'mxODBC':
            if 'Windows' in platform():
                from mx.ODBC import Windows as MsSQLdbapi
            elif 'Linux' in platform():
                from mx.ODBC import unixODBC as MsSQLdbapi
            elif 'Darwin' in platform():
                from mx.ODBC import iODBC as MsSQLdbapi
            else:
                raise ImportError, "Unrecognized platform for mxODBC import"
            MsSQLdbapi.stormify_connection = stormify_connection_mxODBC
        elif connector_name == 'adodbapi':
            import adodbapi as MsSQLdbapi
        elif connector_name == 'pymssql':
            import pymssql as MsSQLdbapi
        else:
            raise ValueError, "Unknown connector name; cannot initialize"
    except ImportError:
        MsSQLdbapi = dummy
        
    # inject Storm exceptions into the db driver 
    install_exceptions(MsSQLdbapi)
    install_exceptions(MsSQLdbapi.Error)

def stormify_connection_mxODBC (raw_connection):
    """
    Customize mxODBC connection object to have necessary
    properties to work well with Storm, such as two-way
    unicode support.
    """
    raw_connection.stringformat = MsSQLdbapi.MIXED_STRINGFORMAT
    raw_connection.datetimeformat = MsSQLdbapi.PYDATETIME_DATETIMEFORMAT 

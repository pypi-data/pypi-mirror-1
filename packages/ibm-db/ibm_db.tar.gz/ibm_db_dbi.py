#--------------------------------------------------------------------------#
# Licensed Materials - Property of IBM                                     #
#                                                                          #
# (C) Copyright IBM Corporation 2006, 2007.                                #
#--------------------------------------------------------------------------#
# Authors: Swetha Patel                                                    #
# Version: 0.1.0
#--------------------------------------------------------------------------#

"""This module implements the Python DB API Specification v2.0 for DB2
database.

"""

import exceptions
import time
import datetime
import types

import ibm_db

# Constants for specifying database connection options.
SQL_ATTR_AUTOCOMMIT = ibm_db.SQL_ATTR_AUTOCOMMIT
SQL_AUTOCOMMIT_OFF = ibm_db.SQL_AUTOCOMMIT_OFF
SQL_AUTOCOMMIT_ON = ibm_db.SQL_AUTOCOMMIT_ON
ATTR_CASE = ibm_db.ATTR_CASE
CASE_NATURAL = ibm_db.CASE_NATURAL
CASE_LOWER = ibm_db.CASE_LOWER
CASE_UPPER = ibm_db.CASE_UPPER

# Module globals
apilevel = '2.0'
threadsafety = 0
paramstyle = 'qmark'


class Error(exceptions.StandardError):
    """This is the base class of all other exception thrown by this
    module.  It can be use to catch all exceptions with a single except
    statement.
    
    """
    def __init__(self, message):
        """This is the constructor which take one string argument."""
        self.message = message
    def __str__(self):
        """Converts the message to a string."""
        return repr(self.message)


class Warning(exceptions.StandardError):
    """This exception is used to inform the user about important 
    warnings such as data truncations.

    """
    def __init__(self, message):
        """This is the constructor which take one string argument."""
        self.message = message
    def __str__(self):
        """Converts the message to a string."""
        return repr(self.message)


class InterfaceError(Error):
    """This exception is raised when the module interface is being
    used incorrectly.

    """
    pass


class DatabaseError(Error):
    """This exception is raised for errors related to database."""
    pass


class InternalError(DatabaseError):
    """This exception is raised when internal database error occurs,
    such as cursor is not valid anymore.

    """
    pass


class OperationalError(DatabaseError):
    """This exception is raised when database operation errors that are
    not under the programmer's control occur, such as unexpected
    disconnect.

    """ 
    pass


class ProgrammingError(DatabaseError):
    """This exception is raised for programming errors, such as table 
    not found.

    """
    pass


class IntegrityError(DatabaseError):
    """This exception is thrown when errors occur when the relational
    integrity of database fails, such as foreign key check fails. 

    """
    pass


class  DataError(DatabaseError):
    """This exception is raised when errors due to data processing,
    occur, such as divide by zero. 

    """
    pass


class NotSupportedError(DatabaseError):
    """This exception is thrown when a method in this module or an 
    database API is not supported.

    """
    pass


def Date(year, month, day):
    """This method can be used to get date object from integers, for 
    inserting it into a DATE column in the database.

    """
    return datetime.date(year, month, day)

def Time(hour, minute, second):
    """This method can be used to get time object from integers, for 
    inserting it into a TIME column in the database.

    """
    return datetime.time(hour, minute, second)

def Timestamp(year, month, day, hour, minute, second):
    """This method can be used to get timestamp object from integers, 
    for inserting it into a TIMESTAMP column in the database.

    """
    return datetime.datetime(year, month, day, hour, minute, second)

def DateFromTicks(ticks):
    """This method can be used to get date object from ticks seconds,
    for inserting it into a DATE column in the database.

    """
    time_tuple = time.localtime(ticks)
    return datetime.date(time_tuple[0], time_tuple[1], time_tuple[2])

def TimeFromTicks(ticks):
    """This method can be used to get time object from ticks seconds,
    for inserting it into a TIME column in the database.

    """
    time_tuple = time.localtime(ticks)
    return datetime.time(time_tuple[3], time_tuple[4], time_tuple[5])

def TimestampFromTicks(ticks):
    """This method can be used to get timestamp object from ticks  
    seconds, for inserting it into a TIMESTAMP column in the database.

    """
    time_tuple = time.localtime(ticks)
    return datetime.datetime(time_tuple[0], time_tuple[1], time_tuple[2], 
                                time_tuple[3], time_tuple[4], time_tuple[5])

def Binary(string):
    """This method can be used to store binary information, for 
    inserting it into a binary type column in the database.

    """
    if not isinstance( string, types.StringType):
        raise InterfaceError("Binary function expects an argument "
                                                           "of type string")
    return buffer(string)


class DBAPITypeObject:
    """Class used for creating objects that can be used to compare
    in order to determine the python type to provide in parameter 
    sequence argument of the execute method.

    """
    def __init__(self, col_types):
        """Constructor for DBAPITypeObject.  It takes a tuple of 
        database column type as an argument.

        """
        self.col_types = col_types
    def __cmp__(self, cmp):
        """This method checks if the string compared with is in the 
        tuple provided to the constructor of this object.  It takes 
        string as an argument. 
 
        """
        if cmp in self.col_types:
            return 0
        if cmp < self.col_types:
            return 1
        else:
            return -1

# The user can use these objects to compare the database column types
# with in order to determine the python type to provide in the 
# parameter sequence argument of the execute method.
STRING = DBAPITypeObject(("CHARACTER", "CHAR", "VARCHAR", 
                               "CHARACTER VARYING", "CLOB", "XML", "STRING"))

BINARY = DBAPITypeObject(("BLOB", "BINARY LARGE OBJECT"))

NUMBER = DBAPITypeObject(("SMALLINT", "INTEGER", "INT", "BIGINT", "FLOAT",
                       "REAL", "DOUBLE", "DECIMAL", "DEC", "NUMERIC", "NUM"))

DATETIME = DBAPITypeObject(("DATE", "TIME", "TIMESTAMP"))

ROWID = DBAPITypeObject(())

# This method is used to determine the type of error that was 
# generated.  It takes an exception instance as an argument, and 
# returns exception object of the appropriate type.
def _get_exception(inst):
    # These tuple are used to determine the type of exceptions that are
    # thrown by the database.  They store the SQLSTATE code and the
    # SQLSTATE class code(the 2 digit prefix of the SQLSTATE code)  
    warining_error_tuple=('01')
    data_error_tuple=('02', '22', '10601', '10603', '10605', '10901', '10902', 
                                                               '38552', '54')

    operational_error_tuple = ( '08', '09', '10502', '10000', '10611', '38501', 
                        '38503', '38553', '38H01', '38H02', '38H03', '38H04',
                                 '38H05', '38H06', '38H07', '38H09', '38H0A')

    integrity_error_tuple = ('23')

    internal_error_tuple = ('24', '25', '26', '2D', '51', '57')

    programming_error_tuple = ('08002', '07', 'OD', 'OF', 'OK', 'ON', '10',  
                              '27', '28', '2E', '34', '36', '38', '39', '56', 
                              '42', '3B', '40', '44', '53', '55', '58', '5U',
                                                                         '21')

    not_supported_error_tuple = ('0A', '10509')

    # These tuple are used to determine the type of exceptions that are
    # thrown from the driver module. 
    interface_exceptions = ("ATTR_CASE attribute must be one of CASE_LOWER, "
      "CASE_UPPER, or CASE_NATURAL", "Connection or statement handle must be "
        "passed in.", "Supplied parameter is invalid", "Param is not a tuple")

    programming_exceptions = ("Connection is not active", 
                       "qualifier must be a string", "owner must be a string",
                "table_name must be a string", "column_name must be a string", 
             "procedure name must be a string", "table name must be a string", 
                    "unique must be a boolean", "table type must be a string", 
                        "Parameters not bound", "Column ordinal out of range", 
                              "Requested row number must be a positive value", 
                                     "Options Array must have string indexes")

    database_exceptions = ("Binding Error", 
                                   "Column information cannot be retrieved: ", 
          "Column binding cannot be done: ", "Failed to Determine XML Size: ")

    statement_exceptions = ("Statement Execute Failed: ", 
        "Describe Param Failed: ", "Sending data failed: ", "Fetch Failure: ",
                          "SQLNumResultCols failed: ", "SQLRowCount failed: ")

    operational_exceptions = ("Connection Resource cannot be found", 
                       "Failed to Allocate Memory", "Describe Param Failed: ",
       "Statement Execute Failed: ", "Sending data failed: ", 
       "Failed to Allocate Memory for XML Data", 
       "Failed to Allocate Memory for LOB Data")

    # First check if the exception is from the database.  If it is 
    # determine the SQLSTATE code which is used further to determine 
    # the exception type.  If not check if the exception is thrown by 
    # by the driver and return the appropriate exception type.  If it 
    # is not possible to determine the type of exception generated 
    # return the generic Error exception.
    if inst is not None:
        message = repr(inst)
        if message.startswith("Exception('") and message.endswith("',)"):
            message = message[11:]
            message = message[:len(message)-3]
        index = message.find('SQLSTATE=')
        if( message != '') & (index != -1):
            error_code = message[(index+9):(index+14)]
        else:
            for key in interface_exceptions:
                if message.find(key) != -1:
                    return InterfaceError(message)
            for key in programming_exceptions:
                if message.find(key) != -1:
                    return ProgrammingError(message)
            for key in operational_exceptions:
                if message.find(key) != -1:
                    return OperationalError(message)
            for key in database_exceptions:
                if message.find(key) != -1:
                    return DatabaseError(message)  
            for key in statement_exceptions:
                if message.find(key) != -1:
                    return DatabaseError(message)
            return Error(message)
    else:
        return Error('An error has occured')

    # First check if the SQLSTATE is in the tuples, if not check
    # if the SQLSTATE class code is in the tuples to determine the
    # exception type. 
    if error_code in warining_error_tuple:
        return Warning(message)
    if error_code in data_error_tuple:
        return DataError(message)
    if error_code in operational_error_tuple:
        return OperationalError(message)
    if error_code in integrity_error_tuple:
        return IntegrityError(message)
    if error_code in internal_error_tuple:
        return InternalError(message)
    if error_code in programming_error_tuple:
        return ProgrammingError(message)
    if error_code in not_supported_error_tuple:
        return NotSupportedError(message)

    prefix_code = error_code[:2]
    if prefix_code in warining_error_tuple:
        return Warning(message)
    if prefix_code in data_error_tuple:
        return DataError(message)
    if prefix_code in operational_error_tuple:
        return OperationalError(message)
    if prefix_code in integrity_error_tuple:
        return IntegrityError(message)
    if prefix_code in internal_error_tuple:
        return InternalError(message)
    if prefix_code in programming_error_tuple:
        return ProgrammingError(message)
    if prefix_code in not_supported_error_tuple:
        return NotSupportedError(message)

    return DatabaseError(message)

def connect(dsn, user='', password='', host='', database='',
                                                           conn_options=None):
    """This method creates a connection to the database.  It returns 
    a Connection object.

    """
    if dsn is None:
        raise InterfaceError("connect expects a not None dsn value") 
    if (not isinstance(dsn, types.StringType)) | \
                              (not isinstance(user, types.StringType)) | \
                              (not isinstance(password, types.StringType)) | \
                              (not isinstance(host, types.StringType)) | \
                              (not isinstance(database, types.StringType)):

        raise InterfaceError("connect expects the first five arguments to "
                                                          "be of type string")
    if conn_options is not None:
        if not isinstance(conn_options, dict):
            raise InterfaceError("connect expects the sixth argument "
                                          "(conn_options) to be of type dict")
        if not SQL_ATTR_AUTOCOMMIT in conn_options:
            conn_options[SQL_ATTR_AUTOCOMMIT] = SQL_AUTOCOMMIT_ON
    else:
        conn_options = {SQL_ATTR_AUTOCOMMIT : SQL_AUTOCOMMIT_ON}

    # If the dsn does not contain port and protocal adding database
    # and hostname is no good.  Add these when required, that is,
    # if there is a '=' in the dsn.  Else the dsn string is taken to be
    # a DSN entry.
    if dsn.find('=') != -1:
        if dsn[len(dsn) - 1] != ';':
            dsn = dsn + ";"
        if database != '' and dsn.find('DATABASE=') == -1:
            dsn = dsn + "DATABASE=" + database + ";"
        if host != '' and dsn.find('HOSTNAME=') == -1:
            dsn = dsn + "HOSTNAME=" + host + ";"
    else:
        dsn = "DSN=" + dsn + ";"

    if user != '' and dsn.find('UID=') == -1:
        dsn = dsn + "UID=" + user + ";"
    if password != '' and dsn.find('PWD=') == -1:
        dsn = dsn + "PWD=" + password + ";"
        
    try:    
        conn = ibm_db.connect(dsn, '', '', conn_options) 
    except Exception, inst:
        raise _get_exception(inst)

    return Connection(conn)


class Connection(object):
    """This class object represents a connection between the database 
    and the application.

    """
    def __init__(self, conn_handler):
        """Constructor for Connection object. It takes ibm_db 
        connection handler as an argument. 

        """
        self.conn_handler = conn_handler

        # Used to identify close cursors for generating exceptions 
        # after the connection is closed.
        self._cursor_list = []

    def close(self):
        """This method closes the Database connection associated with
        the Connection object.  It takes no arguments.

        """
        self.rollback()
        try:
            return_value = ibm_db.close(self.conn_handler)
        except Exception, inst:
            raise _get_exception(inst)
        self.conn_handler = None
        for index in range(len(self._cursor_list)):
            self._cursor_list[index].conn_handler = None
            self._cursor_list[index].stmt_handler = None
            self._cursor_list[index]._all_stmt_handlers = None
        return return_value

    def commit(self):
        """This method commits the transaction associated with the
        Connection object.  It takes no arguments.

        """
        try:
            return_value = ibm_db.commit(self.conn_handler)
        except Exception, inst:
            raise _get_exception(inst)
        return return_value

    def rollback(self):
        """This method rollbacks the transaction associated with the
        Connection object.  It takes no arguments.

        """
        try:
            return_value = ibm_db.rollback(self.conn_handler)
        except Exception, inst:
            raise _get_exception(inst)
        return return_value

    def cursor(self):
        """This method returns a Cursor object associated with the 
        Connection.  It takes no arguments.

        """
        if self.conn_handler is None:
            raise _get_exception(Exception('Connection is not active'))
        cursor = Cursor(self.conn_handler)
        self._cursor_list.append(cursor)
        return cursor

class Cursor(object):
    """This class represents a cursor of the connection.  It can be
    used to process an SQL statement. 

    """
    # This method is used to get the description attribute.
    def __get_description(self):

        # If this method has already been called, after executing a 
        # select statement, return the stored information in the 
        # self.__description. 
        if self.__description is not None:
            return self.__description 

        self.__description = []
        if self.stmt_handler is None:
            return None
        try:
            num_columns = ibm_db.num_fields(self.stmt_handler)
            # If the execute statement did not produce a result set 
            # return None.
            if num_columns == False:
                return None
            for column_index in range(num_columns):
                column_desc = []
                column_desc.append(ibm_db.field_name(self.stmt_handler,
                                                                column_index))
                type = ibm_db.field_type(self.stmt_handler, column_index)
                type = type.upper()
                if STRING.__cmp__(type) == 0:
                    column_desc.append(STRING)
                if BINARY.__cmp__(type) == 0:
                    column_desc.append(BINARY)
                if NUMBER.__cmp__(type) == 0:
                    column_desc.append(NUMBER)
                if DATETIME.__cmp__(type) == 0:
                    column_desc.append(DATETIME)
                if ROWID.__cmp__(type) == 0:
                    column_desc.append(ROWID)
                column_desc.append(ibm_db.field_display_size(
                                             self.stmt_handler, column_index))

                column_desc.append(None)
                column_desc.append(ibm_db.field_precision(
                                             self.stmt_handler, column_index))

                column_desc.append(ibm_db.field_scale(self.stmt_handler,
                                                                column_index))

                column_desc.append(None)
                self.__description.append(column_desc)
        except Exception, inst:
            raise _get_exception(inst)

        return self.__description

    # This attribute provides the metadata information of the columns  
    # in the result set produced by the last execute function.  It is
    # a read only attribute.
    description = property(fget = __get_description)

    # This method is used to get the rowcount attribute. 
    def __get_rowcount( self ):
        return self.__rowcount

    # This attribute specifies the number of rows the last executeXXX()
    # produced or affected.  It is a read only attribute. 
    rowcount = property(__get_rowcount, None, None, "")

    def __init__(self, conn_handler):
        """Constructor for Cursor object. It takes ibm_db connection 
        handler as an argument.

        """
        # This attribute is used to determine the fetch size for fetchmany
        # operation. It is a read/write attribute
        self.arraysize = 1
        self.__rowcount = -1
        self._result_set_produced = False
        self.__description = None
        self.conn_handler = conn_handler
        self.stmt_handler = None

    # This method closes the statemente associated with the cursor object.
    # It takes no argument.
    def close(self):
        """This method closes the cursor object.  After this method is 
        called the cursor object is no longer usable.  It takes no
        arguments.

        """
        if self.conn_handler is None:
            raise _get_exception(Exception('Connection is not active'))
        try:
            return_value = ibm_db.free_stmt(self.stmt_handler)
        except Exception, inst:
            raise _get_exception(inst)
        self.stmt_handler = None
        self.conn_handler = None
        self._all_stmt_handlers = None
        return return_value

    def callproc(self, procname, parameters=None):
        """This method can be used to execute a stored procedure.  
        It takes the name of the stored procedure and the parameters to
        the stored procedure as arguments. 

        """
        if not isinstance(procname, types.StringType):
            raise InterfaceError("callproc expects the first argument to " 
                                                       "be of type String.")
        if parameters is not None:
            if not isinstance(parameters, (types.ListType, types.TupleType)):
                raise InterfaceError("callproc expects the second argument"
                                       " to be of type list or tuple.")

        sql_operation = "CALL " + procname + "("
        if parameters is not None:
            prefix_comma = False
            for index in parameters:
                if prefix_comma == False:
                    sql_operation = sql_operation + "?"
                    prefix_comma = True
                else:
                    sql_operation = sql_operation + ", ?"
        sql_operation = sql_operation + ")"
        self._result_set_produced = True
        return self.execute(sql_operation, parameters)

    # Helper for preparing an SQL statement. 
    def _prepare_helper(self, operation, parameters=None):
        try:
            self.stmt_handler = ibm_db.prepare(self.conn_handler, operation)
        except Exception, inst:
            raise _get_exception(inst)

    # Helper for executing an SQL statement.
    def _execute_helper(self, parameters=None):
        if parameters is not None:
            parameters = list(parameters)
            # Convert date/time and binary objects to string for 
            # inserting into the database. 
            for index in range(len(parameters)):
                if isinstance(parameters[index], (datetime.datetime,
                                     datetime.date, datetime.time)):
                    parameters[index] = str(parameters[index])
                if isinstance(parameters[index], buffer):
                    parameters[index] = str(parameters[index])
            parameters = tuple(parameters)
            try:
                return_value = ibm_db.execute(self.stmt_handler, parameters)
            except Exception, inst:
                raise _get_exception(inst)
        else:
            try:
                return_value = ibm_db.execute(self.stmt_handler)
            except Exception, inst:
                raise _get_exception(inst)
        return return_value

    # This method is used to set the rowcount after executing an SQL 
    # statement. 
    def _set_rowcount(self, operation):
        queryType = operation[0 : 6]
        if (queryType.lower() == 'select') & \
                                     (operation.lower().find('from') != -1):
            temp_operation = operation[0 : 6] + ' COUNT(*)' \
                                 + operation[operation.lower().find('from') :]
            try:
                temp_stmt = ibm_db.exec_immediate(self.conn_handler,
                                                              temp_operation)
                count_row_tuple = ibm_db.fetch_tuple(temp_stmt)
            except Exception, inst:
                raise _get_exception(inst)

            self.__rowcount = count_row_tuple[0]
            self._result_set_produced = True
            return True
        else:
            try:
                return_value = ibm_db.num_rows(self.stmt_handler)
            except Exception, inst:
                raise _get_exception(inst)
            self.__rowcount = return_value
            return True


    def execute(self, operation, parameters=None):
        """This method can be used to prepare and execute an SQL 
        statement.  It takes the SQL statement(operation) and a 
        sequence of values to substitute for the parameter markers in  
        the SQL statement as arguments.

        """
        if not isinstance(operation, types.StringType):
            raise InterfaceError("execute expects the first argument to"
                                                       " be of type String.")
        if parameters is not None:
            if not isinstance(parameters, (types.ListType, types.TupleType)): 
                raise InterfaceError("execute expects the second argument"
                                       " to be of type list or tuple.")
        self.__description = None
        self._all_stmt_handlers = []
        self._prepare_helper(operation)
        self._execute_helper(parameters)
        return self._set_rowcount(operation)


    def executemany(self, operation, seq_parameters):
        """This method can be used to prepare, and then execute an SQL 
        statement many times.  It takes the SQL statement(operation) 
        and sequence of sequence of values to substitute for the 
        parameter markers in the SQL statement as its argument.

        """
        if not isinstance(operation, types.StringType):
            raise InterfaceError("executemany expects the first argument "
                                                    "to be of type String.")
        if seq_parameters is None:
            raise InterfaceError("executemany expects a not None "
                                  "seq_parameters value")

        if not isinstance(seq_parameters, (types.ListType, types.TupleType)):
            raise InterfaceError("executemany expects the second argument "
                                  "to be of type list or tuple of sequence.")

        self.__description = None
        self._all_stmt_handlers = []
        self._prepare_helper(operation)
        for index in range(len(seq_parameters)):
            self._execute_helper(seq_parameters[index])
        return self._set_rowcount(operation)

    # This method is a helper function for fetching fetch_size number 
    # of rows, after executing an SQL statement which produces a result
    # set.  It takes the number of rows to fetch as an argument.  If 
    # this is not provided it fetches all the remaining rows. 
    def _fetch_helper(self, fetch_size=-1):
        if self.stmt_handler is None:
            raise ProgrammingError("Please execute an SQL statement in "
                                      "order to get a row from result set.")
        if self._result_set_produced == False:
            raise  ProgrammingError("The last call to execute did not "
                                                    "produce any result set.")

        row_list = []
        rows_fetched = 0
        while (fetch_size == -1) or (fetch_size != -1 and 
                                                   rows_fetched < fetch_size):
            try:
                row = ibm_db.fetch_tuple(self.stmt_handler)
            except Exception, inst:
                raise _get_exception(inst)
            if row != False:
                row_list.append(self._fix_return_data_type(row))
            else:
                return row_list
            rows_fetched = rows_fetched + 1

        return row_list


    def fetchone(self):
        """This method fetches one row from the database, after 
        executing an SQL statement which produces a result set.

        """
        row_list = self._fetch_helper(1)
        if len(row_list) == 0:
            return None
        else:
            return row_list[0]

    def fetchmany(self, size=0):
        """This method fetches size number of rows from the database,
        after executing an SQL statement which produces a result set.
        It takes the number of rows to fetch as an argument.  If this 
        is not provided it fetches self.arraysize number of rows. 

        """
        if not isinstance(size, (int, long)):
            raise InterfaceError( "fetchmany expects the first argument " 
                                    "to be of type int or long.")
        if size == 0:
            size = self.arraysize
        if size < -1:
            raise ProgrammingError("The argument size should be greater "
                                         "than zero for fetchmany operation.")

        return self._fetch_helper(size)

    def fetchall(self):
        """This method fetches all remaining rows from the database,
        after executing an SQL statement which produces a result set.

        """
        return self._fetch_helper()

    def nextset(self):
        """This method can be used to get the next result set after 
        executing a stored procedure, which produces multiple result sets.

        """
        if self.stmt_handler is None:
            raise ProgrammingError("Please execute an SQL statement in "
                                                 "order to get result sets.")
        if self._result_set_produced == False:
            raise  ProgrammingError("The last call to execute did not "
                                                    "produce any result set.")
        try:
            # Store all the stmt handler that were created.  The 
            # handler was the one created by the execute method.  It 
            # should be used to get next result set. 
            self._all_stmt_handlers.append(self.stmt_handler)
            self.stmt_handler = ibm_db.next_result(self._all_stmt_handlers[0])
        except Exception, inst:
            raise _get_exception(inst)

        if self.stmt_handler == False:
            self.stmt_handler = None
        if self.stmt_handler == None:
            return None 
        return True

    def setinputsizes(self, sizes):
        """This method currently does nothing."""
        pass

    def setoutputsize(self, size, column=-1):
        """This method currently does nothing."""
        pass

    # This method is used to convert a string representing date/time 
    # and binary data in a row tuple fetched from the database 
    # to date/time and binary objects, for returning it to the user.
    def _fix_return_data_type(self, row):
        row = list(row)
        for index in range(len(row)):
            if row[index] is not None:
                type = ibm_db.field_type(self.stmt_handler, index)
                type = type.upper()

                try:
                    if type == 'TIMESTAMP':
                        # strptime() method does not support 
                        # microsecond format. 
                        microsec = 0
                        if row[index][20:] != '':
                            microsec = int(row[index][20:])
                            row[index] = row[index][:19]
                        row[index] = datetime.datetime.strptime(row[index],
                                                          '%Y-%m-%d %H:%M:%S')
                        row[index] = row[index].replace(
                                                       microsecond = microsec)
                    if type == 'DATE':
                        row[index] = datetime.datetime.strptime(row[index], 
                                                            '%Y-%m-%d').date()
                    if type == 'TIME':
                        row[index] = datetime.datetime.strptime(row[index],
                                                            '%H:%M:%S').time()
                    if type == 'BLOB':
                        row[index] = buffer(row[index])
                except Exception, inst:
                    raise DataError("The date and/or time format in the "
                               "database table is not the default db2 format")
        return row


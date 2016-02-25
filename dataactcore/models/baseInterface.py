import sqlalchemy
import json
import os
import inspect
from flask import _app_ctx_stack
from sqlalchemy.orm import sessionmaker , scoped_session
from sqlalchemy.orm.exc import NoResultFound,MultipleResultsFound
from dataactcore.utils.responseException import ResponseException
from dataactcore.utils.statusCode import StatusCode

class BaseInterface(object):
    """ Abstract base interface to be inherited by interfaces for specific databases
    """
    #For Flask Apps use the context for locals
    IS_FLASK = True
    dbConfigFile = None # Should be overwritten by child classes
    dbName = None # Should be overwritten by child classes
    credFileName = None

    def __init__(self):
        if(self.session != None):
            # session is already set up for this DB
            return

        if(self.dbConfigFile == None or self.dbName == None):
            # Child class needs to set these before calling base constructor
            raise ValueError("Need dbConfigFile and dbName defined")
        # Load config info
        confDict = json.loads(open(self.dbConfigFile,"r").read())

        # Create sqlalchemy connection and session
        self.engine = sqlalchemy.create_engine("postgresql://" + confDict["username"] + ":" + confDict["password"] + "@" + confDict["host"] + ":" + confDict["port"] + "/" + self.dbName,pool_size=100,max_overflow=50)
        self.connection = self.engine.connect()
        if(self.Session == None):
            if(BaseInterface.IS_FLASK) :
                self.Session = scoped_session(sessionmaker(bind=self.engine,autoflush=True),scopefunc=_app_ctx_stack.__ident_func__)
            else :
                self.Session = scoped_session(sessionmaker(bind=self.engine,autoflush=True))
        self.session = self.Session()

    def __del__(self):
        try:
            #Close session
            self.session.close()
            #self.Session.close_all()
            self.Session.remove()
            self.connection.close()
            self.engine.dispose()
        except KeyError:
            # KeyError will occur in Python 3 on engine dispose
            pass

    @classmethod
    def getCredDict(cls):
        """ Gets credentials dictionary """
        return json.loads(open(cls.getCredFilePath(),"r").read())

    @classmethod
    def getCredFilePath(cls):
        """  Returns full path to credentials file """
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        lastBackSlash = path.rfind("\\",0,-1)
        lastForwardSlash = path.rfind("/",0,-1)
        lastSlash = max([lastBackSlash,lastForwardSlash])
        return path[0:lastSlash] + "/credentials/" + cls.credFileName

    @staticmethod
    def checkUnique(queryResult, noResultMessage, multipleResultMessage):
        """ Check that result is unique, if not raise exception"""
        if(len(queryResult) == 0):
            # Did not get a result for this job, mark as a job error
            raise ResponseException(noResultMessage,StatusCode.CLIENT_ERROR,NoResultFound,10)

        elif(len(queryResult) > 1):
            # Multiple results for single job ID
            raise ResponseException(multipleResultMessage,StatusCode.INTERNAL_ERROR,MultipleResultsFound,10)

        return True

    @staticmethod
    def runUniqueQuery(query, noResultMessage, multipleResultMessage):
        """ Run query looking for one result, if it fails wrap it in a ResponseException with an appropriate message """
        try:
            return query.one()
        except NoResultFound as e:
            if(noResultMessage == False):
                # Raise the exception as is, used for specific handling
                raise e
            raise ResponseException(noResultMessage,StatusCode.CLIENT_ERROR,NoResultFound,10)
        except MultipleResultsFound as e:
            raise ResponseException(multipleResultMessage,StatusCode.INTERNAL_ERROR,MultipleResultsFound,10)

    def runStatement(self,statement):
        """ Run specified statement on this database"""
        response =  self.session.execute(statement)
        self.session.commit()
        return response

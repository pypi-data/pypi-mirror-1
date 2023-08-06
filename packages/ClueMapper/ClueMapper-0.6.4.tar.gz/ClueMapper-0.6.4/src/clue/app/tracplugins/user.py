import traceback
from StringIO import StringIO
import time
from trac import core
from trac import config
from trac.db import api as dbapi
from tracusermanager import api as umapi
from trac.util.translation import _


class ClueMapperDatabaseManager(dbapi.DatabaseManager):

    connection_uri = config.Option('cluemapper', 'database',
        'sqlite:etc/cluemapper/cluemapper.db',
        """Database connection
        [wiki:TracEnvironment#DatabaseConnectionStrings string] for this
        project""")

    timeout = config.IntOption('cluemapper', 'timeout', '20',
        """Timeout value for database connection, in seconds.
        Use '0' to specify ''no timeout''. ''(Since 0.11)''""")


class ClueMapperUserStore(core.Component):
    core.implements(umapi.IUserStore)

    def __init__(self):
        self.dbm = ClueMapperDatabaseManager(self.compmgr)

    def get_supported_user_operations(self, username):
        return []

    def execute_user_operation(self, operation, user, operation_arguments):
        return True

    def create_user(self, username):
        db = self.dbm.get_connection()
        cursor = db.cursor()

        try:
            cursor.execute("DELETE FROM user_info WHERE "
                           "username=%s AND name='created'", [username])
            cursor.execute('INSERT INTO user_info (username, name, value) '
                           'VALUES (%s,%s,%s)',
                           [username, 'created', int(time.time())])
            db.commit()
        except Exception, e:
            self.log.debug("User already exists, no need to re-create it."
                           % (username))

    def search_users(self, username_pattern=None):
        db = self.dbm.get_connection()
        cursor = db.cursor()
        search_result = []

        try:
            if username_pattern is None:
                cursor.execute("SELECT username FROM user_info "
                               "WHERE name='created'")
            else:
                cursor.execute("SELECT username FROM user_info "
                               "WHERE name='created' AND username LIKE %s",
                               username_pattern)
            for username, in cursor:
                search_result.append(username)
        except Exception, e:
            out = StringIO()
            traceback.print_exc(file=out)
            self.log.error('%s: %s\n%s' % (self.__class__.__name__,
                                           str(e), out.getvalue()))
            raise core.TracError(("Unable to search users [%s].")
                                 % (username_pattern))

        return search_result

    def delete_user(self, username):
        db = self.dbm.get_connection()
        cursor = db.cursor()

        try:
            cursor.execute('DELETE FROM '
                           'user_info '
                           'WHERE username=%s', [username])
            db.commit()
            return True

        except Exception, e:
            out = StringIO()
            traceback.print_exc(file=out)
            self.log.error('%s: %s\n%s' % (self.__class__.__name__,
                                           str(e), out.getvalue()))
            raise core.TracError(_("Unable to delete user [%s].")%(username))
            return False


class ClueMapperAttributeProvider(core.Component):
    core.implements(umapi.IAttributeProvider)

    def __init__(self):
        self.dbm = ClueMapperDatabaseManager(self.compmgr)

    def get_user_attribute(self, username, attribute):
        db = self.dbm.get_connection()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT value FROM user_info "
                           "WHERE username=%s AND name=%s", (username,
                                                             attribute))

            _result = list(cursor)
            if len(_result)>0:
                return _result[0][0]
        except Exception, e:
            out = StringIO()
            traceback.print_exc(file=out)
            self.log.error('%s: %s\n%s' % (self.__class__.__name__,
                                           str(e), out.getvalue()))
            raise core.TracError(_("Unable to load attribute %s for user "
                                   "[%s].") % (attribute, username))

        return None

    def set_user_attribute(self, username, attribute, value):
        """Sets user's attribute value.

        @param username: str 
        @param attribute: str
        @param value: str
        @return: bool
        """
        db = self.dbm.get_connection()
        cursor = db.cursor()
        
        try:
            
            cursor.execute("DELETE FROM user_info "
                           "WHERE username=%s AND name=%s",
                           [username, attribute])
            
            cursor.execute("INSERT INTO user_info "
                           "(username, name, value) VALUES (%s, %s, %s)",
                           [username, attribute, value])
            db.commit()
            
            return True
        except Exception, e:
            out = StringIO()
            traceback.print_exc(file=out)
            self.log.error('%s: %s\n%s' % (self.__class__.__name__,
                                           str(e), out.getvalue()))
            raise core.TracError("Unable to set attribute %s for "
                                 "user [%s]."%(attribute, username))
        
        return False
    
    def delete_user_attribute(self, username, attribute):
        """Removes user attribute.
        
        @param username: str
        @param attribute: str
        @return: bool 
        """
        db = self.dbm.get_connection()
        cursor = db.cursor()
        
        try:
            
            cursor.execute("DELETE FROM user_info "
                           "WHERE username=%s and name=%s",
                           [username, attribute])
            db.commit()
            
            return True
        except Exception, e:
            out = StringIO()
            traceback.print_exc(file=out)
            self.log.error('%s: %s\n%s' % (self.__class__.__name__,
                                           str(e), out.getvalue()))
            raise core.TracError("Unable to delete attribute %s "
                                 "for user [%s]."%(attribute, username))
        
        return False

    def get_usernames_with_attributes(self, attributes_dict=None):
        """ Returns all usernames matching attributes_dict.
        
        Example: self.get_usernames_with_attributes(dict(name='John%', email='%'))
        
        @param attributes_dict: dict
        @return: list
        """
        db = self.dbm.get_connection()
        cursor = db.cursor()
        
        try:                     
            if attributes_dict is None:
                cursor.execute("SELECT username FROM user_info")
            else:
                """@note: [TO DO] Redo this query in order to avoid SQL Injection!
                The following line executes a query that should look like this:
                
                    (for dict(name='John%', email='%@exemple.com')):
                        SELECT  sid, 
                                count(sid) cnt 
                        FROM session_attribute 
                        WHERE name='name' AND value like 'John%' 
                           OR name='email' AND value like '%@exemple.com' 
                        GROUP BY sid 
                        HAVING cnt=2                
                """

                def _get_condition(k, v):
                    is_not = k.startswith('NOT_')
                    return "name='%s' AND value %sLIKE '%s'"%(is_not and k[4:] or k, is_not and 'NOT ' or '', v)
                cursor.execute("SELECT username, count(username) cnt FROM user_info WHERE %s GROUP BY username HAVING cnt=%s"%
                                 (" OR ".join([ _get_condition(k,v)
                                                for k,v in attributes_dict.items()]), len(attributes_dict.items())))
                
            return [id for id, cnd in cursor]
        except Exception, e:
            out = StringIO()
            traceback.print_exc(file=out)
            self.log.error('%s: %s\n%s' % (self.__class__.__name__, str(e), out.getvalue()))
            return []

#!/usr/bin/env python
# License: PSF
# see: LICENSE
# for full text of the license
#
import SOAPpy
import md5
import xml
from pytz import timezone
import datetime
import base64
import urllib2
from pysugar_version import version, major_version, minor_version, mid_version

__version__ = version
__author__ = "Florent Aide"
__doc__ = '''This is the transport layer for the pysugar library.
It uses SOAPpy in order to communicate with the Sugar NuSoap Server.
'''
#selection = SOAPpy.structType(
#        [ 'id', ]
#        )

def item_to_name_value(item):
    '''
    takes a real item dictionnary and prepare it for soap
    returns a name value formated list of dictionnaries
    '''
    nv_list = []
    for key in item:
        nv_list.append({'name':key, 'value':item[key]})
    
    return nv_list
        
class SugarError(Exception):
    '''
    This is the base class for our errors
    '''
    pass

class SugarOperationnalError(SugarError):
    '''
    when some unknow & weird error occurs
    '''
    pass

class SugarLoginError(SugarError):
    '''
    When a login error occurs, we raise this one
    '''
    pass

class SugarCredentialError(SugarError):
    '''
    When a function call requiring a valid session id is call without
    one, this exception will be raised
    '''
    pass

class SugarVersionError(SugarError):
    '''
    If an error occurs on the version number
    '''
    pass

class SugarConnectError(SugarError):
    '''
    any connection error
    '''
    pass

class SugarDataError(SugarError):
    '''
    An error where the data from the server does not macth what we
    were expecting.
    '''
    pass

class SugarSession:
    '''
    This class is the entry point to the rest of the API.
    A Sugar Session is the first thing we need in order to
    communicate with the Sugar Server.
    When we have a session all other requests to the server will
    be called on the session object.
    '''
    def __init__(self, username, password, base_url,
            debug=False, user_management=False):
        '''
        username: a string representing the login
        password: a string with the password for the login
        base_url: a string containing the url for the sugar server
                without the soap.php?wsdl trailer
        debug: a boolean, False by default
        user_management: a boolean, False by default
        
        example:
            s = SugarSession('myuser', 'mypass', 'http://myserver/sugar')
        
        Here s should be a pysugar.SugarSession object ready to be used
        '''
        self.user_management = user_management
        self._session_id = False
        self._debug = debug

        if debug:
            SOAPpy.Config.debug = 1

        self.base_url = base_url
        self.application_name = 'pysugar'
        soap_url = base_url + '/soap.php?wsdl'
        user_url = base_url + '/soap_users.php?wsdl'
        
        try:
            urllib2.urlopen(soap_url)
        except urllib2.HTTPError, e:
            msg = "Can't resolve %s." % e.geturl()
            raise SugarConnectError(msg)

        if user_management:
            try:
                urllib2.urlopen(user_url)
            except urllib2.HTTPError, e:
                msg = "Can't resolve %s.\n" % e.geturl()
                msg += "Maybe you should deploy the soap_users.php script ?"
                raise SugarConnectError(msg)

        try:
            self.soap_proxy = SOAPpy.WSDL.Proxy(soap_url)

        except xml.parsers.expat.ExpatError, args:
            msg = 'Cannot communicate with server,'
            msg += 'please check the url. msg= %s' % args
            raise SugarError(msg)

        if user_management:
            try:
                self.user_proxy = SOAPpy.WSDL.Proxy(user_url)
            except xml.parsers.expat.ExpatError, args:
                msg = 'Cannot communicate with server,'
                msg += 'please check the url. msg= %s' % args
                raise SugarError(msg)

        if not self.test():
            msg = "The Sugar server seems to be offline"
            msg += "or unresponsive"
            raise SugarError(msg)
        else:
            self.login(username, password)


    def login(self, username, password):
        '''
        tries to log into the Sugar server with the given credentials
        '''
        pass_hash = md5.new(password).hexdigest()
        user_auth = SOAPpy.structType({
                        'user_name': username,
                        'password': pass_hash,
                        'version':'1.2'
                        })

        session = self.soap_proxy.login(
                user_auth, application_name = self.application_name
                )

        self._session_id = session.id

        if self._session_id == '-1':
            raise SugarLoginError(
                    'Error when login: %s' % session.error.description 
                    )

        if self._debug:
            print "We are logged-in with session id: '%s'" %\
            self.soap_proxy.get_user_id(session=self._session_id)

    def get_entry_list(
            self,
            module,
            query,
            order_by,
            offset,
            selection,
            max_result,
            deleted):
        '''
        this raw call enables to ask any modules to give its list of data
        '''
        if not self._session_id:
            raise SugarCredentialError(
                    'A valid session id is required to use this method')

        res = self.soap_proxy.get_entry_list(
                self._session_id,
                module,
                query,
                order_by,
                offset,
                selection,
                max_result,
                deleted
                )
    
        next_offset = res.next_offset
        field_list = res.field_list
        module_list = res.entry_list
        errors = res.error
        num_result = res.result_count
    
        my_items = []

        for item in module_list:
            my_items.append(dict(item.name_value_list))

        return my_items

    def get_entry(self, module, id, selection):
        '''
        This method is the way to get entries according to their ids
        '''
        res = self.soap_proxy.get_entry(
                self._session_id,
                module,
                id,
                selection)

        error = res.error
        if not error.number == '0':
            raise SugarError(error.description)

        my_items = []

        for item in res.entry_list:
            my_items.append(dict(item.name_value_list))

        assert len(my_items) == 1 ,\
                'This function cannot return more than one entry'

        return my_items[0]
    
    def set_entry(self, module, item):
        '''
        create a new entry in Sugar
        if an error occurs a SugarError will be raised
        if the operation is a success, a string representing the id of the
        created/modified entry will be returned
        '''
        name_value_list = item_to_name_value(item)
        res = self.soap_proxy.set_entry(
                self._session_id,
                module,
                name_value_list 
                )

        if not res.error.number == '0':
            raise SugarError(res.error.description)

        else:
            return res.id
    
    def set_entries(self, module, items):
        '''
        create a batch of new entries in Sugar for the same module
        '''
        name_value_lists = []
        for item in items:
            name_value_lists.append(item_to_name_value(item))
            
        res = self.soap_proxy.set_entries(
                self._session_id,
                module,
                name_value_lists)

        if not res.error.number == '0':
            raise SugarError(res.error.description)

        else:
            return res
    
    def set_note_attachment(self, note):
        '''
        create a new note attachment in Sugar
        '''
        raise NotImplementedError
    
    def get_note_attachment(self, id):
        '''
        retrieve a note attachement from sugar using its id
        returns the binary content a the file attached to the note
        '''
        res = self.soap_proxy.get_note_attachment(
                self._session_id,
                id
                )

        if not res.error.number == '0':
            raise SugarError(res.error.description)

        else:
            return (
                    base64.b64decode(res.note_attachment.file),
                    res.note_attachment.filename
                    )
    
    def relate_note_to_module(self, note_id, module_name, module_id):
        '''
        ???
        '''
        raise NotImplementedError

    def get_related_notes(self, module_name, module_id, selection):
        '''
        ???
        '''
        raise NotImplementedError

    def logout(self):
        '''
        destroy the given session on the server
        '''
        self.soap_proxy.logout(self._session_id)
    
    def get_user_id(self):
        '''
        given a session this will return a user id string
        if the session is invalid, the returned used id will be '-1'
        '''
        return self.soap_proxy.get_user_id(self._session_id)

    def get_module_fields(self, module_name):
        return self.soap_proxy.get_module_fields(
                self._session_id,
                module_name
                )
                
    def get_available_modules(self):
        '''
        Lists the modules present on the server we are logged in
        '''
        res = self.soap_proxy.get_available_modules(self._session_id)

        error = res.error
        if error.number == '0':
            modules = res.modules
            return list(modules)
        else:
            raise SugarError('%s' % error.description)

    def update_portal_user(self, username, name_value_list):
        '''
        ???
        '''
        raise NotImplementedError
    
    def create_user(self, user_name, password):
        if not self.user_management:
            raise SugarError('User Management is not initialized')

        res = self.user_proxy.create_user(
                self._session_id,
                user_name,
                password)

        if res.id == '-1':
            print res.error
        return res.id

    def test(self):
        '''
        test that the given url responds something we can use
        and the NuSoap php xmlrpc server is indeed present
        '''
        onetest = 'OneStringOfTest'
        res = self.soap_proxy.test(onetest)
        if res == onetest:
            return True
        else:
            return False

    def get_server_time(self):
        '''
        returns the time on the server
        in local time
        '''
        raise NotImplementedError
    
    def get_gmt_time(self):
        '''
        returns the server time in GTM
        the returned time is a datetime.datetime instance in UTC timezone
        the timezone IS specified in the intance using the pytz library
        '''
        res = self.soap_proxy.get_gmt_time()
        utc = timezone('UTC')

        (ymd, hms) = res.split(' ')

        (year, month, day) = ymd.split('-')
        (hour, minute, second) = hms.split(':')

        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        
        return datetime.datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                0,
                tzinfo=utc
                )
    
    def get_server_version(self):
        '''
        returns the version number of the server
        '''
        res = self.soap_proxy.get_server_version()
        if res == '1.0':
            msg = 'The server does not disclose this information'
            raise SugarVersionError(msg)
        else:
            return res

    def get_user_role_ids(self, user_id):
        if not self.user_management:
            raise SugarError('User Management is not initialized')

        return self.user_proxy.get_user_role_ids(
                self._session_id,
                user_id)

    def remove_user_role(self, role_id, user_id):
        if not self.user_management:
            raise SugarError('User Management is not initialized')

        return self.user_proxy.remove_user_role(
                self._session_id,
                role_id,
                user_id)

    def get_relationships(
            self,
            module_name,
            module_id,
            related_module,
            related_module_query,
            deleted):
       return self.soap_proxy.get_relationships(
               self._session_id,
               module_name,
               module_id,
               related_module,
               related_module_query,
               deleted)
        

    def set_relationship(self, set_relationship_value):
        return self.soap_proxy.set_relationship(
                self._session_id,
                set_relationship_value)
            
    def set_relationships(self, set_relationship_list):
        '''
        ???
        '''
        raise NotImplementedError
    
    def set_document_revision(self, document_revision):
        '''
        ???
        '''
        raise NotImplementedError

# vim: expandtab tabstop=4 shiftwidth=4:

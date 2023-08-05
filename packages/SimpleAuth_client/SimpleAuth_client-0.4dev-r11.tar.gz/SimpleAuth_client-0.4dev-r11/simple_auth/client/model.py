import os, sys
from sqlalchemy import *

class UnsupportedError(Exception):
    """simply indicates that an attempted config is not valid"""


class AuthModel(object):
    def __init__(self, db_uri, db_type):
        if db_type.lower() == "mysql":
            from simple_auth.client.mysql_tables import make_tables
        elif db_type.lower() == "oracle":
            from simple_auth.client.oracle_tables import make_tables
        else:
            raise UnsupportedError("Unsupported dbtype %s" % db_type.lower())
        # whichever one we ended up with, run it here
        engine = create_engine(db_uri, pool_recycle=3600)        
        users, services, roles, roles_services, roles_users, resources, resource_users, resource_users_roles = make_tables(engine)

        self.Role.mapper = mapper(self.Role, roles)
        
        self.User.mapper = mapper(self.User, users, properties=dict(
          roles = relation(self.Role, secondary=roles_users, lazy=True),
        ))
        
        self.Service.mapper = mapper(self.Service, services, properties=dict(
          roles = relation(self.Role, secondary=roles_services, lazy=True),
        ))
        
        self.Resource.mapper = mapper(self.Resource, resources)
        
        self.ResourceUser.mapper = mapper(self.ResourceUser, resource_users, properties=dict(
            resource = relation(self.Resource, uselist=False),
            roles = relation(self.Role, secondary=resource_users_roles, lazy=True),
        ))

    class User(object):
        """simple auth user object"""
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
            self.password = kwargs.get('password')
    
    class Service(object):
        """simple auth service object"""
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
        
    
    class Role(object):
        """simple auth service role"""
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
    
    
    class Resource(object):
        """resource object for remote/alternate user sources"""
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
    
    
    class ResourceUser(object):
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
            self.password = kwargs.get('password')


    def authenticate(self, username, password, session=None, resource_name=None):
        if resource_name:
            return self.resource_authenticate(username, password, resource_name, session=session)
        return self.base_authenticate(username, password, session=session)
    
    def authorize(self, servicename, username, rolename, session=None, resource_name=None):
        if resource_name:
            return self.resource_authorize(servicename, username, rolename, resource_name, session=session)
        return self.base_authorize(servicename, username, rolename, session=session)

    def get_roles_for_user(self, servicename, username, session=None, resource_name=None):
        if resource_name:
            return self.resource_get_roles_for_user(servicename, username, resource_name, session=session)
        return self.base_get_roles_for_user(servicename, username, session=session)
    

    def base_authenticate(self, username, password, session=None):
        localSession = False
        if session is None:
            session = create_session()
            localSession = True
        response = None
        user = session.query(self.User).get_by(name=str(username))
        if user:
            if user.password == password:
                response = True
            else:
                response = False
        else:
            response = False
        if localSession:
            session.close()
        return response
    
    
    def base_authorize(self, servicename, username, rolename, session=None):
        localSession = False
        if session is None:
            session = create_session()
            localSession = True
        response = None
        service = session.query(self.Service).get_by(name=str(servicename))
        user = session.query(self.User).get_by(name=str(username))
        role = session.query(self.Role).get_by(name=str(rolename))
        if user and service and role:
            if role in user.roles and role in service.roles:
                response = True
            else:
                response = False
        else:
            response = False
        if localSession:
            session.close()
        return response
    
    
    def base_get_roles_for_user(self, servicename, username, session=None):
        localSession = False
        if session is None:
            session = create_session()
            localSession = True
    
        response = []
        service = session.query(self.Service).get_by(name=str(servicename))
        user = session.query(self.User).get_by(name=str(username))
        
        if service and user:
            for role in service.roles:
                if role in user.roles:
                    response.append(role.name)
    
        if localSession:
            session.close()
        return response
    

    def resource_authenticate(self, username, password, resource_name, session=None):
        localSession = False
        if session is None:
            session = create_session()
            localSession = True
        response = None
    
        resource = session.query(self.Resource).get_by(name=resource_name)
        if resource:
            user = session.query(self.ResourceUser).selectfirst(and_(
                self.ResourceUser.c.resource_id==resource.id,
                self.ResourceUser.c.name==username))
            if user:
                if user.password == password:
                    response = True
                else:
                    response = False
            else:
                response = False
        else:
            response = False
        if localSession:
            session.close()
        return response
    
    
    def resource_authorize(self, servicename, username, rolename, resource_name, session=None):
        localSession = False
        if session is None:
            session = create_session()
            localSession = True
        response = None
        resource = session.query(self.Resource).get_by(name=resource_name)
        user = None
        if resource:
            user = session.query(self.ResourceUser).selectfirst(and_(
                self.ResourceUser.c.resource_id==resource.id,
                self.ResourceUser.c.name==username))
        service = session.query(self.Service).get_by(name=servicename)
        role = session.query(self.Role).get_by(name=rolename)
        if user and service and role:
            if role in user.roles and role in service.roles:
                response = True
            else:
                response = False
        else:
            response = False
        if localSession:
            session.close()
        return response
        
    
    def resource_get_roles_for_user(self, servicename, username, resource_name, session=None):
        localSession = False
        if session is None:
            session = create_session()
            localSession = True
        response = []
        resource = session.query(self.Resource).get_by(name=resource_name)
        user = None
        if resource:
            user = session.query(self.ResourceUser).selectfirst(and_(
                self.ResourceUser.c.resource_id==resource.id,
                self.ResourceUser.c.name==username))
        service = session.query(self.Service).get_by(name=servicename)
    
        if service and user:
            for role in service.roles:
                if role in user.roles:
                    response.append(role.name)
        
        if localSession:
            session.close()
        return response

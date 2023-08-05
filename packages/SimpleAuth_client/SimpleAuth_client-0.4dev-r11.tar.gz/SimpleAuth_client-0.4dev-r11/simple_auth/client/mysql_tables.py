from sqlalchemy import *
import os, sys


def make_tables(engine):
    metadata = BoundMetaData(engine)

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(64), nullable=False, unique=True),
        Column('pass', String(64), nullable=False, key="password"),
    )

    services = Table('services', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(64), nullable=False, unique=True),
    )

    roles = Table('roles', metadata, 
        Column('id', Integer, primary_key=True),
        Column('name', String(64), nullable=False, unique=True),
    )

    roles_services = Table('roles_services', metadata,
        Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
        Column('service_id', Integer, ForeignKey('services.id'), primary_key=True),
    )

    roles_users = Table('roles_users', metadata,
        Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    )
   
    resources = Table('resources', metadata, 
        Column('id', Integer, primary_key=True),
        Column('name', String(64), nullable=False, unique=True),
    )

    resource_users = Table('resource_users', metadata, 
        Column('id', Integer, primary_key=True),
        Column('resource_id', Integer, ForeignKey('resources.id'), nullable=False),
        Column('name', String(64), nullable=False),
        Column('pass', String(64), nullable=False, key="password"),
    )

    resource_users_roles = Table('resource_users_roles', metadata, 
        Column('resource_user_id', Integer, ForeignKey('resource_users.id'), primary_key=True),
        Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    )

    return (users, services, roles, roles_services, roles_users, resources, resource_users, resource_users_roles)

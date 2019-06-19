from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask import Flask, abort, request, jsonify, g, url_for, Response
import uuid

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()
auth = HTTPBasicAuth()

##################
### Validators ###
##################

from jsonschema import validate
import json
import string

# Shared
uuid_regex = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
null = {'type': 'null'}

uuid_schema = {'type': 'string','pattern': uuid_regex}
optional_uuid = {'oneOf': [uuid_schema,null]}

generic_string = {'type': 'string'}
optional_string ={'oneOf': [generic_string,null]}

generic_num = { "type": "number" }
optional_num = {'oneOf': [generic_num,null]}

generic_date = {'type': 'string','format':'date-time'}
optional_date = {'oneOf': [generic_date,null]}

name = {'type': 'string','minLength': 3,'maxLength': 30}
tags = {'type': 'array', 'items': optional_string}
force_to_many = {'type': 'array', 'items': uuid_schema}
to_many = {'type': 'array', 'items': {'oneOf': [uuid_schema,null]}}
#many_to_many = {'anyOf': [{'type': 'array','items': uuid},{'type': 'array','items': null}]}

def schema_generator(properties,required,additionalProperties=False):
    return {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": additionalProperties}
# Protocol things


tags_protocols = db.Table('tags_protocol',
        db.Column('tags_uuid', UUID(as_uuid=True), db.ForeignKey('tags.uuid'), primary_key=True),
    db.Column('protocol_uuid', UUID(as_uuid=True), db.ForeignKey('protocols.uuid'),primary_key=True,nullable=True),
)

class Tag(db.Model):
    __tablename__ = 'tags'
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False,default=sqlalchemy.text("uuid_generate_v4()"), primary_key=True)
    tag = db.Column(db.String)


protocolschema_schema = {
    "uuid": uuid_schema,
    "name": generic_string,
    "description": generic_string,
    "schema": {'type': 'object'}
}
protocolschema_required = ['name','description','schema']
class ProtocolSchema(db.Model):
    validator = schema_generator(protocolschema_schema,protocolschema_required)
    put_validator = schema_generator(protocolschema_schema,[])

    __tablename__ = 'protocolschema'
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False,default=sqlalchemy.text("uuid_generate_v4()"), primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    name = db.Column(db.String())
    description = db.Column(db.String())

    schema = db.Column(db.JSON, nullable=False)

    def toJSON(self,full=None):
        dictionary= {'uuid': self.uuid, 'name': self.name, 'description': self.description, 'schema':self.schema}
        if full=='full':
            pass
        return dictionary


protocol_schema = {
    "uuid": uuid_schema,
    "author": generic_string,
    "description": generic_string,
    "protocol": {'type': 'object'},
    "protocolschema": uuid_schema,
}
protocol_required = ['protocol','protocolschema']
class Protocol(db.Model):
    validator = schema_generator(protocol_schema,protocol_required)
    put_validator = schema_generator(protocol_schema,[])

    __tablename__ = 'protocols'
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False,default=sqlalchemy.text("uuid_generate_v4()"), primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    description = db.Column(db.String())
    protocol = db.Column(db.JSON, nullable=False)

    protocolschema = db.Column(UUID, db.ForeignKey('protocolschema.uuid'), nullable=False)

    tags = db.relationship('Tag', secondary=tags_protocols, lazy='subquery',
        backref=db.backref('protocols', lazy=True))
    def toJSON(self,full=None):
        dictionary= {'uuid': self.uuid, 'description': self.description, 'protocol': self.protocol, 'protocolschema': protocolschema, 'tags':[tag.tag for tag in self.tags]}
        if full=='full':
            pass
        return dictionary



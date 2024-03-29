#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask_expects_json import expects_json # Json schema

from flask_restplus import Api, Resource, fields
from flask.views import MethodView

from flask_migrate import Migrate

import json
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy
from sqlalchemy.sql import func
from flask_cors import CORS

from .config import *

from .models import db

from .routes import ns_token, ns_protocol, ns_protocolschema

# initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# extensions
CORS(app)
db.init_app(app)
auth = HTTPBasicAuth()
authorizations = {
        'token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'token'}
        }
api = Api(app, version='1.1', title=API_TITLE,
            description=API_DESCRIPTION,
            authorizations=authorizations
            )

migrate = Migrate(app, db)


namespaces = [ns_token, ns_protocol, ns_protocolschema]
for ns in namespaces:
    api.add_namespace(ns)



import os
import pickle

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request


def create_app(test_config = None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',     # Should be overridden with random value once deployed
    )

    if test_config == None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent = True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return "Hello World!"

    from . import forms

    from . import home
    app.register_blueprint(home.bp)

    return app
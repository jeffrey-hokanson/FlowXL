#! /usr/bin/python

from distutils.core import setup

setup(name='FlowXL',
		version = '0.1',
		description = 'Web app for using the t-SNE embedding',
		author = 'Jeffrey M. Hokanson',
		author_email = 'jeffrey@hokanson.us',
		url = '',
	)

# Initialize the database

from app import db
db.create_all()


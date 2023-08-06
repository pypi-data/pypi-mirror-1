#!/usr/bin/env python

import os, sys, os.path

import jinja2
import coffin

from django.conf import settings

from django.shortcuts import render_to_string

def relative_path(*args):
    return os.path.abspath(os.path.join(settings.SPHINX_ROOT, *args))

context = {
    'DATABASE_HOST': settings.DATABASE_HOST,
    'DATABASE_PASSWORD': settings.DATABASE_PASSWORD,
    'DATABASE_USER': settings.DATABASE_USER,
    'DATABASE_PORT': settings.DATABASE_PORT,
    'DATABASE_NAME': settings.DATABASE_NAME,
    'SPHINX_HOST': settings.SPHINX_HOST,
    'SPHINX_PORT': settings.SPHINX_PORT,
    'relative_path': relative_path,
}

print render_to_string('conf/sphinx.conf', context)

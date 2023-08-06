====================
emencia.django.links
====================

Introduction
============

emencia.django.links is a django standalone app that provide a web link's
collection.

Features
========

    - add title and description to a web link
    - classify by language
    - classify by categories
    - published features (start-end publish date, visibility status)
    - standart view
    - template tag that get the x last entries

Installation
============

1) With easy_install::

    # easy_install emencia.django.links

2) Python install::
    
    # python setup.py install

You could retrive source from the pypi or bitbucket:

    - http://bitbucket.org/rage2000/emencia.django.links
    - http://pypi.python.org/pypi/emencia.django.links

Instructions
============

    - Install the package in your python sys path
    - Add the app 'emencia.django.links' in the settings.py django project's file
    - Import urls into your root urls.py file:: 
	
	(r'^links/', include('emencia.django.links.urls')),

    - For use the template tag simply load links_monitoring and use get_latest_links tag.
      The syntaxe is {% get_latest_links number_of_links as variable_name %}::

	{% load links_monitoring %}
        {% get_latest_links 2 as last_link %}
        {% for link in last_link %}
            <span><a href="{{ link.url }}">{{ link.title }}</a></span>
        {% endfor %}


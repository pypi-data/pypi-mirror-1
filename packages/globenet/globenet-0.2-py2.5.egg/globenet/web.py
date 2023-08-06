#!/usr/bin/env python
#-*- coding: utf-8 -*-
# globenet - Lightweight web framework for Google(tm) App Engine 
# Version 1.1
#
# Copyright (C) 2008 Tristan Straub (tristanstraub@gmail.com)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from __future__ import with_statement

import sys, logging, inspect, os
import wsgiref.handlers, urllib, urlparse

import google.appengine.api.users
from google.appengine.ext import webapp
from google.appengine.api import users

import routes
from routes import Mapper, url_for 
import mako
import mako.template
from mako.lookup import TemplateLookup

from exceptions import *
from tinyaspect import aspect

import yaml

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)

class HeaderAttribute(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value

@aspect()
def debug(message):
	logging.debug(message)

@aspect()
def loggedin(isadmin = False, redirect = True):
		if not users.get_current_user() or (redirect and isadmin and not users.is_current_user_admin() ):
			raise RequireLogin()

@aspect(aspect.MODIFY)
def header(output, name, value):
	return [HeaderAttribute(self.name, self.value)] + output
	
def add_standard(d):
		d['url_for'] = url_for
		d['users'] = users

def template_mako(output, filename=None, content=None, lookup=None):
		add_standard(output)
		
		if filename:
			if lookup:
				if instanceof(lookup, TemplateLookup):
					templatelookup = lookup
				else:
					templatelookup = TemplateLookup(directories=dirs, output_encoding='utf-8', encoding_errors='replace')
			else:
				templatelookup = TemplateLookup(directories=[os.path.dirname(filename)], output_encoding='utf-8', encoding_errors='replace')
			
			with open(filename,'r') as f:
				content = f.read()
			t = mako.template.Template(content, lookup=templatelookup)
		else:
			t = mako.template.Template(content)
		return [t.render(**output)]

@aspect(aspect.MODIFY)
def template(output, filename=None, content=None, engine='mako'):
	if engine=='mako':
		return template_mako(output, filename, content)
	elif engine=='kid':
		return template_kid(output, filename, content)

@aspect(aspect.ATTACH)
def connect(cls, f, *args, **kw):
		if not hasattr(cls, '_addresses'):
			logging.debug('%s didnt have _addresses' % cls)
			cls._addresses = []

			def _bindaddresses(cls, mapper, prefix = None, cprefix = None):
				prefix = (prefix and (prefix + '/')) or ''
				cprefix = (cprefix and (cprefix + '/')) or ''
				
				for c, f, args, kw in cls._addresses:
					args = list(args)
					i = len(args)-1
					args[i] = prefix + cprefix + args[i]

					logging.debug('binding: %s:%s %s %s' % (c.__name__, f.__name__, args, kw))
					mapper.connect(controller=c.__name__, action=f.__name__, *args, **kw)

			cls._bindaddresses = classmethod(_bindaddresses)
		else:
			logging.debug('%s already had _addresses' % cls)
		logging.debug('connect %s %s %s %s' % (cls,f,args,kw))
		cls._addresses.append((cls, f, args, kw))

class ErrorController(object):
	@connect('error404','error404')
	def notfound(self, *args, **kw):
		return ['<html><body>Page not found!!</body></html>']

	@template(content='<html><body>There was an undefined error!</body></html>')
	@connect('error_index','error')
	def index(self):
		return {}

class DebugController(object):
	@connect('debug','debug')
	@template(content='test ${data}')
	def index(self):
		return {'data':'test!_data'}

class Application(webapp.RequestHandler):
	def __init__(self):
		super(Application, self).__init__()

		logging.debug('Creating application')

		with open('config.ini', 'r') as f:
			config = yaml.load(f.read())

		self.controllers = []

		if 'controllers' in config:
			for vars in config['controllers']:
				clsname = vars['class']
				modulename = '.'.join(clsname.split('.')[:-1])
				classname = clsname.split('.')[-1]

				module = __import__(modulename, globals(), locals(), classname, -1)
#				logging.debug('getting class %s from module %s' % (classname, module))
				cls = getattr(module, classname)

				logging.debug("%s,%s" % (vars['url'], str(cls)))

				self.controllers.append((vars['url'] or '', cls))

		self.controllers.append(('', ErrorController))
		self.controllers.append(('', DebugController))

		logging.debug('controllers:'+repr(self.controllers))

		self.mapper = Mapper()
		self._controllers = dict([(controller.__name__, controller) for cprefix, controller in self.controllers])
		prefix = None
		if hasattr(self, 'prefix'):
			prefix = self.prefix

		for cprefix, controller in self.controllers:
			logging.debug('checking controller "%s" for bindings' % controller)
			if hasattr(controller, '_bindaddresses'):
				logging.debug('found _bindaddresses in %s' % controller)
				controller._bindaddresses(self.mapper, prefix, cprefix)
			else:
				logging.debug('didnt find _bindaddresses in %s' % controller)
	def _get_output(self, path = None):
			r = self.mapper.match(urllib.unquote(path))
			try:
				if r:
					controller = self._controllers[r.pop('controller')]()
					controller.app = self
					action = getattr(controller, r.pop('action'))

					args = dict([(str(name), self.request.get(name)) for name in self.request.arguments()])
					args.update(r)


					output = action(**args)
				else:
					#self.app = self
					url404 = url_for('error404')
					raise Error(404, self._get_output(url404))
			except Error, e:
					self.error(e.code)
					output = e.content
			return output

	def render(self, path = None):
		try:
			self.mapper.environ = self.request.environ
			path = path or self.request.path

			output = self._get_output(path)

			if output:
				for l in output:
					if isinstance(l, HeaderAttribute):
						self.response.headers[l.name] = l.value
					else:
						self.response.out.write(l)
				if 'Content-Type' not in self.response.headers:
					self.response.headers['Content-Type'] = 'text/xhtml'						
		except RequireLogin:
			uri = users.create_login_url(self.request.uri)
			self.redirect(uri)
		except Redirect, inst:
			self.redirect(inst.url)

	def post(self):
		self.render()

	def get(self):
		self.render()

if __name__ == '__main__':
	logging.debug(DebugController().debug())


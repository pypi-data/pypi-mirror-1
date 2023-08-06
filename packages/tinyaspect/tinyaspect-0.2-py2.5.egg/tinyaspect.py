#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# tinyaspect - Easy creation of decorators for methods and functions 
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

import logging
import aspects
from peak.util.decorators import decorate_class

class aspect_instance(object):
	def __init__(self, a, mode, args, kw):
		self.a = a
		self.mode = mode
		self.args = args
		self.kw = kw

	def wrap(self, f):
		def later(cls):
			self.cls = cls
			self.f = f
			if not self.mode == aspect.ATTACH:
				aspects.with_wrap(self.wrapper, getattr(cls, f.__name__))
			else:
				self.a(cls, f, *self.args, **self.kw)
			return cls
		decorate_class(later)
		return f
	
	def wrapper(self, *args, **kw):
		if self.mode == aspect.MODIFY:
			rv = yield aspects.proceed(*args, **kw)
			rv = self.a(rv, *self.args, **self.kw)
		elif self.mode == aspect.NORMAL:
			self.a(*self.args, **self.kw)
			rv = yield aspects.proceed(*args, **kw)
		yield aspects.return_stop(rv)
	
class aspect(object):
	NORMAL = 0
	MODIFY = 1
	ATTACH = 2

	def __init__(self, mode=NORMAL, attach=False):
		self.mode = mode

	def __call__(self, a):
		self.a = a
		return self.wrap

	def wrap(self, *args, **kw):
		return aspect_instance(self.a, self.mode, args, kw).wrap





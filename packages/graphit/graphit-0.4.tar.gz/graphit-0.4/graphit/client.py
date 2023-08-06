#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2009 Antoine Millet <antoine@inaps.org>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from restkit import RestClient, httpc

class GraphItAgent:
	
	def __init__(self, base_url, login=None, passwd=None):
		
		self.base_url = base_url
		
		transport = httpc.HttpClient()
		
		if login and passwd:
			transport.add_authorization(
				httpc.BasicAuth((login, passwd))
			)
		
		self._client = RestClient(transport=transport)
		
	def add_value(self, set, feed, value, unit=''):
		''' Add a value in set for feed. '''
		
		self._client.post(
			self.base_url,
			path = '%s/%s' % (set, feed),
			body = {'value': value, 'unit': unit},
			headers = {'Content-type': ('application/x-www-form-urlenco'
										'ded; charset=utf-8')},
		)

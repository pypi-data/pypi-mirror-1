﻿# -*- coding: utf-8 -*-
# Copyright 2008, 2009 Mr.Z-man

# This file is part of wikitools.
# wikitools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# wikitools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with wikitools.  If not, see <http://www.gnu.org/licenses/>.

import wiki, page, api

class Category(page.Page):
	"""
	A category on the wiki
	"""
	def __init__(self, site, title=False, check=True, followRedir=False, section=False, sectionnumber=False, pageid=False):
		self.members = []
		page.Page.__init__(self, site=site, title=title, check=check, followRedir=followRedir, section=section, sectionnumber=sectionnumber, pageid=pageid)
		if self.namespace != 14:
			self.title = self.site.namespaces[14]['*']+':'+self.title
			
	def getAllMembers(self, titleonly=False, reload=False):
		"""
		Gets a list of pages in the category
		titleonly - set to True to only create a list of strings,
		else it will be a list of Page objects
		reload - reload the list even if it was generated before
		"""
		if self.members and not reload:
			if titleonly:
				ret = []
				for member in self.members:
					ret.append(member.title)
				return ret
			return self.members
		else:
			ret = []
			self.members = []
			for member in self.__getMembersInternal():
				self.members.append(member)
				if titleonly:
					ret.append(member.title)
			if titleonly:
				return ret
			return self.members
	
	def getAllMembersGen(self, titleonly=False, reload=False):
		"""
		Generator function for pages in the category
		titleonly - set to True to return strings,
		else it will return Page objects
		reload - reload the list even if it was generated before
		"""
		if self.members and not reload:
			for member in self.members:
				if titleonly:
					yield member.title
				else:
					yield member
		else:
			self.members = []
			for member in self.__getMembersInternal():
				self.members.append(member)
				if titleonly:
					yield member.title
				else:
					yield member
				
	def __getMembersInternal(self, namespace=False):
		params = {'action':'query',
			'list':'categorymembers',
			'cmtitle':self.title,
			'cmlimit':self.site.limit,
			'cmprop':'title'
		}
		if namespace != False:
			params['cmnamespace'] = namespace
		while True:
			req = api.APIRequest(self.site, params)
			data = req.query(False)
			for item in data['query']['categorymembers']:
				yield page.Page(self.site, item['title'], check=False, followRedir=False)
			try:
				params['cmcontinue'] = data['query-continue']['categorymembers']['cmcontinue']
			except:
				break 

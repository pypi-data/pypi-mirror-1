from os import listdir, sep
from os.path import isdir, join, exists, dirname
import codecs

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from Products.statusmessages.interfaces import IStatusMessage




class MemberList(BrowserView):
	__call__ = ViewPageTemplateFile('memberlist.pt')

	def __init__(self, *args, **kwargs):
		BrowserView.__init__(self, *args, **kwargs)
		self.ctx = aq_inner(self.context)
		self.exclude = set(self.ctx.getExclude())
		self.current = set(self.ctx.getCurrentmembers())

	def currentMembers(self):
		pm = self.ctx.portal_membership
		out = []
		for memberId in self.current:
			member = pm.getMemberById(memberId)
			if member:
				out.append(self._memberInfo(memberId, member))
		return out

	def previousMembers(self):
		pm = self.ctx.portal_membership
		out = []
		for memberId in pm.listMemberIds():
			if not memberId in self.exclude and not memberId in self.current:
				member = pm.getMemberById(memberId)
				out.append(self._memberInfo(memberId, member))
		return out

	def _memberInfo(self, memberId, member):
		portal_url = self.ctx.portal_url()
		homeFolder = "%s/Members/%s" % (portal_url, memberId)
		return dict(
				email = member.getProperty("email"),
				fullname = member.getProperty("fullname"),
				portrait_url = member.getPersonalPortrait().absolute_url(),
				homeFolder = homeFolder,
				description = member.getProperty("description")
			)

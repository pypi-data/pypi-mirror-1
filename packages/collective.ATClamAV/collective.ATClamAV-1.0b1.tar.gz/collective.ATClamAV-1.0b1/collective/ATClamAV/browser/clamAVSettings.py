from zope.component import adapts
from zope.interface import implements
from zope.formlib import form

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from plone.app.controlpanel.form import ControlPanelForm
from collective.ATClamAV.interfaces import IAVScannerSettings
from collective.ATClamAV import ATClamAVMessageFactory as _


class ClamAVControlPanel(ControlPanelForm):

	form_fields = form.FormFields(IAVScannerSettings)

	label = _("ClamAV settings")
	description = _("Clam antivirus host settings.")
	form_name = _("ClamAV settings")

class ClamAVControlPanelAdapter(SchemaAdapterBase):

	adapts(IPloneSiteRoot)
	implements(IAVScannerSettings)

	def __init__(self, context):
		super(ClamAVControlPanelAdapter, self).__init__(context)
		properties = getToolByName(context, 'portal_properties')
		self.context = properties.clamav_properties


	def get_clamav_host(self):
		return getattr(self.context,'clamav_host',"localhost")

	def set_clamav_host(self, value):
		self.context._updateProperty('clamav_host', value)

	clamav_host = property(get_clamav_host,set_clamav_host)

	def get_clamav_port(self):
		return int(getattr(self.context,'clamav_port',"3310"))

	def set_clamav_port(self, value):
		self.context._updateProperty('clamav_port', value)

	clamav_port = property(get_clamav_port,set_clamav_port)

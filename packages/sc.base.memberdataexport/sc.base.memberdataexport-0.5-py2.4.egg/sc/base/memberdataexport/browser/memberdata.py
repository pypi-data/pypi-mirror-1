# coding: utf-8

from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
from zope.interface import implements
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.utils import getToolByName

from csv import QUOTE_ALL, QUOTE_MINIMAL
from csv import DictWriter
from csv import register_dialect
from csv import excel

from tempfile import TemporaryFile
from sc.base.memberdataexport.streaming import FileStreamer



class Exporter(BrowserView):
    
    def __init__(self, context, request):
        super(Exporter, self).__init__(context, request)
        self._memberdata = getToolByName(self.context,'portal_memberdata')
        self._mt = getToolByName(self.context,'portal_membership')
        properties = getToolByName(self, 'portal_properties')
        memberdataexport_properties = getattr(properties, 
                                              'memberdataexport_properties')
        site_properties = getattr(properties, 
                                  'site_properties')
        self._memberdata_properties = self._memberdata.propertyIds()
        self._export_columns = ['username',] + self._memberdata_properties
        self.mpDelimiter = str(memberdataexport_properties.delimiter)
        self.mpAlwaysQuote = memberdataexport_properties.alwaysQuote
        self.mpLineterminator = memberdataexport_properties.lineTerminator
        self.mpEncoding = memberdataexport_properties.encoding
        self.filename = memberdataexport_properties.filename
        self.defaultCharset = site_properties.default_charset
    
    def __call__(self,*args,**kwargs):
        '''Returns the csv file
        '''
        
        tmpfile = FileStreamer(TemporaryFile(suffix='.csv'))
        columns = self._export_columns
        filename = self.filename
        mpDelimiter = self.mpDelimiter
        mpAlwaysQuote = self.mpAlwaysQuote
        mpLineterminator = self.mpLineterminator
        mpEncoding = self.mpEncoding
        if str(mpLineterminator) == 'win':
            mpLineterminator = '\r\n'
        else:
            mpLineterminator = '\n'
        
        # Define our slightly different csv dialect
        class modified_dialect(excel):
            '''Customized dialect
            '''
            delimiter = mpDelimiter
            if mpAlwaysQuote:
                quoting = QUOTE_ALL
            lineterminator = mpLineterminator
        
        register_dialect('modified_dialect',modified_dialect)
        writer = DictWriter(tmpfile, 
                            columns, 
                            extrasaction='ignore',
                            dialect = 'modified_dialect')
        
        # Add header
        writer.writerow(dict(zip(columns,columns)))
        writer.writerows(self.items)
        tmpfile.seek(0, 0)
        dataLen = len(tmpfile)
        setHeader = self.request.response.setHeader
        setHeader('Content-Length', dataLen)
        setHeader('Content-Type', 'text/csv')
        setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
        
        return tmpfile
    
    @property
    def items(self):
        # get a list of memberids
        memberIds = self._listMemberIds()
        for memberId in memberIds:
            yield self._userData(memberId)
    
    def _userData(self,userId):
        member = self._mt.getMemberById(userId)
        tmpUserData = {}
        mpEncoding = self.mpEncoding
        defaultCharset = self.defaultCharset
        if not member:
            return tmpUserData
        tmpUserData['username'] = member.getUserName()
        for m_prop in self._memberdata_properties:
            tmpUserData[m_prop]= str(member.getProperty(m_prop,
                                     '')).decode(defaultCharset).encode(mpEncoding)
        return tmpUserData
    
    def _listMemberIds(self):
        ''' Returns a list of member ids for this portal
        '''
        mt = self._mt
        memberIds = mt.listMemberIds()
        return memberIds
    

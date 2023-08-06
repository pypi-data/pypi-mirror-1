from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from csci.shortlinks import shortlinksMessageFactory as _

#
from plone.app.form.validators import null_validator
from Products.statusmessages.interfaces import IStatusMessage
import google_short

class InewlinkSchema(interface.Interface):
    # -*- extra stuff goes here -*-
    
    long_url = schema.TextLine(
        title=u'Enter URL to shorten',
        description=u'paste link here',
        required=True,
        readonly=False,
        default=u'http://',
        )



class newlink(formbase.PageForm):
    form_fields = form.FormFields(InewlinkSchema)
    label = _(u'Create New Link')
    description = _(u'Create a new shortlink here')
    
    @form.action('Submit')
    def actionSubmit(self, action, data):
        
        
        shorturl = google_short.get_short(server    =self.context.servername,
                                          action    =self.context.action,
                                          hmac      =self.context.hmac,
                                          email     =self.context.email,
                                          url       = data['long_url'],
                                          short_name='anything',
                                          is_public ='true')
        
        shorturl = shorturl.replace('/s.14o','/14o')        
        output_str = data['long_url'] + ' is \n now ' + shorturl
        
        IStatusMessage(self.request).addStatusMessage(_(output_str), type='info')
#        self.request.response.redirect(self.context.absolute_url() + '/')


        # Put the action handler code here 

    @form.action('Cancel', validator=null_validator)
    def actionCancel(self, action, data):
        self.request.response.redirect(self.context.absolute_url() + '/')
        # Put the action handler code here 




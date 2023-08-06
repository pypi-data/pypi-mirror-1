from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from csci.feedback import feedbackMessageFactory as _

#
from zope.interface import invariant, Invalid
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget


def val_captcha(value):
    print 'validating: ', value
    result = True
    return result
    
    
class IfeedbackSchema(interface.Interface):
    # -*- extra stuff goes here -*-

    name = schema.TextLine(
        title=u'Your Name',
        description=u'enter your own name here',
        required=True,
        readonly=False,
        default=u'Name',
        )
    email = schema.TextLine(
        title=u'Your email address',
        description=u'enter your email address here',
        required=True,
        readonly=False,
        default=None,
        )
    city = schema.TextLine(
        title=u'City or Town',
        description=u'enter the nearest city or town to you',
        required=False,
        readonly=False,
        default=None,
        )    
    country = schema.TextLine(
        title=u'Country',
        description=u'enter the country you are in',
        required=False,
        readonly=False,
        default=None,
        )    
    gender = schema.Choice(
        title=u'Gender',
        description=u'please select your gender',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm(value=1, token='male', title='Male'),
            SimpleTerm(value=2, token='female', title='Female')
            ))	
        )
    captcha = schema.TextLine(
        title=u'Captcha',
        description=u'',
        required=True,
        readonly=False,
        default=None,
    )   

      

class ReCaptcha(object):
    subject = u""
    captcha = u""
    def __init__(self, context):
        self.context = context
        

class feedback(formbase.PageForm):
    form_fields = form.FormFields(IfeedbackSchema)
    form_fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    label = _(u'Feedback Form')
    description = _(u'Contact us and leave feedback')

    @form.action('Submit')
    def actionSubmit(self, action, data):
        pass
        # Put the action handler code here 

    @form.action('Cancel')
    def actionCancel(self, action, data):
        pass
        # Put the action handler code here 




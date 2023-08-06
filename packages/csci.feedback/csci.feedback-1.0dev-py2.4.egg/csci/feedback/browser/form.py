from Acquisition import aq_inner
from zope import interface
from zope import schema
from zope.component import getMultiAdapter
from z3c.form import form, field, button
from plone.z3cform.layout import wrap_form

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget


class IReCaptchaForm(interface.Interface):
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
    messageTone = schema.Choice(
        title=u'What kind of comment would you like to send?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm(value=1, token='oops!', title='oops!'),
            SimpleTerm(value=2, token='negative', title='negative'),
            SimpleTerm(value=3, token='positive', title='positive')
            ))	
        )
    messageTone = schema.Choice(
        title=u'What would you like to commment on?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm(value=1, token='Website', title='Website'),
            SimpleTerm(value=2, token='Advertising', title='Advertising'),
            SimpleTerm(value=3, token='Inappropriate websites', title='Inappropriate websites'),
            SimpleTerm(value=4, token='Corrections', title='Corrections'),
            SimpleTerm(value=5, token='Problem/Error', title='Problem/Error'),
            SimpleTerm(value=6, token='Other', title='Other')
            ))	
        )
    browser = schema.Choice(
        title=u'What browser are you using?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm(value=1, token='Internet Explorer', title='Internet Explorer'),
            SimpleTerm(value=2, token='Firefox', title='Firefox'),
            SimpleTerm(value=3, token='Chrome', title='Chrome'),
            SimpleTerm(value=4, token='Opera', title='Opera'),
            SimpleTerm(value=5, token='Netscape', title='Netscape'),
            SimpleTerm(value=6, token='Other', title='Other')
            ))	
        )
    message = schema.Text(
        title=u'Message',
        description=u'enter your message',
        required=False,
        readonly=False,
        default=None,
        )  
    captcha = schema.TextLine(title=u"ReCaptcha",
                              description=u"",
                              required=False)

class ReCaptcha(object):
    subject = u""
    captcha = u""
    def __init__(self, context):
        self.context = context

class BaseForm(form.Form):
    """ example captcha form """
    fields = field.Fields(IReCaptchaForm)
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    @button.buttonAndHandler(u'Save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if data.has_key('captcha'):
            # Verify the user input against the captcha
            captcha = getMultiAdapter((aq_inner(self.context), self.request), name='recaptcha')
            if captcha.verify(data['captcha']):
                print 'ReCaptcha validation passed.'
                mTo = 'pjdyson@gmail.com'
                mFrom = 'pdyson@cannondata.com'
                mSubj = 'Site Feedback'
                message = 'a message from your site'
                for i in data.keys():
                    message += str(i) + ': ' + str(data[i]) + '\n'
                    
                self.context.MailHost.send(message, mTo, mFrom, mSubj)

            else:
                print 'The code you entered was wrong, please enter the new one.'
        return

ReCaptchaForm = wrap_form(BaseForm)
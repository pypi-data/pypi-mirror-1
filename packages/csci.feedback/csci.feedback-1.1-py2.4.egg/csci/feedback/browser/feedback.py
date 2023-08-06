from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from csci.feedback import feedbackMessageFactory as _

#
from collective.captcha.form import Captcha
from plone.app.form.validators import null_validator
from zope.app.form.browser import RadioWidget as _RadioWidget


class IfeedbackSchema(interface.Interface):
    # -*- extra stuff goes here -*-

    name = schema.TextLine(
        title=u'Your Name',
        description=u'enter your own name here',
        required=True,
        readonly=False,
        default=None,
        )
    email = schema.TextLine(
        title=u'Your email address',
        description=u'enter your email address here',
        required=True,
        readonly=False,
        default=None,
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
    about = schema.Choice(
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
    message = schema.Text(
        title=u'Message',
        description=u'Please enter your message',
        required=False,
        readonly=False,
        default=None,
        )  
    publish_example = schema.Text(
        title=u'',
        description=u'',
        required=False,
        readonly=True,
        default=u'If we publish comments they will be in the form:\n --- "Great Site! Keep up the good work" CJ - CA, USA --- We never publish nor pass on email addresses',
        ) 
    publish = schema.Bool(
        title=u'Click this box and we will not publish your comments on the Web.',
        description=u'',
        required=False,
        readonly=False,
        default=False,
        )
    
    #==========================================================
    #Optional Section
    #
    optional = schema.Text(
        title=u'Here are some optional questions but answering them helps us build a better site',
        description=u'====================================================================',
        required=False,
        readonly=True,
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
    age = schema.Choice(
        title=u'Age',
        description=u'please select your age group',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm(value=1, token='Under 20', title='Under 20'),
            SimpleTerm(value=2, token='20-40', title='20-40'),
            SimpleTerm(value=3, token='40-60', title='40-60'),
            SimpleTerm(value=4, token='Over 60', title='Over 60')
            ))	
        )
    mybrowser = schema.Choice(
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
    findus = schema.Choice(
        title=u'How did you find us?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm(value=1, token='Search Engine', title='Search Engine'),
            SimpleTerm(value=2, token='Friends recommendation', title='Friends recommendation'),
            SimpleTerm(value=3, token='Media (Newspaper, TV, radio)', title='Media (Newspaper, TV, radio)'),
            SimpleTerm(value=4, token='Another website', title='Another website'),
            SimpleTerm(value=5, token="Don't Know", title="Don't Know")
            ))	
        )

    #==========================================================
    #Validation and submission
    #
    optional2 = schema.Text(
        title=u'Form Validation and Submission:',
        description=u'====================================================================',
        required=False,
        readonly=True,
        default=None,
        )  
    captcha = Captcha(
        title=_(u'Type the code'),
        description=_(u'Type the code from the picture shown below or '
                      u'from the audio.'))

def RadioWidget(field, request):
    vocabulary = field.vocabulary
    widget = _RadioWidget(field, vocabulary, request)
    return widget 

class feedback(formbase.PageForm):
    form_fields = form.FormFields(IfeedbackSchema)

#    form_fields['findus'].custom_widget = RadioWidget
 #   form_fields['gender'].custom_widget = RadioWidget
  #  form_fields['messageTone'].custom_widget = RadioWidget
   # form_fields['about'].custom_widget = RadioWidget
    #form_fields['mybrowser'].custom_widget = RadioWidget

    label = _(u'Feedback Form')
    description = _(u'Feedback Form')

    @form.action('Submit')
    def actionSubmit(self, action, data):
#        mTo = 'webdirector@greenwich2000.com'
#        mFrom = 'webdirector@greenwich2000.com'
        mTo = 'pjdyson@gmail.com'
        mFrom = 'pdyson@cannondata.com'
        mSubj = 'Site Feedback'
        message = 'a message from your site:\n=================================\n'
        for i in data.keys():
            message += str(i) + ': ' + str(data[i]) + '\n'
            
        #send the email
        self.context.MailHost.send(message, mTo, mFrom, mSubj)

        #redirect to thankyou page
        self.request.response.redirect(self.context.absolute_url() + '/@@fbform_view')

    @form.action('Cancel', validator=null_validator)
    def actionCancel(self, action, data):
        self.request.response.redirect(self.context.absolute_url() + '/')
        # Put the action handler code here 



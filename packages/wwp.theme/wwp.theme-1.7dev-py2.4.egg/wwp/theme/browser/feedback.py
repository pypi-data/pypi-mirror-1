from zope import interface, schema
from zope.formlib import form
from Products.Five.formlib import formbase
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.CMFPlone import PloneMessageFactory as _

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
            SimpleTerm('oops!', 'oops!'),
            SimpleTerm('negative', 'negative'),
            SimpleTerm('positive', 'positive')
            ))	
        )
    about = schema.Choice(
        title=u'What would you like to commment on?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm('Website', 'Website'),
            SimpleTerm('Advertising', 'Advertising'),
            SimpleTerm('Inappropriate websites', 'Inappropriate websites'),
            SimpleTerm('Corrections', 'Corrections'),
            SimpleTerm('Problem/Error', 'Problem/Error'),
            SimpleTerm('Other', 'Other')
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
        title=u'Click this box and we will NOT publish your comments on the Web.',
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
            SimpleTerm('Male', 'Male'),
            SimpleTerm('Female', 'Female')
            ))	
        )
    age = schema.Choice(
        title=u'Age',
        description=u'please select your age group',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm('Under 20', 'Under 20'),
            SimpleTerm('20-40', '20-40'),
            SimpleTerm('40-60', '40-60'),
            SimpleTerm('Over 60', 'Over 60')
            ))	
        )
    mybrowser = schema.Choice(
        title=u'What browser are you using?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm('Internet Explorer', 'Internet Explorer'),
            SimpleTerm('Firefox', 'Firefox'),
            SimpleTerm('Chrome', 'Chrome'),
            SimpleTerm('Opera', 'Opera'),
            SimpleTerm('Netscape', 'Netscape'),
            SimpleTerm('Other', 'Other')
            ))	
        )    
    findus = schema.Choice(
        title=u'How did you find us?',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        vocabulary=SimpleVocabulary((
            SimpleTerm('Search Engine', 'Search Engine'),
            SimpleTerm('Friends recommendation', 'Friends recommendation'),
            SimpleTerm('Media (Newspaper, TV, radio)', 'Media (Newspaper, TV, radio)'),
            SimpleTerm('Another website', 'Another website'),
            SimpleTerm("Don't Know", "Don't Know")
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

    form_fields['findus'].custom_widget = RadioWidget
    form_fields['gender'].custom_widget = RadioWidget
    form_fields['messageTone'].custom_widget = RadioWidget
    form_fields['about'].custom_widget = RadioWidget
    form_fields['mybrowser'].custom_widget = RadioWidget

    label = _(u'Feedback Form')
    description = _(u'Feedback Form')
    
    @form.action('Submit')
    def actionSubmit(self, action, data):
        
        mTo   = self.context.email_from_address
        mFrom = self.context.email_from_address
        mSubj = 'Site Feedback'
        message = 'Feedback from your site:\n=================================\n'
        message += 'Name : ' + str(data['name']) + '\n'
        message += 'Email : ' + str(data['email']) + '\n'
        message += 'Message Tone : ' + str(data['messageTone']) + '\n'
        message += 'Message Subject : ' + str(data['about']) + '\n'
        message += 'do NOT Publish : ' + str(data['publish']) + '\n'
        message += 'Message : ' + '\n'
        message += str(data['message']) + '\n'
        message += '------------------------------------------------------------------' + '\n'
        message += 'City : ' + str(data['city']) + '\n'
        message += 'Country : ' + str(data['country']) + '\n'
        message += 'Gender : ' + str(data['gender']) + '\n'
        message += 'Age : ' + str(data['age']) + '\n'
        message += 'Browser : ' + str(data['mybrowser']) + '\n'
        message += 'Source : ' + str(data['findus']) + '\n'
        message += '------------------------------------------------------------------' + '\n'

        #send the email
        self.context.MailHost.send(message, mTo, mFrom, mSubj)

        #redirect to thankyou page
        self.request.response.redirect(self.context.absolute_url() + '/@@thankyou')

    @form.action('Cancel', validator=null_validator)
    def actionCancel(self, action, data):
        self.request.response.redirect(self.context.absolute_url() + '/')
        # Put the action handler code here 



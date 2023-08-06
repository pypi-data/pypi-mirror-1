import urllib
import datetime
import time
import random
import unicodedata
from string import maketrans
#EMAIL
from email.Header import make_header
from email.MIMEMessage import Message
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText 

# some utility functions
def nametoid(text):
    '''change a name into an id'''
    try:
        text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
    except:
        pass

    # check for illegal chars
    illegal  = '.,!"£$%^&*()_+=[]{}@#~?/><|\'¬`;:'
    for ill in illegal:
        text = text.replace(ill,'')
    
    # remove linebreaks
    text = text.replace('<br>','')
    text = text.replace('\n','')
    text = text.replace('\r','')

    # replace spaces with '-' 
    text = text.replace(' ','-')
    
    return text
    

def publishNews(context, title, description, text):
    '''publishes a news item to the site repository'''
    #####################################
    ##post and publish news item

    _newsSubDir = 'news'
    today = datetime.date.today()
    news_id = str(title)+ '-' +str(today)
    news_id += '-' + str(random.random()*100)[:2]
    news_id = news_id.replace(' ','-')
    news_id = _removeSymb(news_id)
    news_id = news_id.lower()

    #go to news folder
    root_app = context.restrictedTraverse(_newsSubDir)
    #create item
    news_item = root_app.invokeFactory(type_name='News Item',
                                       id=news_id,
                                       title=title,
                                       description=description,
                                       text=text)
    root_app.reindexObject()
    
    #automatically publish news item
    root_app = context.restrictedTraverse('news/'+news_id)
    urltool  = getToolByName(context, 'portal_url')
    workflow = getToolByName(context, "portal_workflow")
    review_state = workflow.getInfoFor(root_app, 'review_state')
    if review_state != 'published':
        error=workflow.doActionFor(root_app,'publish',comment='publised programmatically') 
    root_app.reindexObject()
    
def postToTwitter(uname, passwd, text):
    '''sends a post to twitter under specified username'''
    #print '------posting a tweet---'
    errors = ''
    ##login to twitter
    try:
        api = twitter.Api(username=uname, password=passwd)
    except:
        errors += 'Twitter login fail'
        return errors

    ##post the message
    try:
        statuses = api.PostUpdate(status=text[:140], in_reply_to_status_id=None)
    except:
        errors += 'Failed at posting'
        return errors
    
    return None
        
def get_short(server='',
              action='get_or_create_hash',
              hmac='',
              email='',
              url='',
              short_name='anything',
              is_public='true'):    
    
    request_url = google_short.make_request_uri(server,                           #short.cannonscientific.com
                                                action,                           #get_or_create_hash
                                                hmac,                             #foobar
                                                user=email,                       #toor@cannonscientific.com
                                                url=url,                          #http://www.google.com
                                                shortcut=short_name,              #anything
                                                is_public=str(is_public).lower()  #true
                                                )

    response = urllib.urlopen(request_url)
    res = response.read()
    res = res.replace('true','True')
    res_dict = eval(res)
    end_url = 'http://' + str(server) + '/' + str(res_dict['shortcut'])
    
    return end_url
def sendEmail(context, mTo, mFrom, mSubj, message, message_b):
   
    # -*- coding: iso-8859-1 -*-
    e_subject = mSubj
    e_from = mFrom
    e_to = mTo
    body_html = message
    body_plain = message_b
   
    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = e_subject
    mime_msg['From'] = e_from
    mime_msg['To'] = e_to
    mime_msg.preamble = 'This is a multi-part message in MIME format.'
   
    # Encapsulate the plain and HTML versions of the message body 
    # in an 'alternative' part, so message agents can decide 
    # which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    mime_msg.attach(msgAlternative)
   
    # plain part
    if message_b != '':
        msg_txt = MIMEText(body_plain,  _charset='iso-8859-1')
        msgAlternative.attach(msg_txt)
   
    # html part
    if message != '':
        msg_txt = MIMEText(body_html, _subtype='html', 
                           _charset='iso-8859-1')
        msgAlternative.attach(msg_txt)
    
    # send the mail
    context.MailHost.send(mime_msg.as_string())
#
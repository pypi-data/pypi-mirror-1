import os
from urlparse import urlparse

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime

from zope.interface import implements

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva.interfaces import IVersionedContent, IVersion
from Products.Silva import mangle
from Products.Silva.helpers import add_and_edit
from Products.Silva import SilvaPermissions

from Products.SilvaExternalSources.ExternalSource import ExternalSource
from Products.SilvaExternalSources.interfaces import IExternalSource

icon = "www/pollquestion.gif"

def set_no_cache_headers(REQUEST):
    headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
                ('Last-Modified', 
                    DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
                ('Cache-Control', 'no-cache, must-revalidate'),
                ('Cache-Control', 'post-check=0, pre-check=0'),
                ('Pragma', 'no-cache'),
                ]
    placed = []
    for key, value in headers:
        if key not in placed:
            REQUEST.RESPONSE.setHeader(key, value)
            placed.append(key)
        else:
            REQUEST.RESPONSE.addHeader(key, value)
    
class OverwriteNotAllowed(Exception):
    """raised when trying to overwrite answers for a used question"""

class TooManyAnswers(Exception):
    """raised when more than 20 answers are given"""

class ViewableExternalSource(ExternalSource):
    """ExternalSource subclass that has index_html overridden to display the
        external source object's public view as usual
    """

    def index_html(self, view_method='view'):
        """this is kinda nasty... copied the index_html Python script to
            avoid having ExternalSources.index_html (which returns the props
            form, not a decent public view, perhaps that should be changed some
            time) 

            note that, in addition to the response headers index_html sets 
            originally, this sets special headers to not have the content
            cached in browsers
        """
        content = 'content.html'
        override = 'override.html'
        if hasattr(self.aq_explicit, override):
            renderer = override
        else:
            renderer = content
        self.REQUEST.RESPONSE.setHeader('Content-Type', 
                                            'text/html;charset=utf-8')

        return getattr(self, renderer)(view_method=view_method)

class PollQuestion(VersionedContent, ViewableExternalSource):
    """This Silva extension enables users to conduct polls inside Silva sites. 
        A Question is posed to the public and results of the answers are 
        displayed to those that respond. The poll can be an independent page 
        or be embedded in a document as a Code Source.
    """

    security = ClassSecurityInfo()
    meta_type = 'Silva Poll Question'
    implements((IVersionedContent, IExternalSource))
    
    _sql_method_id = 'poll_question'
    _layout_id = 'layout'
    parameters = None

    def __init__(self, id):
        PollQuestion.inheritedAttribute('__init__')(self, id)
        self._init_form()

    def _init_form(self):
        form = ZMIForm('form', 'Properties Form')
        f = open(os.path.join(package_home(globals()), 'www', 
                                'externalSourceForm.form'))
        XMLToForm(f.read(), form)
        f.close()
        self.set_form(form)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_OverwriteNotAllowed')
    def get_OverwriteNotAllowed(self):
        return OverwriteNotAllowed

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_TooManyAnswers')
    def get_TooManyAnswers(self):
        return TooManyAnswers

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'to_html')
    def to_html(self, REQUEST, **kw):
        """return HTMl for ExternalSource interface"""
        edit_mode = REQUEST.get('edit_mode', False)
        if edit_mode:
            version = self.get_previewable()
        else:
            version = self.get_viewable()
        if kw.has_key('display') and kw['display'] == 'link':
            return '<p class="p"><a href="%s">%s</a></p>' % (
                self.absolute_url(), self.absolute_url())
        # XXX is this the expected behaviour? do we want to display a link to
        # the poll instead when the question and results shouldn't be 
        # displayed?
        if version is None:
            return ''
        view_type = edit_mode and 'preview' or 'public'
        return self.view_version(view_type, version)

    is_cacheable = ViewableExternalSource.is_cacheable
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'current_question_start_datetime')
    def current_question_start_datetime(self):
        version = self._get_published_or_closed()
        if version is None:
            return None
        return version.question_start_datetime()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'current_question_end_datetime')
    def current_question_end_datetime(self):
        version = self._get_published_or_closed()
        if version is None:
            return None
        return version.question_end_datetime()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'current_result_start_datetime')
    def current_result_start_datetime(self):
        version = self._get_published_or_closed()
        if version is None:
            return None
        return version.result_start_datetime()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'current_result_end_datetime')
    def current_result_end_datetime(self):
        version = self._get_published_or_closed()
        if version is None:
            return None
        return version.result_end_datetime()

    def _get_published_or_closed(self):
        version = self.get_viewable()
        if version is None:
            version = self.get_last_closed()
        return version

    # XXX hope this doesn't result in scary subtle breakage...
    def approve_version(self):
        """approve the current unapproved version"""
        # just call super's approve_version, if that raises an exception let
        # it pass through, in that case the dates are obviously not set
        PollQuestion.inheritedAttribute('approve_version')(self)
        viewable = self.get_viewable()
        now = DateTime()
        if self.current_question_start_datetime() is None:
            viewable.set_question_start_datetime(now)
        if self.current_result_start_datetime() is None:
            viewable.set_result_start_datetime(now)

    security.declarePublic('view_version')
    def view_version(self, *args, **kwargs):
        """overriding so we can set headers"""
        set_no_cache_headers(self.REQUEST)
        return PollQuestion.inheritedAttribute('view_version')(
                                            self, *args, **kwargs)

InitializeClass(PollQuestion)

class PollQuestionVersion(Version):
    """A poll question version"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Poll Question Version'
    implements(IVersion)

    _question = None
    _answers = None
    qid = None

    def __init__(self, id):
        PollQuestionVersion.inheritedAttribute('__init__')(self, id)
        # for older SilvaExternalSources use this:
        #PollQuestionVersion.inheritedAttribute('__init__')(self, id, '')
        self.qid = None
        self._question_start_datetime = None
        self._question_end_datetime = None
        self._result_start_datetime = None
        self._result_end_datetime = None

    def manage_afterAdd(self, item, container):
        PollQuestionVersion.inheritedAttribute('manage_afterAdd')(self, 
                                                            item, container)
        question = ''
        answers = []
        votes = []
        if self.qid is not None:
            question = self.get_question()
            answers = self.get_answers()
            votes = self.get_votes()
        self.qid = self.service_polls.create_question(question, answers, votes)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'save')
    def save(self, question, answers, overwrite=False):
        """save question data"""
        votes = self.service_polls.get_votes(self.qid)
        curranswers = self.service_polls.get_answers(self.qid)
        answers = [x.strip() for x in answers.strip().split('\n\n')]
        if len(answers) > 20:
            raise TooManyAnswers, self.qid
        have_votes = not not [x for x in votes if x != 0]
        if (answers != curranswers and have_votes and not overwrite):
            raise OverwriteNotAllowed, self.qid
        self._save(question, answers)

    def _save(self, question, answers):
        self.service_polls.save(self.qid, question, answers)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_question')
    def get_question(self):
        """returns a string"""
        return self.service_polls.get_question(self.qid)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_answers')
    def get_answers(self):
        """returns a list of strings"""
        return self.service_polls.get_answers(self.qid)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_votes')
    def get_votes(self):
        """returns a list of ints"""
        return self.service_polls.get_votes(self.qid)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'manage_vote')
    def manage_vote(self, REQUEST=None):
        if REQUEST is None:
            REQUEST = self.REQUEST
        if not REQUEST or not REQUEST.has_key('answer'):
            return
        answer = unicode(REQUEST['answer'], 'UTF-8')
        answers = self.get_answers()

        import pdb; pdb.set_trace()
        id = answers.index(answer)
        service = self.service_polls
        service.vote(self.qid, id)
        if service.store_cookies():
            REQUEST.RESPONSE.setCookie('voted_cookie_%s' % 
                                        self.get_silva_object().absolute_url(), 
                                    '1', 
                                    expires='Wed, 19 Feb 2020 14:28:00 GMT',
                                    path='/')
        headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
                    ('Last-Modified', 
                        DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
                    ('Cache-Control', 'no-cache, must-revalidate'),
                    ('Cache-Control', 'post-check=0, pre-check=0'),
                    ('Pragma', 'no-cache'),
                    ]
        placed = []
        for key, value in headers:
            if key not in placed:
                REQUEST.RESPONSE.setHeader(key, value)
                placed.append(key)
            else:
                REQUEST.RESPONSE.addHeader(key, value)
        return True

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'has_voted')
    def has_voted(self, REQUEST=None):
        if not self.service_polls.store_cookies():
            return False
        if REQUEST is None:
            REQUEST = self.REQUEST
        return REQUEST.has_key('voted_cookie_%s' % 
                                    self.get_silva_object().absolute_url())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'display_question')
    def display_question(self):
        """returns True if the question should be displayed, False if not"""
        startdate = self.question_start_datetime()
        enddate = self.question_end_datetime()
        now = DateTime()
        return ((startdate and startdate < now) and 
                  (not enddate or enddate > now))

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'display_results')
    def display_results(self):
        """returns True if results should be displayed, False if not"""
        startdate = self.result_start_datetime()
        enddate = self.result_end_datetime()
        now = DateTime()
        return ((startdate and startdate < now) and 
                  (not enddate or enddate > now))
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'display_too_late')
    def display_too_late(self):
        """returns True if questions or results should be displayed

            on False only a message 'this poll is closed' will be showed
        """
        red = self.result_end_datetime()
        return red is not None and red < DateTime()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'question_start_datetime')
    def question_start_datetime(self):
        return self._question_start_datetime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'set_question_start_datetime')
    def set_question_start_datetime(self, dt):
        self._question_start_datetime = dt

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'question_end_datetime')
    def question_end_datetime(self):
        return self._question_end_datetime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'set_question_end_datetime')
    def set_question_end_datetime(self, dt):
        self._question_end_datetime = dt

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'result_start_datetime')
    def result_start_datetime(self):
        return self._result_start_datetime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'set_result_start_datetime')
    def set_result_start_datetime(self, dt):
        self._result_start_datetime = dt

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'result_end_datetime')
    def result_end_datetime(self):
        return self._result_end_datetime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'set_result_end_datetime')
    def set_result_end_datetime(self, dt):
        self._result_end_datetime = dt

InitializeClass(PollQuestionVersion)

manage_addPollQuestionForm = PageTemplateFile('www/pollQuestionAdd', 
                        globals(), __name__='manage_addPollQuestionForm')

def manage_addPollQuestion(self, id, title, question, answers, REQUEST=None):
    """add a poll question"""
    if not mangle.Id(self, id).isValid():
        return
    obj = PollQuestion(id)
    self._setObject(id, obj)
    obj = getattr(self, id)
    obj.manage_addProduct['SilvaPoll'].manage_addPollQuestionVersion(
        '0', title, question, answers)
    obj.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addPollQuestionVersionForm = PageTemplateFile(
                        'www/pollQuestionVersionAdd', globals(), 
                        __name__='manage_addPollQuestionVersionForm')

def manage_addPollQuestionVersion(self, id, title, question, answers,
                                    REQUEST=None):
    """add a poll question version"""
    if not mangle.Id(self, id).isValid():
        return
    version = PollQuestionVersion(id)
    self._setObject(id, version)
    
    version = self._getOb(id)
    version.set_title(title)
    version._save(question, answers)

    add_and_edit(self, id, REQUEST)
    return ''

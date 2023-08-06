from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements

from Products.Silva.helpers import add_and_edit

from interfaces import IServicePolls
from zodbdb import DB

class ServicePolls(SimpleItem):
    """Service that manages poll data"""

    security = ClassSecurityInfo()
    implements(IServicePolls)
    meta_type = 'Silva Poll Service'

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.db = DB(self)
        self._store_cookies = True

    def create_question(self, question, answers, votes):
        return self.db.create(question, answers, votes)

    def set_store_cookies(self, store_cookies):
        self._store_cookies = store_cookies
        
    def get_question(self, qid):
        return self.db.get(qid).question

    def get_answers(self, qid):
        return self.db.get(qid).answers

    def get_votes(self, qid):
        return self.db.get(qid).votes

    def save(self, qid, question, answers):
        self.db.update(qid, question, answers)

    def vote(self, qid, index):
        self.db.vote(qid, index)

    def store_cookies(self):
        if not hasattr(self, 'store_cookies'):
            self._store_cookies = True
            return True
        return self._store_cookies
    
InitializeClass(ServicePolls)

manage_addServicePollsForm = PageTemplateFile('www/servicePollsAdd', globals(),
                                        __name__='manage_addServicePollsForm')

def manage_addServicePolls(self, id='service_polls', title='', REQUEST=None):
    """add service to the ZODB"""
    id = self._setObject(id, ServicePolls(id, unicode(title, 'UTF-8')))
    store_cookies = False
    if REQUEST.has_key('store_cookies'):
        store_cookies = True
    service = getattr(self, id)
    service.set_store_cookies(store_cookies)
    add_and_edit(self, id, REQUEST)
    return ''

# Zope imports
from zope.interface import implements

# Plone imports
from Products.CMFPlone.PloneBatch import Batch as PloneBatch
from Products.CMFCore.utils import getToolByName
from plone.app.layout.globals.interfaces import IViewView

# Quills imports
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEntry
from quills.core.browser.interfaces import IWeblogView
from quills.core.browser.interfaces import IWeblogEntryView
from quills.core.browser.interfaces import ITopicView
from baseview import BaseView
from quills.app.interfaces import IWeblogEnhancedConfiguration


class WeblogView(BaseView):
    """A class with helper methods for use in views/templates.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogView, WeblogView)
    True
    """

    implements(IWeblogView)

    def getWeblog(self):
        return IWeblog(self.context)

    def getWeblogContentObject(self):
        return self.context

    def getConfig(self):
        """See IWeblogView.
        """
        return IWeblogEnhancedConfiguration(self.getWeblogContentObject())

    def getWeblogEntriesDates(self, entries_dict):
        """See IWeblogView.
        """
        days = entries_dict.keys()
        days.sort()
        days.reverse()
        return days

    def sortWeblogEntriesToDates(self, lazy_entries, resolution='day'):
        """See IWeblogView.
        """
        if resolution == 'day':
            format = '%Y-%m-%d 00:00:00'
        elif resolution == 'month':
            format = '%Y-%m'
        elif resolution == 'year':
            format = '%Y'
        else:
            msg = "The 'resolution' parameter must be one of 'day', 'month', \
                   or 'year'.  You passed %s."
            raise Exception(msg % resolution)
        if isinstance(lazy_entries, PloneBatch):
            start = lazy_entries.start - 1
            end = lazy_entries.end
            lazy_entries = lazy_entries._sequence[start:end]
        results = {}
        for lazy_entry in lazy_entries:
            date = lazy_entry.getPublicationDate().strftime(format)
            try:
                if results[date]:
                    # Add the entry to the top of the list for that day
                    results[date].append(lazy_entry)
            except:
                results[date] = [lazy_entry,]
        return results


class WeblogEntryView(BaseView):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogEntryView, WeblogEntryView)
    True
    """

    implements(IWeblogEntryView, IViewView)

    def getWeblog(self):
        return self.getWeblogEntry().getWeblog()

    def getWeblogContentObject(self):
        return IWeblogEntry(self.context).getWeblogContentObject()

    def getWeblogEntry(self):
        return IWeblogEntry(self.context)

    def getConfig(self):
        """See IWeblogView.
        """
        weblog = self.getWeblogContentObject()
        return IWeblogEnhancedConfiguration(weblog)
    
    def workflow_state(self):
        """returns the current workflow state of the context"""
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(self.context, "review_state")


class TopicView(WeblogView):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(ITopicView, TopicView)
    True
    """

    implements(ITopicView)

    def getLastModified(self, topic=None):
        """See ITopicView.
        """
        if topic is None:
            topic = self.context
        entries = topic.getEntries()
        if entries:
            # XXX modified should be in an interface
            return entries[0].modified


class WeblogArchiveView(BaseView):
    """A class with helper methods for use in views/templates.
    """

    #implements(IWeblogArchiveView)
    pass

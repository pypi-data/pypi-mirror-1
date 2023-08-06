# -*- coding: utf-8 -*-
from zope.component import getUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Acquisition import aq_inner
from collective.collection.alphabetic.interfaces import ICharacters


class TopicAlphabeticView(BrowserView):
    template = ViewPageTemplateFile('topic_alphabetic_view.pt')

    def __call__(self):
        return self.template()

    def queryCatalog(self):
        """Returns queryCatalog"""
        context = aq_inner(self.context)
        return context.queryCatalog()

    def title_url_dictionary_lists(self):
        """Returns list of title, url dictionaries for the selected alphabet."""
        qc = self.queryCatalog()
        character = self.request.get('character', None)
        results = []
        if character:
            uni_character = unicode(character)
            for item in qc:
                first_character = unicode(item.Title)[0]
                if first_character == uni_character or first_character == uni_character.lower():
                    results.append((('title', item.Title),('url', item.getURL())))
            results.sort()
            return [dict(item) for item in results]
        else:
            return None

    def selected_character(self):
        """Returns selected character."""
        return self.request.get('character', None)

    def has_contents(self, character):
        """Return True if there are any contents for the character."""
        qc = self.queryCatalog()
        contents = [item for item in qc if unicode(item.Title)[0] == (character or character.lower())]
        if contents != []:
            return True
        else:
            return False

    def characters(self):
        """Returns list of character, url bit dictionaries 
        like {'character':'A', 'url_bit':'?character=A'}"""
        context = aq_inner(self.context)
        properties = getToolByName(context, 'portal_properties').collection_alphabetic_properties
        tokens = properties.getProperty('character_tokens')
        use_alphabet = properties.getProperty('use_alphabet')
        characters = getUtility(ICharacters)(tokens, use_alphabet)
        return [{
                    'character':character, 
                    'url_bit':'%s%s' %('?character=', character),
                    'has_contents':self.has_contents(character),
                    'selected' : self.selected_character() == character,
                } for character in characters]

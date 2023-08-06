# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from collective.collection.alphabetic.browser import topic_alphabetic
from collective.collection.alphabetic.browser.topic_alphabetic import TopicAlphabeticView
#from topic_alphabetic import alphabets

class CategoryAlphabeticView(TopicAlphabeticView):
    template = ViewPageTemplateFile('category_alphabetic_view.pt')

    def __call__(self):
        return self.template()

    def title_url_dictionary_lists(self):
        context = aq_inner(self.context)
        portal_state = self.context.restrictedTraverse("@@plone_portal_state")
        url = portal_state.portal_url()
        qc = self.queryCatalog()
#        alphabet = self.request.get('alphabet', None)
#        results = []
#        if (alphabet == u'Ä') or (alphabet == u'Ö') or (alphabet == u'Å'):
#            for item in qc:
#                category = item.Subject
#                if category != ():
#                    for c in category:
#                        category_url = '%s/search?Subject:list=%s' % (url,c)
#                        unicode_alphabet = c[0] + c[1]
#                        if ((unicode_alphabet == alphabet) or (unicode_alphabet == self.make_lower(alphabet))) and ((('title', c),('url', category_url)) not in results):
#                            results.append((('title', c),('url', category_url)))
#            results.sort()
#            return [dict(item) for item in results]

#        elif alphabet:
#            for item in qc:
#                category = item.Subject
#                if category != ():
#                   for c in category:
#                        category_url = '%s/search?Subject:list=%s' % (url,c)
#                        if (c[0] == alphabet or c[0] == alphabet.lower()) and ((('title', c),('url', category_url)) not in results):
#                            results.append((('title', c),('url', category_url)))
#            results.sort()
#            return [dict(item) for item in results]
#        else:
#            return None
        character = self.request.get('character', None)
        results = []
        if character:
            uni_character = unicode(character)
            for item in qc:
                category = item.Subject
                if category != ():
                   for c in category:
                        category_url = '%s/search?Subject:list=%s' % (url,c)
                        first_character = unicode(c)[0]
                        if (first_character == uni_character or first_character == uni_character.lower()) and ((('title', c),('url', category_url)) not in results):
                            results.append((('title', c),('url', category_url)))
            results.sort()
            return [dict(item) for item in results]
        else:
            return None



#    def selected_category_alphabet(self):
#        """Returns selected category alphabet."""
#        return self.request.get('alphabet-category', None)

    def has_contents(self, character):
        """Return True if there are any contents for the category character."""
        qc = self.queryCatalog()
        category_tuple = [item.Subject for item in qc]
        results = []
        for subject in category_tuple:
            for c in subject:
                if c not in results:
                    results.append(c)
#        if (character == u'Ä') or (character == u'Ö') or (character == u'Å'):
#            contents = [c for c in results if (c[0] + c[1] == character) or (c[0] + c[1] == self.make_lower(character))]
#            if contents != []:
#                return True
#            else:
#                return False

#        else:
#            contents = [c for c in results if (c[0] == character) or (c[0] == character.lower())]
#            if contents != []:
#                return True
#            else:
#                return False

        contents = [c for c in results if (unicode(c)[0] == character) or (unicode(c)[0] == character.lower())]
        if contents != []:
            return True
        else:
            return False

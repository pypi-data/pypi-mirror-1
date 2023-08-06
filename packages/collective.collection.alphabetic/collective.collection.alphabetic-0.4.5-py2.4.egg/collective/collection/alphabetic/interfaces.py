from zope.interface import Interface
from zope.schema import Bool, TextLine
from collective.collection.alphabetic import CollectionAlphabeticMessageFactory as _

class ICharacters(Interface):
    def __call__(character_tokens, alphabet):
        """Returns characters."""

class ICharacterTokens(Interface):
    def __call__(character_tokens, use_alphabet):
        """Clean up tokens by eliminating duplications."""

class ICharacterOptions(Interface):

   use_alphabet = Bool(
                        title=_(u'Use alphabets?'),
                        description=_(u'Select this option if you want to use alphabets, A-Z.'),
                        default=True,
                        required=False,
                        )

   character_tokens = TextLine(
                        title=_(u'Characters'),
                        description=_(u'Input characters without any separation.'),
                        required=False,
                        )

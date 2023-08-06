# -*- coding: utf-8 -*-
from zope.interface import implements
from collective.collection.alphabetic.interfaces import ICharacters, ICharacterTokens
from collective.collection.alphabetic.config import ALPHABETS

class Characters(object):
    implements(ICharacters)
    def __call__(self, character_tokens, alphabet):
        if alphabet:
            alphabets = list(ALPHABETS)
            if character_tokens:
                tokens = [unicode(character) for character in character_tokens]
                return alphabets + tokens
            else:
                return alphabets
        else:
            if character_tokens is not None:
                return [unicode(character) for character in character_tokens]
            else:
                None

class CharacterTokens(object):
    implements(ICharacterTokens)
    def __call__(self, tokens, use_alphabet):
        uni_tokens = unicode(tokens.upper())
        tokens = u''
        if use_alphabet:
            alphabets = ALPHABETS
            for token in uni_tokens:
                if token not in (alphabets + tokens):
                    tokens += token
            tokens = tokens.replace(u' ', u'')
            return tuple(tokens)
        else:
            for token in uni_tokens:
                if token not in tokens:
                    tokens += token
            tokens= tokens.replace(u' ', u'')
            return tuple(tokens)

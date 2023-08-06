alphabet = 'abcdefghijklmnopqrstuvxyz'

import random
import os

from StringIO import StringIO

from plone.memoize import forever

from generation import generate_phrase
from generation import words
from generation import paragraphs

class StringContentProvider(object):
    def __init__(self, widget):
        self.widget = widget
        
    def setContentFor(self, field, instance):
        word_count = random.randint(4, 10)
        field.set(instance, generate_phrase(word_count))

class TextAreaContentProvider(object):
    def __init__(self, widget):
        self.widget = widget
        
    def setContentFor(self, field, instance):
        field.set(instance, random.choice(paragraphs))

class RichContentProvider(object):
    def __init__(self, widget):
        self.widget = widget

    def setContentFor(self, field, instance):
        section_count = 3
        paragraph_count = 2

        title_length = random.randint(4,7)
        
        out = StringIO()

        for section in range(section_count):
            out.write("<h2>%s</h2>" % generate_phrase(title_length))
            for paragraph in range(paragraph_count):
                out.write("<p>%s</p>" % random.choice(paragraphs))

        field.set(instance, out.getvalue())

class FileContentProvider(object):
    filename = 'resources/lipsum.pdf'
    
    @property
    @forever.memoize
    def data(self):
        path = os.path.dirname(__file__)
        f = open('%s/%s' % (path, self.filename), 'rb')
        data = f.read()
        f.close()
        return data

    def __init__(self, widget):
        self.widget = widget

    def setContentFor(self, field, instance):        
        field.set(instance, self.data)

class ImageContentProvider(FileContentProvider):
    filename ='resources/ferret.jpg'
    
    def __init__(self, widget):
        self.widget = widget

    def setContentFor(self, field, instance):
        field.set(instance, self.data)

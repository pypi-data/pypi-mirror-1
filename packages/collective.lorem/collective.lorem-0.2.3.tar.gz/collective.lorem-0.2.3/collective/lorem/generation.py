from Products.CMFCore import utils as cmfutils
from Products.CMFCore.WorkflowCore import WorkflowException

import collective.lorem

from interfaces import IFieldContentProvider
from zExceptions import BadRequest

import random

lorem = """\
Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Cras leo orci, tincidunt et, consequat ut, fermentum vestibulum, sapien. Maecenas porta diam quis sapien. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. Fusce pulvinar. Donec fermentum arcu et elit. Sed elementum diam. Phasellus consectetuer urna eu nibh. Quisque tincidunt eros vel lectus. Etiam congue erat eget metus. In laoreet. Mauris nibh justo, varius et, pellentesque in, feugiat eu, erat. Sed egestas eros non purus. Etiam a tortor hendrerit velit condimentum tempus. Nunc laoreet nisi ut mi. Donec mattis aliquam nulla. Nunc lacus. Phasellus eu diam."""

corpus = open(collective.lorem.__path__[0]+'/corpus.txt').read()

sentences = []
for paragraph in corpus.split('\n'):
    while '. ' in paragraph:
        i = paragraph.find('. ')
        sentence = paragraph[:i+1]
        paragraph = paragraph[i+2:]
        sentences.append(sentence)

# create paragraphs
paragraphs = []
while sentences:
    count = random.randint(5,15)
    paragraphs.append(" ".join(sentences[:count]))
    sentences = sentences[count:]

words = filter(None, corpus.replace('  ', ' ').replace(',', '').replace(';', '').replace('.', '').replace('\n', ' ').split(' '))

def generate_phrase(word_count):
    phrase = ' '.join([random.choice(words) for i in range(1,word_count+1)]).lower()
    return phrase[0].upper()+phrase[1:]

def normalize(u):
    return u.lower().replace(' ', '-')

def createNestedStructure(context, branches=1, depth=1):
    wtool = cmfutils.getToolByName(context, 'portal_workflow')
    
    for i in range(branches):
        while True:
            title = generate_phrase(random.randint(1,3))
            id_ = normalize(title)

            if id_ in context.objectIds():
                continue
            
            try:
                context.invokeFactory(id=id_, type_name='Folder')
            except BadRequest:
                continue
            
            break
        
        folder = context[id_]
        folder.setTitle(title)
        
        try:
            wtool.doActionFor(folder, 'publish')
        except WorkflowException:
            pass

        folder.reindexObject()
        
        if depth > 1:
            createNestedStructure(folder, branches=branches, depth=depth-1)

def createStandardContent(root, count=5):
    catalog = cmfutils.getToolByName(root, 'portal_catalog')
    wtool = cmfutils.getToolByName(root, 'portal_workflow')
    
    brains = catalog(path=root.getPhysicalPath(),
                     meta_type="ATFolder")
    for brain in brains:
        folder = brain.getObject()

        contenttypes = ['Document',
                        'News Item',
                        'Event',
                        'File',
                        'Image']

        for contenttype in contenttypes:
            for i in range(count):
                while True:
                    title = generate_phrase(random.randint(1,6))
                    id_ = normalize(title)

                    if id_ in folder.objectIds():
                        continue
                    
                    try:
                        folder.invokeFactory(id=id_, type_name=contenttype)
                    except BadRequest:
                        continue
                    
                    break
                
                content = folder[id_]
                
                loremipsumize(content)

                content.setTitle(title)
                
                try:
                    wtool.doActionFor(content, 'publish')
                except WorkflowException:
                    pass

                content.reindexObject()
                
def loremipsumize(content):
    for f in content.Schema().fields():
        fieldname = f.getName()
        widget = f.widget
        schemata = f.schemata

        # ignore `id`
        if fieldname ==  'id':
            continue

        # ignore metadata
        if schemata in ['ownership', 'metadata', 'categorization', 'dates', 'settings']:
            continue

        try:
            provider = IFieldContentProvider(widget)
        except TypeError:
            continue
        
        provider.setContentFor(f, content)

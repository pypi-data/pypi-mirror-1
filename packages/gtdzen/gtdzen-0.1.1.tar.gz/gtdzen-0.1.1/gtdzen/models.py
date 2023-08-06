from elixir import *
from utils import get_or_create
from pdb import set_trace

class Task(Entity):
    title = Field(Unicode(40))
    note = Field(UnicodeText)
    tags = ManyToMany('Tag')
    priority = Field(Float)
    done = Field(Boolean, default = False)

    using_options(tablename='tasks', order_by='-priority')

    def __str__(self):
        return u'"%s" / %s (%s)' % (self.title, self.priority, ', '.join(map(unicode, self.tags)))

    def __repr__(self):
        return u'<Task "%s" with tags %s>' % (self.title, ', '.join(map(unicode, self.tags)))

    def setTags(self, tags):
        self.tags = [get_or_create(Tag, title = tag) for tag in tags]

class Tag(Entity):
    title = Field(Unicode(40), unique = True)
    tasks = ManyToMany('Task')

    using_options(tablename='tags', order_by='title')

    def __str__(self):
        return self.title

    def __repr__(self):
        return u'<Tag "%s">' % self.title

    @property
    def open_tasks(self):
        return [t for t in self.tasks if not t.done]

    @property
    def closed_tasks(self):
        return [t for t in self.tasks if t.done]


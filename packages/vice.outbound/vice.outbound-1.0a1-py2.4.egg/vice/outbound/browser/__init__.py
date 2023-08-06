# Empty, just here to turn it into an importable module.

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.component import provideAdapter
# XXX TODO: Bad, need to replce with below
legacy_rss = ViewPageTemplateFile('rss-1.0.pt')
legacy_rss = NamedTemplateImplementation(legacy_rss)
# All feed formats should be named for extensibility
rss1 = ViewPageTemplateFile('rss-1.0.pt')
rss1 = NamedTemplateImplementation(rss1)
rss2 = ViewPageTemplateFile('rss-2.0.pt')
rss2 = NamedTemplateImplementation(rss2)
atom1 = ViewPageTemplateFile('atom-1.0.pt')
atom1 = NamedTemplateImplementation(atom1)

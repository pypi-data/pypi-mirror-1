from zope.app.form.browser.objectwidget import ObjectWidget
from zope.app.form.browser.objectwidget import ObjectWidgetView
from zope.app.form.browser import SequenceWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from vice.outbound.interfaces import IFeedConfig, IFeedSettings
from zope.formlib.form import Fields
from zope.component import getUtility

class ConfigurableObjectWidget(ObjectWidget):
    """Custom ObjectWidget for the purpose of binding it's display to a
    specific page template.
    """  

    def __init__(self, context, request, factory, **kw):
        super(ConfigurableObjectWidget, self).__init__(context, request, factory, **kw)

        # bind to a specific page template
        self.view = SpecificTemplateWidgetView(self, request)

    def subwidgets(self):
        return [self.getSubWidget(name) for name in self.names
                if not is_filtered_field(name)]

class SpecificTemplateWidgetView(ObjectWidgetView):
    """Seems to be required for the template binding."""
    template = ViewPageTemplateFile('feed_config.pt')

class ConfigurableSequenceWidget(SequenceWidget):
    """Custom SequenceWidget for the purpose of binding it's display to a
    specific page template.
    """ 
    # bind to a specific page template
    template = ViewPageTemplateFile('feed_config_grid.pt')

    @property
    def config_field_titles(self):
        """Return list of field titles for the table headers."""
        return [f.field.title for f in Fields(IFeedConfig)
                if not is_filtered_field(f.field.__name__)]

def is_filtered_field(name):
    if name == 'published_url' \
       and not getUtility(IFeedSettings).published_url_enabled:
        return True
    if name == 'recurse' \
       and not getUtility(IFeedSettings).recursion_enabled:
        return True
    return False
try:
    # These imports are for zope2, they'll fail on zope3
    from Products.Five.formlib.formbase import EditForm
    from Products.Five.viewlet.viewlet import ViewletBase
    from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile as ViewPageTemplateFile
except ImportError:
    # These are the imports for zope3
    from zope.formlib.form import EditForm
    from zope.viewlet.viewlet import ViewletBase
    from zope.app.pagetemplate import ViewPageTemplateFile

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser.boolwidgets import CheckBoxWidget
from zope.formlib.form import Fields
from vice.outbound.interfaces import IFeedConfigs
from vice.outbound.feedconfig import FeedConfig
from vice.outbound.browser.widgets import ConfigurableObjectWidget 
from vice.outbound.browser.widgets import ConfigurableSequenceWidget 


class FeedConfigsEditForm(EditForm):
    """Edit form for feed configurations, used to edit the feeds on a container.
    """

    form_fields = Fields(IFeedConfigs)

    # custom widget factories to be provided for the subwidgets in
    # ConfigurableObjectWidget
    row_custom_widgets = {'recurse_widget': CustomWidgetFactory(CheckBoxWidget),
                          'enabled_widget': CustomWidgetFactory(CheckBoxWidget),
                          'auto_discover_widget': CustomWidgetFactory(CheckBoxWidget)}

    ow = CustomWidgetFactory(ConfigurableObjectWidget, FeedConfig, 
                             **row_custom_widgets)
    sw = CustomWidgetFactory(ConfigurableSequenceWidget, subwidget=ow)

    form_fields['configs'].custom_widget = sw

    label = u'Configure feeds'


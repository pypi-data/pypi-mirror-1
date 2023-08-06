#this might go away.

from view import View

class ViewFactory:
    def create(self, view_config, id=None):
        kw = view_config.get_widget_args()
        if id == None:
            id = view_config.__class__.__name__+'_'+view_config.identifier
        kw['id'] = id.replace('.', '_')
        parentWidget = view_config.widget_type(**kw)
        return View(parentWidget, view_config)

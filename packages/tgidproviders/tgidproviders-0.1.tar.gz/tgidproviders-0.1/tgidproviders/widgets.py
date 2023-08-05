import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

js_dir = pkg_resources.resource_filename("tgidproviders",
                                         "static/javascript")
register_static_directory("tgidproviders", js_dir)

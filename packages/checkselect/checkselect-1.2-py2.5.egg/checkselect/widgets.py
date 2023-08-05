import pkg_resources

from turbogears.widgets import CSSLink, JSLink, \
                               WidgetDescription, register_static_directory, \
                               CheckBoxList, mochikit, js_location

static_dir = pkg_resources.resource_filename("checkselect", "static")
register_static_directory("checkselect", static_dir)

js_dir = pkg_resources.resource_filename("checkselect", "static/javascript")

checkselect_css = [CSSLink("checkselect", "css/checkselect.css")]
checkselect_js = [
    mochikit,
    JSLink("checkselect", "javascript/checkselect.js",
        location = js_location.bodytop),
    ]

__all__ = [
    'CheckSelect',
    'CheckSelectAdd',
    ]


class CheckSelect(CheckBoxList):
    """
CheckSelect aims to solve a problem found with Multiple Select fields
where it isn't possible to specify their widths, messing up with some
layouts.  It also aims to make selecting multiple choices easier and
more accessible for users of your application.

This is a widgetized version of Nicholas Rougeux code at
http://c82.net/article.php?ID=25 that extends TurboGears' default
CheckBoxList code.
    """
    template = "checkselect.templates.checkselect"
    css = checkselect_css
    javascript = checkselect_js


class CheckSelectAdd(CheckBoxList):
    """
CheckSelectAdd is an alternative implementation of CheckSelect that
allows the user to click on a hyperlink to perform some action, most
commonly add new options to the list of available choices.
    """
    template = "checkselect.templates.checkselectadd"
    css = checkselect_css
    javascript = checkselect_js

    params = ['link', 'text', 'target']
    params_doc = {
        'link':'Hyperlink to where the user should be directed',
        'text':'Descriptive text for the link',
        'target':'Target for the action',
    }


    target = ''
    text = 'Add new entry'


class CheckSelectDesc(WidgetDescription):
    name = "CheckSelect"
    for_widget = CheckSelect("your_checkselect",
        options=[(1, "Python"),
            (2, "Java"),
            (3, "Pascal"),
            (4, "Ruby"),
            (5, "JavaScript"),
            (6, "C"),
            (7, "C++"),
            (8, "Eiffel"),
            (9, "Haskell"),
            (10, "SmallTalk"),
            (11, "ADA"),
            (12, "APL"),
            (13, "Perl"),
            (14, "A very long entry to see what happens when this exceeds the horizontal size of the list")],
        default=[1,5])


class CheckSelectAddDesc(WidgetDescription):
    name = "CheckSelectAdd"
    for_widget = CheckSelectAdd("your_checkselect",
        options=[(1, "Python"),
            (2, "Java"),
            (3, "Pascal"),
            (4, "Ruby"),
            (5, "JavaScript"),
            (6, "C"),
            (7, "C++"),
            (8, "Eiffel"),
            (9, "Haskell"),
            (10, "SmallTalk"),
            (11, "ADA"),
            (12, "APL"),
            (13, "Perl"),
            (14, "A very long entry to see what happens when this exceeds the horizontal size of the list")],
        link = '#',
        default=[1,5])
import itertools
from datetime import datetime

from turbogears import validators, expose
from turbojson import jsonify
from turbogears.widgets.base import CSSLink, JSLink, CSSSource, JSSource, \
                                    Widget, WidgetsList, static, mochikit, \
                                    CoreWD
from turbogears.widgets.i18n import CalendarLangFileLink
from turbogears.widgets.forms import FormField, CompoundFormField, TextField, \
                                    HiddenField, TableForm, CheckBox, \
                                    RadioButtonList
from turbogears.widgets.rpc import RPC

__all__ = ["CalendarDatePicker", "CalendarDateTimePicker", "AutoCompleteField",
           "LinkRemoteFunction", "RemoteForm", "AjaxGrid", "URLLink"]


class CalendarDatePicker(FormField):
    """Use a Javascript calendar system to allow picking of calendar dates."""
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
    <input type="text" id="${field_id}" class="${field_class}" name="${name}" value="${strdate}" py:attrs="attrs"/>
    <input type="button" id="${field_id}_trigger" class="date_field_button" value="${button_text}"/>
    <script type="text/javascript">
    Calendar.setup(
    {
        inputField : "${field_id}",
        ifFormat : "${format}",
        button : "${field_id}_trigger"
        <span py:if="picker_shows_time" py:replace="', showsTime : true'"/>
    }
    );
    </script>
    </div>
    """
    params = ["attrs", "skin", "picker_shows_time", "button_text",
        "format", "calendar_lang"]
    params_doc = {'attrs': 'Extra attributes',
        'skin': 'For alternate skins, such as "calendar-blue" or "skins/aqua/theme"',
        'picker_shows_time': 'Whether the calendar should let you pick a time, too',

        'button_text': 'Text for the button that will show the calendar picker',
        'format': 'The date format (default is mm/dd/yyyy)',
        'calendar_lang': 'The language to be used in the calendar picker.'}
    attrs = {}
    skin = "calendar-system"
    picker_shows_time = False
    button_text = "Choose"
    format = "%m/%d/%Y"
    calendar_lang = None
    _default = None

    def __init__(self, name=None, default=None, not_empty=True,
                 calendar_lang=None, validator=None, format=None, **kw):
        super(CalendarDatePicker, self).__init__(name, **kw)
        self.not_empty = not_empty
        if default is not None or not self.not_empty:
            self._default = default
        if format is not None:
            self.format = format
        if validator is None:
            self.validator = validators.DateTimeConverter(
                format=self.format, not_empty=self.not_empty)
        else:
            self.validator = validator
        if calendar_lang:
            self.calendar_lang = calendar_lang
        javascript = [JSLink(static, "calendar/calendar.js"),
            JSLink(static, "calendar/calendar-setup.js")]
        javascript.append(CalendarLangFileLink(static,
            language=self.calendar_lang))
        self.javascript = self.javascript + javascript
        if self.skin:
            css = [CSSLink(static, "calendar/%s.css" % self.skin)]
            self.css = self.css + css

    def _get_default(self):
        if self._default is None and self.not_empty:
            return datetime.now()
        return self._default
    default = property(_get_default)

    def update_params(self, d):
        super(CalendarDatePicker, self).update_params(d)
        if hasattr(d['value'], 'strftime'):
            d['strdate'] = d['value'].strftime(d['format'])
        else:
            d['strdate'] = d['value']


class CalendarDatePickerDesc(CoreWD):
    name = "Calendar"
    for_widget = CalendarDatePicker("date_picker")


class CalendarDateTimePicker(CalendarDatePicker):
    format = "%Y/%m/%d %H:%M"
    picker_shows_time = True


class CalendarDateTimePickerDesc(CoreWD):
    name = "Calendar with time"
    for_widget = CalendarDateTimePicker("datetime_picker")


class AutoCompleteField(CompoundFormField):
    """Performs Ajax-style autocompletion by requesting search
    results from the server as the user types."""

    template = """
    <div xmlns:py="http://purl.org/kid/ns#" id="${field_id}">
    <script language="JavaScript" type="text/JavaScript">
        AutoCompleteManager${field_id} = new AutoCompleteManager('${field_id}',
        '${text_field.field_id}', '${hidden_field.field_id}',
        '${search_controller}', '${search_param}', '${result_name}',${str(only_suggest).lower()},
        '${show_spinner and tg.url([tg.widgets, 'turbogears.widgets/spinner.gif']) or None}',
        ${complete_delay}, ${str(take_focus).lower()});
        addLoadEvent(AutoCompleteManager${field_id}.initialize);
    </script>

    ${text_field.display(value_for(text_field), **params_for(text_field))}
    <img py:if="show_spinner" id="autoCompleteSpinner${field_id}"
        src="${tg.url([tg.widgets, 'turbogears.widgets/spinnerstopped.png'])}" alt=""/>
    <div class="autoTextResults" id="autoCompleteResults${field_id}"/>
    ${hidden_field.display(value_for(hidden_field), **params_for(hidden_field))}
    </div>
    """
    javascript = [mochikit, JSLink(static,"autocompletefield.js")]
    css = [CSSLink(static,"autocompletefield.css")]
    member_widgets = ["text_field", "hidden_field"]
    params = ["search_controller", "search_param", "result_name", "attrs",
        "only_suggest", "complete_delay", "take_focus", "show_spinner"]
    params_doc = {'attrs': 'Extra attributes',
        'search_controller': 'Name of the controller returning the auto completions',
        'search_param': 'Name of the search parameter ("*" passes all form fields)',
        'result_name': 'Name of the result list returned by the controller',
        'only_suggest': 'If true, pressing enter does not automatically submit the first list item.',
        'complete_delay': 'Delay (in seconds) before loading new auto completions',
        'take_focus': 'If true, take focus on load.',
        'show_spinner': 'If false, the spinner (load indicator) is not shown.'}
    text_field = TextField(name="text")
    hidden_field = HiddenField(name="hidden")
    attrs = {}
    search_controller = ""
    search_param = "searchString"
    result_name = "textItems"
    only_suggest = False
    complete_delay = 0.200
    take_focus = False
    show_spinner = True


class AutoCompleteFieldDesc(CoreWD):
    name = "Auto Complete"

    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California",
              "Colorado", "Connecticut", "Delaware", "Florida",
              "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana",
              "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
              "Maryland", "Massachusetts", "Michigan", "Minnesota",
              "Mississippi", "Missouri", "Montana", "Nebraska",
              "Nevada", "New Hampshire", "New Jersey", "New Mexico",
              "New York", "North Carolina", "North Dakota", "Ohio",
              "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
              "South Carolina", "South Dakota", "Tennessee", "Texas",
              "Utah", "Vermont", "Virginia", "Washington",
              "West Virginia", "Wisconsin", "Wyoming"]

    template = """
    <div>
        Please choose a state:<br/>
        ${for_widget.display()}
    </div>
    """
    full_class_name = "turbogears.widgets.AutoCompleteField"

    def __init__(self, *args, **kw):
        super(AutoCompleteFieldDesc, self).__init__(*args, **kw)
        self.for_widget = AutoCompleteField(name="state",
                                    search_controller="%s/search" %
                                                    self.full_class_name,
                                    search_param="statename",
                                    result_name="states")

    def search(self, statename):
        statename = statename.lower()
        return dict(states=
                filter(lambda item: statename in item.lower(), self.states))
    search = expose(format="json")(search)


class LinkRemoteFunction(RPC):
    """ Returns a link that executes a POST asynchronously
    and updates a DOM Object with the result of it """

    template = """
    <a xmlns:py="http://purl.org/kid/ns#" name="${name}" py:attrs="attrs" onclick="${js}" href="#">${value}</a>
    """
    params = ["attrs"]
    attrs = {}


class LinkRemoteFunctionDesc(CoreWD):
    name = "Ajax remote function"

    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California",
              "Colorado", "Connecticut", "Delaware", "Florida",
              "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana",
              "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
              "Maryland", "Massachusetts", "Michigan", "Minnesota",
              "Mississippi", "Missouri", "Montana", "Nebraska",
              "Nevada", "New Hampshire", "New Jersey", "New Mexico",
              "New York", "North Carolina", "North Dakota", "Ohio",
              "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
              "South Carolina", "South Dakota", "Tennessee", "Texas",
              "Utah", "Vermont", "Virginia", "Washington",
              "West Virginia", "Wisconsin", "Wyoming"]

    template = """
    <div>
        ${for_widget.display("States starting with 'N'", update="items")}
        <div id="items">states</div>
    </div>
    """
    full_class_name = "turbogears.widgets.LinkRemoteFunction"

    def __init__(self, *args, **kw):
        super(LinkRemoteFunctionDesc, self).__init__(*args, **kw)
        self.for_widget = LinkRemoteFunction(
            name="state", action="%s/search_linkrf" % self.full_class_name,
            data = dict(state_starts_with="N"))

    def search_linkrf(self, state_starts_with):
        return '<br/>'.join(
                filter(lambda item: item.startswith(state_starts_with),
                       self.states)
       )
    search_linkrf = expose()(search_linkrf)


class RemoteForm(RPC, TableForm):
    """A TableForm that submits the data asynchronously and loads the resulting
    HTML into a DOM object"""

    def update_params(self, d):
        super(RemoteForm, self).update_params(d)
        d['form_attrs']['onSubmit'] = "return !remoteFormRequest(this, '%s', %s);" % (
            d.get("update", ''),
            jsonify.encode(self.get_options(d)),
        )


class RemoteFormDesc(CoreWD):
    name = "AJAX Form"

    class TestFormFields(WidgetsList):
        name = TextField()
        age = TextField()
        check = CheckBox()
        radio = RadioButtonList(options=[(1, "Python"),
                                         (2, "Java"),
                                         (3, "Pascal"),
                                         (4, "Ruby")],
                                default=4)

    template = """
    <div>
        ${for_widget.display()}
        <div id="post_data">&nbsp;</div>
    </div>
    """
    full_class_name = "turbogears.widgets.RemoteForm"

    def __init__(self, *args, **kw):
        super(RemoteFormDesc, self).__init__(*args, **kw)
        self.for_widget = RemoteForm(
            fields = self.TestFormFields(),
            name="remote_form",
            update = "post_data",
            action = "%s/post_data_rf" % self.full_class_name,
            before = "alert('pre-hook')",
            confirm = "Confirm?",
        )

    def post_data_rf(self, **kw):
        return """Received data:<br/>%r""" % kw
    post_data_rf = expose()(post_data_rf)


ajaxgridcounter = itertools.count()

class AjaxGrid(Widget):
    """ AJAX updateable datagrid based on widget.js grid. """

    template = """<div id="${id}" xmlns:py="http://purl.org/kid/ns#">
    <a py:if="refresh_text"
       href="#"
       onclick="javascript:${id}_AjaxGrid.refresh(${defaults});return false;">
       ${refresh_text}
    </a>
    <div id="${id}_update"></div>
    <script type="text/javascript">
        addLoadEvent(partial(${id}_AjaxGrid.refresh, ${defaults}));
    </script>
    </div>
    """

    params = ["refresh_text", "id", "defaults"]

    defaults = {}
    refresh_text = "Update"
    id = "ajaxgrid_%d" % ajaxgridcounter.next()

    def __init__(self, refresh_url, *args, **kw):
        super(AjaxGrid, self).__init__(*args, **kw)
        target = "%s_update" % self.id
        self.javascript = [
            mochikit,
            JSLink("turbogears", "js/widget.js"),
            JSLink(static, "ajaxgrid.js"),
            JSSource("""
                %(id)s_AjaxGrid = new AjaxGrid('%(refresh_url)s', '%(target)s');
            """ % dict(id=self.id, refresh_url=refresh_url, target=target)
            ),
        ]

    def update_params(self, d):
        super(AjaxGrid, self).update_params(d)
        d["defaults"] = jsonify.encode(d["defaults"])


class AjaxGridDesc(CoreWD):
    name = "Ajax Grid"

    def facgen(n):
        total = 1
        yield 0, 1
        for x in xrange(1, n+1):
            total *= x
            yield x, total
    facgen = staticmethod(facgen)


    full_class_name = "turbogears.widgets.AjaxGrid"

    def __init__(self, *args, **kw):
        super(AjaxGridDesc, self).__init__(*args, **kw)
        self.for_widget = AjaxGrid(
            refresh_url = "%s/update" % self.full_class_name,
            # Dummy default params, just POC
            defaults = dict(),
        )
        self.update_count = itertools.count()

    def update(self):
        return dict(
            headers = ["N", "fact(N)"],
            rows = list(self.facgen(self.update_count.next())),
        )
    update = expose(format="json")(update)


class URLLink(FormField):
    template = """
    <a xmlns:py="http://purl.org/kid/ns#"
       href="$link"
       target="$target"
       py:attrs="attrs"
    >$text</a>
    """
    params = ["target", "text", "link", "attrs"]
    attrs = {}
    params_doc = {'link': 'Hyperlink',
                  'target': 'Specify where the link should be opened',
                  'text': 'The message to be shown for the link',
                  'attrs': 'Extra attributes'}

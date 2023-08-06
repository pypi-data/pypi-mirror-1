import re
import turbogears
import cherrypy
import turbogears.testutil as testutil
from turbogears import widgets, validators, validate, expose, error_handler

def setup_module():
    testutil.start_server()

def teardown_module():
    testutil.stop_server()


def test_required_fields():
    """
    Required fields are automatically discovered from the form validator and
    marked with the "requiredfield" css class.
    """
    class MyFields(widgets.WidgetsList):
        name = widgets.TextField(validator=validators.String())
        comment = widgets.TextArea(validator=validators.String(not_empty=True))
    form = widgets.TableForm(fields=MyFields())

    class MyRoot(turbogears.controllers.RootController):
        def test(self):
            return dict(form=form)
        test = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test)

    app = testutil.make_app(MyRoot)
    response = app.get("/test")
    output = response.body.lower()

    print output
    name_p = 'name="comment"'
    class_p = 'class="textarea requiredfield"'
    assert (re.compile('.*'.join([class_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, class_p])).search(output)
    )
    name_p = 'name="name"'
    class_p = 'class="textfield"'
    assert (re.compile('.*'.join([class_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, class_p])).search(output)
    )

def test_two_form_in_the_same_page():
    """
    Two different forms containing some fields with the same name can be
    validated and re-displayed on the same page with right values and errors.
    """
    class MyFields(widgets.WidgetsList):
        age = widgets.TextField(validator=validators.Int())
        email = widgets.TextArea(validator=validators.Email())
    form1 = widgets.TableForm(name="form1", fields=MyFields())
    form2 = widgets.TableForm(name="form2", fields=MyFields())

    class MyRoot(turbogears.controllers.RootController):

        #@expose(template="turbogears.widgets.tests.two_forms")
        #@validate(form=form1)
        #@error_handler('test')
        def test(self, age, email):
            validated_form = cherrypy.request.validated_form.name
            form1_valid = form1.is_validated
            form2_valid = form2.is_validated
            return dict(form1=form1, form2=form2, validated_form=validated_form,
                        form1_valid=form1_valid, form2_valid=form2_valid)
        test = turbogears.expose(template="kid:turbogears.widgets.tests.two_forms")(test)
        test = turbogears.validate(form=form1)(test)
        test = turbogears.error_handler(test)(test)


        def test2(self):
            validated_form = cherrypy.request.validated_form.name
            form1_valid = form1.is_validated
            form2_valid = form2.is_validated
            return dict(form=form2, validated_form=validated_form,
                        form1_valid=form1_valid, form2_valid=form2_valid)
        test2 = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test2)
        test2 = turbogears.validate(form=form2)(test2)
        test2 = turbogears.error_handler(test2)(test2)

        def test3(self):
            validated_form = cherrypy.request.validated_form.name
            form1_valid = form1.is_validated
            form2_valid = form2.is_validated
            return dict(form=form1, validated_form=validated_form,
                        form1_valid=form1_valid, form2_valid=form2_valid)
        test3 = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test3)
        test3 = turbogears.validate(form=form2)(test3)
        test3 = turbogears.error_handler(test3)(test3)

    app = testutil.make_app(MyRoot)

    response = app.get("/test?age=foo&email=bar")
    output = response.body.lower()

    assert response.raw['validated_form'] == 'form1'
    assert response.raw['form1_valid']
    assert not response.raw['form2_valid']
    value_p = 'value="foo"'
    id_p = 'id="form1_age"'
    assert (re.compile('.*'.join([value_p, id_p])).search(output) or
            re.compile('.*'.join([id_p, value_p])).search(output)
    )
    value_p = 'value="foo"'
    id_p = 'id="form2_age"'
    assert not (re.compile('.*'.join([value_p, id_p])).search(output) or
            re.compile('.*'.join([id_p, value_p])).search(output)
    )

    response = app.get("/test2?age=foo&email=bar")
    output = response.body.lower()

    assert response.raw['validated_form'] == 'form2'
    assert not response.raw['form1_valid']
    assert response.raw['form2_valid']
    assert 'value="foo"' in output
    assert '>bar<' in output
    assert 'class="fielderror"' in output

    response = app.get("/test3?age=foo&email=bar")
    output = response.body.lower()

    assert response.raw['validated_form'] == 'form2'
    assert not response.raw['form1_valid']
    assert response.raw['form2_valid']
    assert 'value="foo"' not in output
    assert '>bar<' not in output
    assert 'class="fielderror"' not in output

def test_repeating_fields():
    repetitions = 5

    class MyFields(widgets.WidgetsList):
        name = widgets.TextField(validator=validators.String(not_empty=True))
        comment = widgets.TextField(validator=validators.String())

    form = widgets.TableForm(name="form", fields=[widgets.RepeatingFieldSet(
            name="repeat", fields=MyFields(), repetitions=repetitions)])

    class MyRoot(turbogears.controllers.RootController):
        def test(self):
            return dict(form=form)
        test = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test)

        def test_value(self):
            value = dict(repeat=[{'name':'foo', 'comment':'hello'},
                                 None,
                                 None,
                                 {'name':'bar', 'comment':'byebye'}])
            return dict(form=form, value=value)
        test_value = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test_value)

        def test_validation(self):
            validation_errors = cherrypy.request.validation_errors
            return dict(form=form, validation_errors=validation_errors)
        test_validation = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test_validation)
        test_validation = turbogears.validate(form=form)(test_validation)
        test_validation = turbogears.error_handler(test_validation)(test_validation)

    app = testutil.make_app(MyRoot)
    response = app.get("/test")
    output = response.body.lower()
    for i in range(repetitions):
        assert 'id="form_repeat_%i"' % i in output
        assert 'name="repeat-%i.name"' % i in output
        assert 'id="form_repeat_%i_name"' % i in output
        assert 'name="repeat-%i.comment"' % i in output
        assert 'id="form_repeat_%i_comment"' % i in output

    response = app.get("/test_value")
    output = response.body.lower()
    name_p = 'name="repeat-0.name"'
    value_p = 'value="foo"'
    assert (re.compile('.*'.join([value_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, value_p])).search(output)
    )
    name_p = 'name="repeat-0.comment"'
    value_p = 'value="hello"'
    assert (re.compile('.*'.join([value_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, value_p])).search(output)
    )
    name_p = 'name="repeat-3.name"'
    value_p = 'value="bar"'
    assert (re.compile('.*'.join([value_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, value_p])).search(output)
    )
    name_p = 'name="repeat-3.comment"'
    value_p = 'value="byebye"'
    assert (re.compile('.*'.join([value_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, value_p])).search(output)
    )
    name_p = 'name="repeat-1.name"'
    value_p = 'value=""'
    assert (re.compile('.*'.join([value_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, value_p])).search(output)
    )
    name_p = 'name="repeat-1.comment"'
    value_p = 'value=""'
    assert (re.compile('.*'.join([value_p, name_p])).search(output) or
            re.compile('.*'.join([name_p, value_p])).search(output)
    )

    #FIXME: Why is stopping the server necessary here?
    testutil.stop_server(tg_only = True)
    app = testutil.make_app(MyRoot)
    testutil.start_server()

    response = app.get("/test_validation?repeat-0.name=foo&repeat-1.name="
        "&repeat-2.name=bar&repeat-3.name=&repeat-4.name=")
    output = response.body.lower()
    print "Raw", response.raw
    validation_errors = response.raw['validation_errors']
    assert validation_errors.has_key("repeat")
    assert isinstance(validation_errors["repeat"], list)
    assert validation_errors["repeat"][0] is None
    assert validation_errors["repeat"][1].has_key("name")
    assert validation_errors["repeat"][2] is None
    assert validation_errors["repeat"][3].has_key("name")
    assert validation_errors["repeat"][4].has_key("name")

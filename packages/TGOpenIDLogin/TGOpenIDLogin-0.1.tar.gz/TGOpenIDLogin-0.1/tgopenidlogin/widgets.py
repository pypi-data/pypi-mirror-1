import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory
from turbogears import widgets

resource_dir = pkg_resources.resource_filename("tgopenidlogin",
                                         "static")
register_static_directory("tgopenidlogin", resource_dir)

openidcss = CSSLink("tgopenidlogin", "css/openid.css", media="screen")

import cherrypy

class OpenIDText(widgets.TextField):
    label = "OpenID"
    name = "identity_url"
    field_class = "openid_login"
    attrs = {'size': 10, 'class': 'openid_login'}
    css = [openidcss] 

class OpenIDLoginForm(widgets.Form):
    template = """
    <form xmlns:py="http://purl.org/kid/ns#"
        name="${name}"
        action="${action}"
        method="${method}"
        class="tableform"
        py:attrs="form_attrs"
    >
        <div py:for="field in hidden_fields" 
            py:replace="field.display(value_for(field), **params_for(field))" 
        />
        <table border="0" cellspacing="0" cellpadding="2">
            <tr py:for="i, field in enumerate(fields)" 
                class="${i%2 and 'odd' or 'even'}"
            >
                <th>
                    <label class="fieldlabel" for="${field.field_id}" py:content="field.label" />
                </th>
                <td>
                    <span py:replace="field.display(value_for(field), **params_for(field))" />
                    <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
                    <span py:if="field.help_text" class="fieldhelp" py:content="field.help_text" />
                </td>
            </tr>
            <tr>
                <td>&#160;</td>
                <td py:content="submit.display(submit_text)" />
            </tr>
        </table>
    </form>
    """
    params = ["openidrequest"]
    params_doc = {'openidrequest' : 'An OpenID request object to carry through'}
    openidrequest = None
    submit_text = "Log in"
    action = "/openid/loginBegin"

    def update_params(self, d):
        super(OpenIDLoginForm, self).update_params(d)
        hidden_fields = d.setdefault('hidden_fields', [])
        forward_url = widgets.HiddenField(name="forward_url", default=cherrypy.request.path)
        forward_url.hidden = True
        hidden_fields.append(forward_url)

    fields = [
        OpenIDText(name="identity_url"),
    ]



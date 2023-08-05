import pkg_resources
from cherrypy import request
#from turbogears.widgets import ListForm, TextField, RepeatingFormField, SingleSelectField
#from turbogears import validators
from turbogears.widgets import RepeatingFormField
from turbogears.widgets import CompoundWidget
from turbogears.widgets.base import register_static_directory
from turbogears.widgets.base import JSLink, CSSLink

my_static = "dyn_static"
directory = pkg_resources.resource_filename(__name__, "static")
register_static_directory(my_static, directory)

class AppendableFormFieldList(RepeatingFormField):
    template = '''
    <div class="appendable_form_field_list" xmlns:py="http://purl.org/kid/ns#">
    <ol id="${field_id}">
        <li py:for="repetition in repetitions"
            class="${field_class}"
            id="${field_id}_${repetition}">
            <div py:for="field in hidden_fields"
                py:replace="field.display(value_for(field), **params_for(field))"
            />
            <ul>
                <li py:for="field in fields">
                    <label class="fieldlabel" for="${field.field_id}"
                           py:content="field.label" />
                    <span py:content="field.display(value_for(field),
                          **params_for(field))" />
                    <span py:if="error_for(field)" class="fielderror"
                          py:content="error_for(field)" />
                    <span py:if="field.help_text" class="fieldhelp"
                          py:content="field_help_text" />
                </li>
                <li>
                <a
                href="javascript:AppendableFormFieldList.removeItem('${field_id}_${repetition}')">
                <img src='${tg.url([tg.widgets, "dyn_static/images/bin_empty.png"])}'
 border="0"
                     title="Remover item"
                     alt="Remover item" />
                </a></li>
            </ul>
        </li>
    </ol>
    <a id="doclink"
       href="javascript:AppendableFormFieldList.addItem('${field_id}');">
       <img src="${tg.tg_static}/images/add.png" alt="Adicionar item"
            title="Adicionar item" border="0" />
       Adicionar
    </a>
    </div>
    '''
    javascript = [JSLink(my_static, 'javascript/appendable_form_field_list.js'), ]
    css = [CSSLink(my_static, 'css/appendable_form_field_list.css'), ]

    def display(self, value=None, **params):
        if value and isinstance(value, list) and len(value) > 1:
            params['repetitions'] = len(value)
        return super(AppendableFormFieldList, self).display(value, **params)

# def createForm():
#     tf1 = TextField(name='first_name', label='First Name',
#                     validator=validators.UnicodeString(notEmpty=True))
#     tf2 = TextField(name='last_name', label='Last Name')
#     sf3 = SingleSelectField(name='sexo', options=((1, 'masculino'), (2, 'feminino')))
#     afs = AppendableFormFieldList(label='Appendable Form Field List',
#                                   fields=[tf1, tf2, sf3])
#     form = ListForm('myform', fields=[afs, ], action='save_data',
#                     submit_text='Submit Data')
#     return form

# form = createForm()

"""
formbase Module

Classes to create form widgets.

Copyright (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2008
Released under MIT license.
"""
import inspect
from tw.api import Widget
from tw.forms import HiddenField, TableForm
from viewbase import ViewBase
from formencode import Schema, All
from sprox.validators import UniqueValue
from formencode.validators import UnicodeString, String
from widgetselector import SAWidgetSelector
from sprox.metadata import FieldsMetadata
from validatorselector import SAValidatorSelector

class FilteringSchema(Schema):
    """This makes formencode work for most forms, because some wsgi apps append extra values to the parameter list."""
    filter_extra_fields = True
    allow_extra_fields = True

class FormBase(ViewBase):
    """

    :Modifiers:


    Modifiers defined in this class

    +-----------------------------------+--------------------------------------------+------------------------------+
    | Name                              | Description                                | Default                      |
    +===================================+============================================+==============================+
    | __base_widget_type__              | What widget to use for the form.           | TableForm                    |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __widget_selector_type__          | What class to use for widget selection.    | SAWidgetSelector             |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __validator_selector_type__       | What class to use for validator selection. | SAValidatorSelector          |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __require_fields__                | Specifies which fields are required.       | []                           |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __check_if_unique__               | Set this to True for "new" forms.  This    | False                        |
    |                                   | causes Sprox to check if there is an       |                              |
    |                                   | existing record in the database which      |                              |
    |                                   | matches the field data.                    |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __field_validators__              | A dictionary of validators indexed by      | {}                           |
    |                                   | fieldname.                                 |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __field_validator_types__         | Types of validators to use for each field  | {}                           |
    |                                   | (allow sprox to set the attribute of the   |                              |
    |                                   | validators).                               |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __base_validator__                | A validator to attch to the form.          | None                         |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __validator_selector__            | What object to use to select field         | None                         |
    |                                   | validators.                                |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __metadata_type__                 | What metadata type to use to get schema    | FieldsMetadata               |
    |                                   | info on this object                        |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __dropdown_view_names__           | list of names to use for discovery of view | None                         |
    |                                   | fieldnames for dropdowns (None uses the    |                              |
    |                                   | sprox default names.                       |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+

    Modifiers inherited from :class:`sprox.viewbase.ViewBase`

    +-----------------------------------+--------------------------------------------+------------------------------+
    | Name                              | Description                                | Default                      |
    +===================================+============================================+==============================+
    | __field_widgets__                 | A dictionary of widgets to replace the     | {}                           |
    |                                   | ones that would be chosen by the selector  |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __field_widget_types__            | A dictionary of types of widgets, allowing | {}                           |
    |                                   | sprox to determine the widget args         |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+
    | __widget_selector__               | an instantiated object to use for widget   | None                         |
    |                                   | selection.                                 |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+

    Modifiers inherited from :class:`sprox.configbase.ConfigBase`


    :Example Usage:

    One of the more useful things sprox does for you is to fill in the arguments to a drop down automatically.
    Here is the userform, limited to just the town field, which gets populated with the towns.

    >>> from sprox.test.base import User, setup_database, setup_records
    >>> session, engine, metadata = setup_database()
    >>> user = setup_records(session)
    >>> class TownForm(FormBase):
    ...    __model__ = User
    ...    __limit_fields__ = ['town']
    >>>
    >>> town_form = TownForm(session)
    >>>
    >>> print town_form()
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="post" class="required tableform">
        <div>
                <input type="hidden" name="sprox_id" class="hiddenfield" id="sprox_id" value="" />
        </div>
        <table border="0" cellspacing="0" cellpadding="2">
            <tr id="town.container" class="even">
                <td class="labelcol">
                    <label id="town.label" for="town" class="fieldlabel">Town</label>
                </td>
                <td class="fieldcol">
                    <select name="town" class="propertysingleselectfield" id="town">
            <option value="1">Arvada</option><option value="2">Denver</option><option value="3">Golden</option><option value="4">Boulder</option><option value="" selected="selected">-----------</option>
    </select>
                </td>
            </tr><tr id="submit.container" class="odd">
                <td class="labelcol">
                </td>
                <td class="fieldcol">
                    <input type="submit" class="submitbutton" value="Submit" />
                </td>
            </tr>
        </table>
    </form>

    Forms created with sprox can be validated as you would any other widget.

    >>> town_form.validate(params={'town':1})
    Traceback (most recent call last):
    ...
    Invalid: sprox_id: Missing value


    >>> session.rollback()
    """
    __require_fields__     = None
    __check_if_unique__    = False

    #object overrides
    __base_widget_type__       = TableForm

    __widget_selector_type__   = SAWidgetSelector

    __validator_selector__      = None
    __validator_selector_type__ = SAValidatorSelector

    __field_validators__       = None
    __field_validator_types__  = None
    __base_validator__         = None

    __metadata_type__ = FieldsMetadata

    __dropdown_view_names__      = None

    def _do_init_attrs(self):
        super(FormBase, self)._do_init_attrs()
        if self.__require_fields__ is None:
            self.__require_fields__ = []
        if self.__field_validators__ is None:
            self.__field_validators__ = {}
        if self.__validator_selector__ is None:
            self.__validator_selector__ = self.__validator_selector_type__(self.__provider__)
        if self.__field_validator_types__ is None:
            self.__field_validator_types__ = {}

    def validate(self, params):
        """A pass-thru to the widget's validate function."""
        return self.__widget__.validate(params)

    def _do_get_widget_args(self):
        """Override this method to define how the class get's the
           arguments for the main widget
        """
        d = super(FormBase, self)._do_get_widget_args()
        if self.__base_validator__ is not None:
            d['validator'] = self.__base_validator__
        return d

    def _do_get_field_widget_args(self, field_name, field):
        """Override this method do define how this class gets the field
        widget arguemnts
        """
        args = super(FormBase, self)._do_get_field_widget_args( field_name, field)
        v = self.__field_validators__.get(field_name, self._do_get_field_validator(field_name, field))
        if self.__provider__.is_relation(self.__entity__, field_name):
            args['entity'] = self.__entity__
            args['field_name'] = field_name
        if v:
            args['validator'] = v
        return args

    def _do_get_fields(self):
        """Override this function to define how
        """
        fields = super(FormBase, self)._do_get_fields()
        if 'sprox_id' not in fields:
            fields.append('sprox_id')
        return fields

    def _do_get_field_widgets(self, fields):
        widgets = super(FormBase, self)._do_get_field_widgets(fields)
        widgets['sprox_id'] = HiddenField('sprox_id')
        return widgets

    def _do_get_field_validator(self, field_name, field):
        """Override thius function to define how a field validator is chosen for a given field.
        """
        v_type = self.__field_validator_types__.get(field_name, self.__validator_selector__[field])
        if field_name in self.__require_fields__ and v_type is None:
            v_type = String
        if v_type is None:
            return
        args = self._do_get_validator_args(field_name, field, v_type)
        v = v_type(**args)
        if hasattr(field, 'unique') and field.unique and self.__check_if_unique__:
            v = All(UniqueValue(self.__provider__, self.__entity__, field_name), v)
        return v

    def _do_get_validator_args(self, field_name, field, validator_type):
        """Override this function to define how to get the validator arguments for the field's validator.
        """
        args = {}
        args['not_empty'] = (not self.__provider__.is_nullable(self.__entity__, field_name)) or \
                             field_name in self.__require_fields__

        if hasattr(field, 'type') and hasattr(field.type, 'length') and\
           issubclass(validator_type, String):
            args['max'] = field.type.length

        return args

class EditableForm(FormBase):
    """A form for editing a record.
    :Modifiers:

    see :class:`sprox.formvase.FormBase`

    """
    def _do_get_disabled_fields(self):
        fields = self.__disable_fields__[:]
        fields.append(self.__provider__.get_primary_field(self.__entity__))
        return fields

class AddRecordForm(EditableForm):
    """An editable form who's purpose is record addition.

    :Modifiers:

    see :class:`sprox.formbase.FormBase`

    +-----------------------------------+--------------------------------------------+------------------------------+
    | Name                              | Description                                | Default                      |
    +===================================+============================================+==============================+
    | __check_if_unique__               | Set this to True for "new" forms.  This    | True                         |
    |                                   | causes Sprox to check if there is an       |                              |
    |                                   | existing record in the database which      |                              |
    |                                   | matches the field data.                    |                              |
    +-----------------------------------+--------------------------------------------+------------------------------+

    Here is an example registration form, as generated from the vase User model.

    >>> from sprox.test.base import setup_database, setup_records
    >>> from sprox.test.model import User
    >>> from sprox.formbase import AddRecordForm
    >>> from formencode import Schema
    >>> from formencode.validators import FieldsMatch
    >>> from tw.forms import PasswordField, TextField
    >>> form_validator =  Schema(chained_validators=(FieldsMatch('password',
    ...                                                         'verify_password',
    ...                                                         messages={'invalidNoMatch':
    ...                                                         'Passwords do not match'}),))
    >>> class RegistrationForm(AddRecordForm):
    ...     __model__ = User
    ...     __require_fields__     = ['password', 'user_name', 'email_address']
    ...     __omit_fields__        = ['_password', 'groups', 'created', 'user_id', 'town']
    ...     __field_order__        = ['user_name', 'email_address', 'display_name', 'password', 'verify_password']
    ...     __base_validator__     = form_validator
    ...     email_address          = TextField
    ...     display_name           = TextField
    ...     verify_password        = PasswordField('verify_password')
    >>> registration_form = RegistrationForm()
    >>> print registration_form()
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="post" class="required tableform">
        <div>
                <input type="hidden" name="sprox_id" class="hiddenfield" id="sprox_id" value="" />
        </div>
        <table border="0" cellspacing="0" cellpadding="2">
            <tr id="user_name.container" class="even">
                <td class="labelcol">
                    <label id="user_name.label" for="user_name" class="fieldlabel required">User Name</label>
                </td>
                <td class="fieldcol">
                    <input type="text" name="user_name" class="textfield required" id="user_name" value="" />
                </td>
            </tr><tr id="email_address.container" class="odd">
                <td class="labelcol">
                    <label id="email_address.label" for="email_address" class="fieldlabel required">Email Address</label>
                </td>
                <td class="fieldcol">
                    <input type="text" name="email_address" class="textfield required" id="email_address" value="" />
                </td>
            </tr><tr id="display_name.container" class="even">
                <td class="labelcol">
                    <label id="display_name.label" for="display_name" class="fieldlabel">Display Name</label>
                </td>
                <td class="fieldcol">
                    <input type="text" name="display_name" class="textfield" id="display_name" value="" />
                </td>
            </tr><tr id="password.container" class="odd">
                <td class="labelcol">
                    <label id="password.label" for="password" class="fieldlabel required">Password</label>
                </td>
                <td class="fieldcol">
                    <input type="password" name="password" class="required passwordfield" id="password" value="" />
                </td>
            </tr><tr id="verify_password.container" class="even">
                <td class="labelcol">
                    <label id="verify_password.label" for="verify_password" class="fieldlabel">Verify Password</label>
                </td>
                <td class="fieldcol">
                    <input type="password" name="verify_password" class="passwordfield" id="verify_password" value="" />
                </td>
            </tr><tr id="town_id.container" class="odd">
                <td class="labelcol">
                    <label id="town_id.label" for="town_id" class="fieldlabel">Town Id</label>
                </td>
                <td class="fieldcol">
                    <input type="text" name="town_id" class="textfield" id="town_id" value="" />
                </td>
            </tr><tr id="submit.container" class="even">
                <td class="labelcol">
                </td>
                <td class="fieldcol">
                    <input type="submit" class="submitbutton" value="Submit" />
                </td>
            </tr>
        </table>
    </form>

    What is unique about the AddRecord form, is that if the fields in the database are labeled unique, it will
    automatically vaidate against uniqueness for that field.  Here is a simple user form definition, where the
    user_name in the model is unique:

    >>> session, engine, metadata = setup_database()
    >>> user = setup_records(session)
    >>> class AddUserForm(AddRecordForm):
    ...     __entity__ = User
    ...     __limit_fields__ = ['user_name']
    >>> user_form = AddUserForm(session)
    >>> user_form.validate(params={'sprox_id':'asdf', 'user_name':u'asdf'}) # doctest: +SKIP
    Traceback (most recent call last):
    ...
    Invalid: user_name: That value already exists

    The validation fails because there is already a user with the user_name 'asdf' in the database

    >>> session.rollback()
    """
    __check_if_unique__ = True

class DisabledForm(FormBase):
    """A form who's set of fields is disabled.


    :Modifiers:

    see :class:`sprox.formbase.FormBase`

    Here is an example disabled form with only the user_name and email fields.

    >>> from sprox.test.model import User
    >>> from sprox.formbase import DisabledForm
    >>> class DisabledUserForm(DisabledForm):
    ...     __model__ = User
    ...     __limit_fields__ = ['user_name', 'email_address']
    >>> disabled_user_form = DisabledUserForm()
    >>> print disabled_user_form(values=dict(user_name='percious', email='chris@percious.com'))
    <form xmlns="http://www.w3.org/1999/xhtml" action="" method="post" class="required tableform">
        <div>
                <input type="hidden" name="user_name" class="hiddenfield" id="user_name" value="" />
                <input type="hidden" name="email_address" class="hiddenfield" id="email_address" value="" />
                <input type="hidden" name="sprox_id" class="hiddenfield" id="sprox_id" value="" />
        </div>
        <table border="0" cellspacing="0" cellpadding="2">
            <tr id="user_name.container" class="even">
                <td class="labelcol">
                    <label id="user_name.label" for="user_name" class="fieldlabel">User Name</label>
                </td>
                <td class="fieldcol">
                    <input type="text" name="user_name" class="textfield" id="user_name" value="" disabled="disabled" />
                </td>
            </tr><tr id="email_address.container" class="odd">
                <td class="labelcol">
                    <label id="email_address.label" for="email_address" class="fieldlabel">Email Address</label>
                </td>
                <td class="fieldcol">
                    <textarea id="email_address" name="email_address" class="textarea" disabled="disabled" rows="7" cols="50"></textarea>
                </td>
            </tr><tr id="submit.container" class="even">
                <td class="labelcol">
                </td>
                <td class="fieldcol">
                    <input type="submit" class="submitbutton" value="Submit" />
                </td>
            </tr>
        </table>
    </form>

    You may notice in the above example that disabled fields pass in a hidden value for each disabled field.

    """


    def _do_get_disabled_fields(self):
        return self.__fields__
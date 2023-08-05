# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: decorators.py 78 2008-01-04 20:11:18Z s0undt3ch $
# =============================================================================
#             $URL: http://pastie.ufsoft.org/svn/sandbox/PylonsGenshi/trunk/pylonsgenshi/decorators.py $
# $LastChangedDate: 2008-01-04 20:11:18 +0000 (Fri, 04 Jan 2008) $
#             $Rev: 78 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================
"""
Genshi related decorators ported from pylons.
"""
import os
import pylons
from paste.util.multidict import UnicodeMultiDict
import formencode
import formencode.variabledecode as variabledecode
from decorator import decorator
from pylons.decorators import determine_response_charset
from genshi.filters.html import HTMLFormFiller
from genshi.template.loader import TemplateLoader
import logging

log = logging.getLogger(__name__)

__docformat__ = 'restructuredtext en'

def validate(template=None, schema=None, validators=None, form=None,
             variable_decode=False, dict_char='.', list_char='-', state=None,
             post_only=True, on_get=False):
    """Validate input either for a FormEncode schema, or individual validators

    Given a form schema or dict of validators, validate will attempt to
    validate the schema or validator list.

    If validation was successful, the valid result dict will be saved
    as ``self.form_result``. Otherwise, the action will be re-run as if it was
    a GET, and the output will be filled by FormEncode's htmlfill to fill in
    the form field errors.

    ``template``
        Refers to the Genshi template to use in case errors need to be shown.
    ``schema``
        Refers to a FormEncode Schema object to use during validation.
    ``form``
        Method used to display the form, which will be used to get the
        HTML representation of the form for error filling.
    ``variable_decode``
        Boolean to indicate whether FormEncode's variable decode function
        should be run on the form input before validation.
    ``dict_char``
        Passed through to FormEncode. Toggles the form field naming
        scheme used to determine what is used to represent a dict. This
        option is only applicable when used with variable_decode=True.
    ``list_char``
        Passed through to FormEncode. Toggles the form field naming
        scheme used to determine what is used to represent a list. This
        option is only applicable when used with variable_decode=True.
    ``post_only``
        Boolean that indicates whether or not GET (query) variables should
        be included during validation.

        .. warning::
            ``post_only`` applies to *where* the arguments to be
            validated come from. It does *not* restrict the form to only
            working with post, merely only checking POST vars.
    ``state``
        Passed through to FormEncode for use in validators that utilize
        a state object.
    ``on_get``
        Whether to validate on GET requests. By default only POST requests
        are validated.

    Example:

    .. code-block:: python

        class SomeController(BaseController):

            def create(self, id):
                return render('myform.html')

            @validate(template='myform.html', schema=model.forms.myshema(),
                      form='create')
            def update(self, id):
                # Do something with self.form_result
                pass
    """
    log.debug('On PylonsGenshi validate decorator')
    def wrapper(func, self, *args, **kwargs):
        """Decorator Wrapper function"""
        request = pylons.request._current_obj()
        errors = {}
         # Skip the validation if on_get is False and its a GET
        if not on_get and request.environ['REQUEST_METHOD'] == 'GET':
            return func(self, *args, **kwargs)

        if post_only:
            params = request.POST
        else:
            params = request.params
        is_unicode_params = isinstance(params, UnicodeMultiDict)
        params = params.mixed()
        if variable_decode:
            log.debug("Running variable_decode on params:")
            decoded = variabledecode.variable_decode(params, dict_char,
                                                     list_char)
            log.debug(decoded)
        else:
            decoded = params

        if schema:
            log.debug("Validating against a schema")
            try:
                self.form_result = schema.to_python(decoded, state)
            except formencode.Invalid, e:
                errors = e.unpack_errors(variable_decode, dict_char, list_char)
        if validators:
            log.debug("Validating against provided validators")
            if isinstance(validators, dict):
                if not hasattr(self, 'form_result'):
                    self.form_result = {}
                for field, validator in validators.iteritems():
                    try:
                        self.form_result[field] = \
                            validator.to_python(decoded.get(field), state)
                    except formencode.Invalid, error:
                        errors[field] = error
        if errors:
            log.debug("Errors found in validation, parsing form with htmlfill "
                      "for errors")
            request.environ['REQUEST_METHOD'] = 'GET'
            pylons.c.form_errors = errors

            # If there's no form supplied, just continue with the current
            # function call.
            if not form:
                raise Exception('You MUST pass a form to display errors')
                return func(self, *args, **kwargs)

            request.environ['pylons.routes_dict']['action'] = form
            response = self._dispatch_call()

            log.debug(errors)
            pylons.c.errors = errors
            engine_dict = pylons.buffet._update_names({})
            loader = TemplateLoader(pylons.config['pylons.paths']['templates'])
            tpl = loader.load(template.replace('.', os.sep)+'.html')
            stream = tpl.generate(**engine_dict) | HTMLFormFiller(data=decoded)

            return  stream.render()
        return func(self, *args, **kwargs)
    return decorator(wrapper)

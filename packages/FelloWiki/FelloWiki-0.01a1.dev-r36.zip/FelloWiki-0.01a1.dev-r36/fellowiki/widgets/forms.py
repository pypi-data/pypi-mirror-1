# Copyright (c) 2006 Jan Niklas Fingerle
# 
# This source code file is based on the TurboGears project's code.
# The TurboGears framework is copyrighted (c) 2005, 2006 by Kevin Dangoor 
# and contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import turbogears.widgets as w

class SubmitPreviewForm(w.Form):
    name = 'submit_preview_form'
    member_widgets = ['preview', 'reset']
    params = ['preview_text', 'reset_text']
    params_doc = {'preview_text': 'Text for the preview button',
                  'reset_text': 'Text for the reset button'}
    preview = w.SubmitButton(name='preview')
    reset = w.ResetButton()
    
    
class SubmitPreviewTableForm(SubmitPreviewForm):
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
        <table border="0" cellspacing="0" cellpadding="2" py:attrs="table_attrs">
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
                <td>${submit.display(submit_text)} ${preview.display(preview_text)} ${reset.display(reset_text)}</td>
            </tr>
        </table>
    </form>
    """
    params = ["table_attrs"]
    params_doc = {'table_attrs' : 'Extra (X)HTML attributes for the Table tag'}
    table_attrs = {}

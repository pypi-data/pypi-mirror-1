<%doc>
/sale/edit.mako - Custom Sale Edit Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/transaction/edit_base.mako"/>

<h1>${c.title}</h1>

<form name="editForm" action="save" method="">

${self.show_children()}

% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>
% for col in c.columns:
    % if col != 'id' and col != 'created' and col != 'type':
    <dt>${col}</dt>
    <dd>
    <%
        input = self.show_div_field(col)
    %>
    ${input}
    </dd>
    % endif
% endfor

</dl>

${self.show_properties()}

<input type="submit" value="Save" />

</form>



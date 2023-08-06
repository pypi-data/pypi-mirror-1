<%doc>
edit.mako - Template for PyCRUD application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17


Copyright (C) 2008 Emanuel Calso <egcalso [at] gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

</%doc>
<%inherit file="/edit_base.mako"/>

<h1>${c.title}</h1>
<%
%>

<form name="editForm" action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>

%if c.session_user.role == 1:
    <%
        col = 'owner'
    %>
    <dt>${col}</dt>
    <dd>
    ${self.show_field(col)}
    </dd>
%endif

<%
    col = 'name'
%>
<dt>
${col}
</dt>
<dd>
${self.show_field(col)}
<small>(Can only contain letters, numbers and "_")</small>
</dd>

<%
    col = 'type'
%>
<dt>Type</dt>
<dd>
<%
value = getattr(c.entry, col)
%>
<select name="type">
%for app_type in ('static', 'symlink', 'subversion', 'webdav'):
    <option>${app_type}</option>
%endfor
</select>
</dd>

<%
    col = 'extra_info'
%>
<dt>Extra Info</dt>
<dd>
${self.show_field(col)}
</dd>

${self.show_properties()}

${self.show_children()}

</dl>

<input type="submit" value="Save" />

</form>



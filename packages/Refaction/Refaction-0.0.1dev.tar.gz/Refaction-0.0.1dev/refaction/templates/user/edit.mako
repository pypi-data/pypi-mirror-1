<%doc>
edit.mako - Template for Refaction application

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

<%
%>

<h1>User</h1>

<form name="editForm" action="submit" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>

<% col = 'name' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'password' %>
<dt>${col}</dt>
<dd>
<input type="password" name="password" />
</dd>
<dt>Confirm ${col}</dt>
<dd>
<input type="password" name="password2" />
</dd>

<% col = 'role' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'email_address' %>
<dt>Email Address</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'details' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

</dl>

<input type="submit" value="Submit" />

</form>



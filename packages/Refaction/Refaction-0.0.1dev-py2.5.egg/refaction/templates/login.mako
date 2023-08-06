<%doc>
login.mako - Login Template for Refaction application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-09-14
    2008-09-16


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
<%inherit file="base.mako"/>

<%
%>

<div>
<h1>Login</h1>

% if c.msg:
    <span>
    ${c.msg}
    </span>
% endif
<form method="post">
<dl>
<dt>Username:</dt>
<dd><input id="user" name="user" /></dd>
<dt>Password:</dt>
<dd><input id="password" name="password" type="password" /></dd>
</dl>
<input type="submit" name="action" value="Login" />
</form>
<div>


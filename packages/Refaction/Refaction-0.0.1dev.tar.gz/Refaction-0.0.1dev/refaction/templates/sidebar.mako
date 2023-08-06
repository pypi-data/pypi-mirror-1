<%doc>
sidebar.mako

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

<%
try:
    name = c.session_user.name
except AttributeError:
    name = None
try:
    role = c.session_user.role
except AttributeError:
    role = 0
%>

<div id="title">
    <h1><a href="/" name="Home">Refaction</a></h1>
</div>

<div id="topBar">
    % if name is not None:
        <div><a href="/logout">Logout</a></li></div>
        <div><a href="#">Welcome ${name}</a></div>
    % else:
        <div><a href="/login">Login</a></div>
    % endif
</div>

<div id="menu">

    %if role > 0:
    <div>
    <ul>
    <li class="menuTop"><strong>Websites</strong></li>
    <li><a href="/app/">Applications</a></li>
    <li><a href="/domain/">Domains</a></li>
    <li><a href="/website/">Websites</a></li>
    </ul>
    </div>
    %endif

    %if role == 1:
    <div>
    <ul>
    <li class="menuTop"><strong>Domains</strong></li>
    <li><a href="/dns/">DNS Override</a></li>
    <li><a href="/domain/">Domains</a></li>
    </ul>
    </div>
    %endif

    %if role == 1:
    <div>
    <ul>
    <li class="menuTop"><strong>Others</strong></li>
    <li><a href="/cron/">Cron Jobs</a></li>
    <li><a href="/db/">Databases</a></li>
    <li><a href="/email/">Emails</a></li>
    <li><a href="/mailbox/">Mail Boxes</a></li>
    </ul>
    </div>
    %endif

    %if role == 1:
    <div>
    <ul>
    <li class="menuTop"><strong>Admin</strong></li>
    <li><a href="/users/">Users</a></li>
    <li>
    Session: ${getattr(c.session, 'id', None)}
    </li>
    <li>
    Session User: ${getattr(c.session_user, 'name', None)}
    </li>
    <li>
    Session Role: ${getattr(c.session_user, 'role', None)}
    </li>
    </ul>
    </div>
    %endif

</div>


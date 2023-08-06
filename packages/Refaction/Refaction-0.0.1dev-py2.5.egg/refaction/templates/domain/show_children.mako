<%doc>

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
child = c.child
parent = c.parent
child_cnt = 0
try:
    child_label = c.child_details['label']
except KeyError:
    child_label = child
%>

<%def name="get_value(entry, col)">
    <%
    if 'parent' in c.child_details and col in c.child_details['parent']:
        parent = c.child_details['parent'][col]
        parent_col = parent['column']
        parent_tbl = parent['table']
        parent_id = getattr(entry, col)
        parent_entry = parent_tbl.get(parent_id)
        try:
            value = getattr(parent_entry, parent_col)
        except AttributeError:
            value = ''
    else:
        value = getattr(entry, col)
    %>
    ${value}
</%def>

<h3>${child_label}</h3>
<table>
<thead>
<tr>
%for column in c.child_details['columns']:
    <th>
    ${column}
    </th>
%endfor
</tr>
</thead>
<tbody>
%for entry in c.children:
<%
child_cnt += 1
%>
<tr id="old-${child}-${child_cnt}">
%   for column in c.child_details['columns']:
    <td>
    %if entry.name == '':
        ${c.parent.name}
    %else:
        ${self.get_value(entry, column)}.${c.parent.name}
    %endif
    </td>
%   endfor
<td>
%if entry.name != '':
    <a href="#${child}" onclick="edit_child_${child}(${child_cnt}, ${entry.id}, ${c.parent.id});">edit</a>
%endif
</td>
</tr>
%endfor

<!-- Add default subdomains -->
%if child_cnt == 0:
    <tr id="new-${child}-00">
        <td>
            <input name="subdomain.name" value="" readonly="readonly" />
        </td>
        <td>
        </td>
    </tr>
    <tr id="new-${child}-0">
        <td>
            <input name="subdomain.name" value="www" readonly="readonly" />
        </td>
        <td>
        </td>
    </tr>
%endif

%for cnt in range(1, 1+50):
    <tr id="new-${child}-${cnt}"></tr>
%endfor
</tbody>
</table>
<a href="#${child}" onclick="add_child_${child}();">add</a>
<a name="${child}">&nbsp;</a>


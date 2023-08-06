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

<%inherit file="/edit_child_base.mako"/>

<%
%>

<%def name="show_subdomain(col)">
    <%
    from refaction import model
    try:
        v_id = getattr(c.entry, col)
    except AttributeError:
        v_id = None
    v_id = getattr(c.entry, col)
    try:
        parent = c.child_details['parent'][col]
    except KeyError:
        raise KeyError('The column %s should be defined as a parent.' % (col))
    try:
        p_table = parent['table']
    except KeyError:
        raise KeyError('The table for the parent %s should be specified.' % (col))
    try:
        p_column = parent['column']
    except KeyError:
        raise KeyError('The column for the parent %s should be specified.' % (col))
    p_entries = p_table.list()
    domains = {}
    for domain in model.Domain.list():
        domains[domain.id] = domain.name
    %>
    <select name="${c.child}.${col}">
    %if getattr(c.table.c, col).nullable:
        <option value=""></option>
    %endif
    %for entry in p_entries:
        <%
        if entry.domain is None:
            continue
        value = getattr(entry, p_column)
        domain = domains[int(entry.domain)]
        if value == '':
            value = domain
        else:
            value = '%s.%s' % (value, domain)
        %>
        %if entry.id == v_id:
            <option value="${entry.id}" selected="selected">
                ${value}
            </option>
        %else:
            <option value="${entry.id}">
                ${value}
            </option>
        %endif
    %endfor
    </select>
</%def>


<input type="hidden" name="${c.child}-id" value="${c.entry.id}" />
% for col in c.columns:
    % if col == 'subdomain':
    <td>
    <%
        input = self.show_subdomain(col)
    %>
    ${input}
    </td>
    % elif col not in ('id', 'subdomain'):
    <td>
    <%
        input = self.show_field(col)
    %>
    ${input}
    </td>
    % endif
% endfor
<td class="child-remove-link">
${h.link_to_remote('remove',
        dict(update='old-'+c.child+'-'+c.cnt, url=h.url_for(
            action='rem_child',
            id=c.entry.id,
            child=c.child,
            p_id=c.p_id,
        ))
    )}
</td>


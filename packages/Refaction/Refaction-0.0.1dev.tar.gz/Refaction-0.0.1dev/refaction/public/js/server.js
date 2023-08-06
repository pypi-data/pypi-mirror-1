/*
 *
 * Copyright (C) 2008 Emanuel Calso <egcalso [at] gmail.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 */

function showRestart(id) {
    new Ajax.Updater(
            id,
            '/admin/show_restart',
            {asynchronous:true, evalScripts:true}
        );
}

function startReceiver() {
    showRestart('receiverStatus');
    new Ajax.Updater(
            'receiverStatus',
            '/admin/start_receiver',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

function startSender() {
    showRestart('senderStatus');
    new Ajax.Updater(
            'senderStatus',
            '/admin/start_sender',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

function showStatus() {
    window.location.reload(true);
    return false;
}

function showStatusSender() {
    new Ajax.Updater(
            'senderStatus',
            '/admin/show_status_sender',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}

function showStatusReceiver() {
    new Ajax.Updater(
            'receiverStatus',
            '/admin/show_status_receiver',
            {asynchronous:true, evalScripts:true}
        );
    return false;
}


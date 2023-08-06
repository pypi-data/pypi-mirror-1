/*****************************************************************************
 *
 * Copyright (c) InQuant GmbH
 *
 * This software is distributed under the terms of the GPL License.
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 *****************************************************************************/

function initCustomTools(editorId) {
    var prefix = '#'+editorId+' ';

    var opendrawer = function(drawerid) {
        return function(button, editor) {
            drawertool.openDrawer(prefix+drawerid);
        };
    };

    /* EMOTICON TOOL */
    var emoticontool = new EmoticonTool()
    kupu.registerTool('emoticontool', emoticontool);

    /* EMOTICON DRAWER BUTTON */
    var emoticondrawerbutton = new KupuButton(prefix+'button.kupu-emoticons',
                                              opendrawer('emoticondrawer'));
    kupu.registerTool('emoticondrawerbutton', emoticondrawerbutton);

    /* EMOTICON DRAWER */
    var emoticondrawer = new EmoticonDrawer(prefix+'div.kupu-emoticondrawer', emoticontool);
    drawertool.registerDrawer(prefix+'emoticondrawer', emoticondrawer, kupu);
}

/* vim: set ft=javascript ts=4 sw=4 expandtab : */

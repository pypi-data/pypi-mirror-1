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

function EmoticonTool(smilebutton, sadbutton, winkbutton, lolbutton, coolbutton) {
    /* tool to set emoticons */

    this.smilebutton = getFromSelector(smilebutton);
    this.sadbutton = getFromSelector(sadbutton);
    this.winkbutton = getFromSelector(winkbutton);
    this.lolbutton = getFromSelector(lolbutton);
    this.coolbutton = getFromSelector(coolbutton);
};

EmoticonTool.prototype = new KupuTool;


EmoticonTool.prototype.initialize = function(editor) {
    /* attach event handlers */
    this.editor = editor;

    if (this.smilebutton) {
        //alert('add Event')
        addEventHandler(this.smilebutton, "click", this.addSmileEmoticon, this);
    }
    if (this.sadbutton) {
        addEventHandler(this.sadbutton, "click", this.addSadEmoticon, this);
    }
    if (this.winkbutton) {
        addEventHandler(this.winkbutton, "click", this.addWinkEmoticon, this);
    }
    if (this.lolbutton) {
        addEventHandler(this.lolbutton, "click", this.addLolEmoticon, this);
    }
    if (this.coolbutton) {
        addEventHandler(this.coolbutton, "click", this.addCoolEmoticon, this);
    }
};

EmoticonTool.prototype.addSmileEmoticon = function() {
    /* add :-) */
    this.addEmoticon(":-)");
};

EmoticonTool.prototype.addSadEmoticon = function() {
    /* add :-( */
    this.addEmoticon(":-(");
};

EmoticonTool.prototype.addWinkEmoticon = function() {
    /* add ;-) */
    this.addEmoticon(";-)");
};

EmoticonTool.prototype.addLolEmoticon = function() {
    /* add :-D */
    this.addEmoticon(":-D");
};

EmoticonTool.prototype.addCoolEmoticon = function() {
    /* add 8-) */
    this.addEmoticon("8-)");
};

EmoticonTool.prototype.addEmoticon = function(emoticon) {
    //alert(emoticon)
    var kupu = this.editor;
    var doc = kupu.getInnerDocument();

    var span = doc.createElement('span');
    var text = doc.createTextNode(emoticon)
    span.appendChild(text)
    kupu.insertNodeAtSelection(span, 1)
};

/* vim: set ft=javascript ts=4 sw=4 expandtab : */

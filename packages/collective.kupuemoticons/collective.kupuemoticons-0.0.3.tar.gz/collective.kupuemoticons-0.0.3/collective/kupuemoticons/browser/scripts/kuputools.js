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

/* The tools inserts the smiley to the iframe */
function EmoticonTool() {
    /* Add Emoticons */
    this.initialize = function(editor) {
        this.editor = editor;
    }
    this.addEmoticon = function(src, alt, title) {
        var kupu = this.editor;
        var doc = kupu.getInnerDocument();
        var img = doc.createElement('img');
        img.setAttribute('src', src);
        img.setAttribute('alt', alt);
        img.setAttribute('title', title);
        kupu.insertNodeAtSelection(img, 1);
    };
    this.addSmileEmoticon = function() {
        this.addEmoticon('smiley_smile.gif', ':-)', 'Smile');
        this.editor.focusDocument();
    };
    this.addSadEmoticon = function() {
        this.addEmoticon('smiley_sad.gif', ':-(', 'Sad');
        this.editor.focusDocument();
    };
    this.addAngryEmoticon = function() {
        this.addEmoticon('smiley_angry.gif', ':-@', 'Angry');
        this.editor.focusDocument();
    };
    this.addBoredEmoticon = function() {
        this.addEmoticon('smiley_bored.gif', ':-|', 'Bored');
        this.editor.focusDocument();
    };
    this.addCoolEmoticon = function() {
        this.addEmoticon('smiley_cool.gif', '8-)', 'Cool');
        this.editor.focusDocument();
    };
    this.addCuriousEmoticon = function() {
        this.addEmoticon('smiley_curious.gif', ':-/', 'Curious');
        this.editor.focusDocument();
    };
    this.addDeadEmoticon = function() {
        this.addEmoticon('smiley_dead.gif', 'X-|', 'Dead');
        this.editor.focusDocument();
    };
    this.addDohEmoticon = function() {
        this.addEmoticon('smiley_doh.gif', ':-O', 'Doh');
        this.editor.focusDocument();
    };
    this.addGrinEmoticon = function() {
        this.addEmoticon('smiley_grin.gif', ':-D', 'Grin');
        this.editor.focusDocument();
    };
    this.addJoshEmoticon = function() {
        this.addEmoticon('smiley_josh.gif', ':-P', 'Josh');
        this.editor.focusDocument();
    };
    this.addKissEmoticon = function() {
        this.addEmoticon('smiley_kiss.gif', ':-*', 'Kiss');
        this.editor.focusDocument();
    };
    this.addLolEmoticon = function() {
        this.addEmoticon('smiley_lol.gif', '=)', 'LOL');
        this.editor.focusDocument();
    };
    this.addNodEmoticon = function() {
        this.addEmoticon('smiley_nod.gif', '(nod)', 'Nod');
        this.editor.focusDocument();
    };
    this.addNopeEmoticon = function() {
        this.addEmoticon('smiley_nope.gif', '(nope)', 'Nope');
        this.editor.focusDocument();
    };
    this.addPfuiEmoticon = function() {
        this.addEmoticon('smiley_pfui.gif', '(pfui)', 'Pfui');
        this.editor.focusDocument();
    };
    this.addWaveEmoticon = function() {
        this.addEmoticon('smiley_wave.gif', '(wave)', 'Wave');
        this.editor.focusDocument();
    };
    this.addWeepEmoticon = function() {
        this.addEmoticon('smiley_weep.gif', ';-(', 'Weep');
        this.editor.focusDocument();
    };
    this.addWinkEmoticon = function() {
        this.addEmoticon('smiley_wink.gif', ';-)', 'Wink');
        this.editor.focusDocument();
    };
};
EmoticonTool.prototype = new KupuTool;


function EmoticonDrawer(elementid, tool) {
    /* Table drawer */
    this.element = getFromSelector(elementid);
    this.tool = tool;

    this.createContent = function() {
        this.element.style.display = 'block';
        this.focusElement();
    };
    this.addSmileEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addSmileEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addSadEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addSadEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addAngryEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addAngryEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addBoredEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addBoredEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addCoolEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addCoolEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addCuriousEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addCuriousEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addDeadEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addDeadEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addDohEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addDohEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addGrinEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addGrinEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addJoshEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addJoshEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addKissEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addKissEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addLolEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addLolEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addNodEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addNodEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addNopeEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addNopeEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addPfuiEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addPfuiEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addWaveEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addWaveEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addWeepEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addWeepEmoticon();
        this.drawertool.closeDrawer();
    };
    this.addWinkEmoticon = function() {
        this.editor.resumeEditing();
        this.tool.addWinkEmoticon();
        this.drawertool.closeDrawer();
    };
};
EmoticonDrawer.prototype = new Drawer;

/* vim: set ft=javascript ts=4 sw=4 expandtab : */

/*
File: kupumashups_tools.js

Copyright (c) Matias Bordese

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

// MASHUP_LINK_PREFIX = 'ref';
// MASHUP_POPUP_PREFIX = 'popup';

function MashupTool() {
    this.linkclass = 'mashup-link';

    this.initialize = function(editor) {
        this.editor = editor;
    };

    /* If editing a previous link, update it and its popup */
    this.checkLinkAround = function(textvalue, terms) {
        var currnode = this.editor.getSelectedNode();

        // selection inside link
        var linkel = this.editor.getNearestParentOfType(currnode, 'A');
        if (linkel) {
            this.updateLink(linkel, textvalue, terms, null);
            return true;
        }

        if (currnode.nodeType!=1) return false;

        // selection contains links
        var linkelements = currnode.getElementsByTagName('A');
        var selection = this.editor.getSelection();
        var containsLink = false;
        for (var i = 0; i < linkelements.length; i++) {
            linkel = linkelements[i];
            if (selection.containsNode(linkel)) {
                this.updateLink(linkel, textvalue, terms, null);
                containsLink = true;
            }
        };
        return containsLink;
    };

    /* Check if editing a previous link and if not create a new one */
    this.createLink = function(textvalue, terms) {
        terms = terms.strip();
        if (!terms) {
            return;
        };
        if (!this.checkLinkAround(textvalue, terms)){
            var doc = this.editor.getInnerDocument();
            var docbody = doc.body;
            var linkel = doc.createElement("a");
            var divel = doc.createElement("div");
            var id = this.generateRandomId();

            divel.setAttribute('class', 'popup');
            divel.setAttribute('id', MASHUP_POPUP_PREFIX + id);
            divel.appendChild(doc.createTextNode(terms));
            doc.body.appendChild(divel);

            this.updateLink(linkel, textvalue, terms, id);
            this.editor.getSelection().replaceWithNode(linkel, true);
        }
    };

    /* Updates the link and popup details */
    this.updateLink = function (linkel, textvalue, terms, id) {
        var doc = this.editor.getInnerDocument();
        linkel.href = '#';
        if (linkel.innerHTML == "") {
            linkel.appendChild(doc.createTextNode(textvalue || terms));
        }
        linkel.className = this.linkclass;
        if (id != null)
            linkel.id = MASHUP_LINK_PREFIX + id;
        else{
            var popup = doc.getElementById(MASHUP_POPUP_PREFIX + linkel.id.substring(MASHUP_LINK_PREFIX.length));
            popup.innerHTML = terms;
        }
    };

    /* Generate a random id to identify link and popup */
    this.generateRandomId = function() {
        var d = new Date()
        var id = (d.getTime() % 100000).toString() + Math.ceil(100000*Math.random());
        return id
    };
}

MashupTool.prototype = new KupuTool;


function GoogleSearchTool() {
    /* Add and update Google Search mashups */
    this.linkclass = 'googlesearch-link';
}

GoogleSearchTool.prototype = new MashupTool;

function WikipediaTool() {
    /* Add and update Wikipedia mashups */
    this.linkclass = 'wikipedia-link';
}

WikipediaTool.prototype = new MashupTool;

function GoogleMapsTool() {
    /* Add and update Google Maps mashups */
    this.linkclass = 'googlemaps-link';
}

GoogleMapsTool.prototype = new MashupTool;


/* Redefine remove to manage the mashups case */
function KupuRemoveElementButton(buttonid, element_name, cssclass) {
    /* A button specialized in removing elements in the current node
       context. Typical usages include removing links, images, etc. */
    this.button = getFromSelector(buttonid);
    this.onclass = 'invisible';
    this.offclass = cssclass;
    this.pressed = false;

    this.commandfunc = function(button, editor) {
        editor.focusDocument();
        this.removePopUp(editor);
        editor.removeNearestParentOfType(editor.getSelectedNode(), element_name);
        editor.updateState();
    };

    this.removePopUp = function(editor) {
        var doc = editor.getInnerDocument();
        var element = editor.getNearestParentOfType(editor.getSelectedNode(), element_name);
        var popup = doc.getElementById(MASHUP_POPUP_PREFIX + element.id.substring(MASHUP_LINK_PREFIX.length));
        if (popup)
            popup.parentNode.removeChild(popup);
    }

    this.checkfunc = function(currnode, button, editor, event) {
        var element = editor.getNearestParentOfType(currnode, element_name);
        return (element ? false : true);
    };
};

KupuRemoveElementButton.prototype = new KupuStateButton;
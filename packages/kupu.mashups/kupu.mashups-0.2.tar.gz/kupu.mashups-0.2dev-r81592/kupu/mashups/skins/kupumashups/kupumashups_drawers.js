/*
File: kupumashups_drawers.js

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

function GoogleSearchDrawer(elementid, tool) {
    /* Google Search drawer */
    this.element = getFromSelector(elementid);
    this.tool = tool;

    var termsinput = getBaseTagClass(this.element, 'input', 'kupu-gsearchdrawer-terms');

    this.createContent = function() {
        /* Run when displaying the drawer */
        var editor = this.editor;
        var currnode = editor.getSelectedNode();
        var linkel = editor.getNearestParentOfType(currnode, 'a');
        var preview = document.getElementById('search_preview');

        if (linkel) {
            var doc = editor.getInnerDocument();
            var popup = doc.getElementById(MASHUP_POPUP_PREFIX + linkel.id.substring(MASHUP_LINK_PREFIX.length));
            termsinput.value = popup.innerHTML;
        } else {
            termsinput.value = editor.getSelection();
        };
        preview.innerHTML = '';
        this.element.style.display = 'block';
        this.focusElement();
    };

    this.preview = function() {
        var gsearch = new google.search.WebSearch();
        var terms = termsinput.value;
        gsearch.setSearchCompleteCallback(this, searchComplete, new Array(gsearch, 'search_preview'));
        gsearch.execute(terms);
    };

    this.save = function() {
        var selected = this.editor.getSelection();
        var terms = termsinput.value;
        this.tool.createLink(selected, terms);
        termsinput.value = '';
        this.drawertool.closeDrawer();
    };
};

GoogleSearchDrawer.prototype = new Drawer;


function WikipediaDrawer(elementid, tool) {
    /* Wikipedia drawer */
    this.element = getFromSelector(elementid);
    this.tool = tool;

    var articleinput = getBaseTagClass(this.element, 'input', 'kupu-wikipediadrawer-article');

    this.createContent = function() {
        /* Run when displaying the drawer */
        var editor = this.editor;
        var currnode = editor.getSelectedNode();
        var linkel = editor.getNearestParentOfType(currnode, 'a');
        var preview = document.getElementById('wikipedia_preview');

        if (linkel) {
            var doc = editor.getInnerDocument();
            var popup = doc.getElementById(MASHUP_POPUP_PREFIX + linkel.id.substring(MASHUP_LINK_PREFIX.length));
            articleinput.value = popup.innerHTML;
        } else {
            articleinput.value = editor.getSelection();
        };
        preview.innerHTML = '';
        this.element.style.display = 'block';
        this.focusElement();
    };

    this.preview = function() {
        var popup = jq('#wikipedia_preview');
        var article = articleinput.value;
        popup.load('wikipediaMashupView', {'title': article});
    };

    this.save = function() {
        var selected = this.editor.getSelection();
        var article = articleinput.value;
        this.tool.createLink(selected, article);
        articleinput.value = '';
        this.drawertool.closeDrawer();
    };
};

WikipediaDrawer.prototype = new Drawer;


function GoogleMapsDrawer(elementid, tool) {
    /* Google Maps drawer */
    this.element = getFromSelector(elementid);
    this.tool = tool;

    var locationinput = getBaseTagClass(this.element, 'input', 'kupu-gmapsdrawer-location');

    this.createContent = function() {
        /* Run when displaying the drawer */
        var editor = this.editor;
        var currnode = editor.getSelectedNode();
        var linkel = editor.getNearestParentOfType(currnode, 'a');
        var preview = document.getElementById('maps_preview');

        if (linkel) {
            var doc = editor.getInnerDocument();
            var popup = doc.getElementById(MASHUP_POPUP_PREFIX + linkel.id.substring(MASHUP_LINK_PREFIX.length));
            locationinput.value = popup.innerHTML;
        } else {
            locationinput.value = editor.getSelection();
        };
        preview.innerHTML = '';
        this.element.style.display = 'block';
        this.focusElement();
    };

    this.preview = function() {
        var map_canvas = document.getElementById('maps_preview');
        var location = locationinput.value;
        var map = new GMap2(map_canvas);
        var geocoder = new GClientGeocoder();
        geocoder.getLatLng(location, function(point) {
                                        if (point) {
                                            map.setCenter(point, 7);
                                            var marker = new GMarker(point);
                                            map.addOverlay(marker);
                                        }
                                    }
        );
        map.addControl(new GSmallZoomControl());
        map.addControl(new GMapTypeControl());
    };

    this.save = function() {
        var selected = this.editor.getSelection();
        var location = locationinput.value;
        this.tool.createLink(selected, location);
        locationinput.value = '';
        this.drawertool.closeDrawer();
    };
};

GoogleMapsDrawer.prototype = new Drawer;

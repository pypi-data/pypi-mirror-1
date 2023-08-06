/*
File: kupumashups_popup.js

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

MASHUP_LINK_PREFIX = 'ref';
MASHUP_POPUP_PREFIX = 'popup';

function addSeparator(x) {
    sep = ',';
    z = '';
    for (i=x.length-1;i>=0;i--)
        z += x.charAt(i);
    // add separators. but undo the trailing one, if there
    z = z.replace(/(\d{3})/g, "$1" + sep);
    if (z.slice(-sep.length) == sep)
        z = z.slice(0, -sep.length);
    x = "";
    // reverse again to get back the number
    for (i=z.length-1;i>=0;i--)
        x += z.charAt(i);
    return x;
}

/* Popups code adapted from http://jqueryfordesigners.com/coda-popup-bubbles/ */
function mashupPopUps() {
        // options
        var distance = 10;
        var time = 250;
        var hideDelay = 500;

        var hideDelayTimer = null;

        // tracker
        var beingShown = false;
        var shown = false;

        var trigger = jq(this);
        var popup = jq('#' + MASHUP_POPUP_PREFIX + this.id.substring(MASHUP_LINK_PREFIX.length)).css('opacity', 0);

        // set the mouseover and mouseout on both element
        jq([trigger.get(0), popup.get(0)]).mouseover(
            function () {
                // stops the hide event if we move from the trigger to the popup element
                if (hideDelayTimer) clearTimeout(hideDelayTimer);

                // don't trigger the animation again if we're being shown, or already visible
                if (beingShown || shown) {
                    return;
                } else {
                    beingShown = true;
                    var pos = jq(trigger).offset();
                    jq(trigger).trigger('dblclick');

                    // reset position of popup box
                    popup.css({
                    top: pos.top + 30,
                    left: pos.left - 20,
                    display: 'block' // brings the popup back in to view
                    })
                    // (we're using chaining on the popup) now animate it's opacity and position
                    .animate({
                        top: '-=' + distance + 'px',
                        opacity: 1
                    }, time, 'swing', function() {
                    // once the animation is complete, set the tracker variables
                    beingShown = false;
                    shown = true;
                    });
                }
            }).mouseout(
            function () {
                // reset the timer if we get fired again - avoids double animations
                if (hideDelayTimer) clearTimeout(hideDelayTimer);

                // store the timer so that it can be cleared in the mouseover if required
                hideDelayTimer = setTimeout(function () {
                    hideDelayTimer = null;
                    popup.animate({
                        top: '-=' + distance + 'px',
                        opacity: 0
                    }, time, 'swing', function () {
                    // once the animate is complete, set the tracker variables
                    shown = false;
                    // hide the popup entirely after the effect (opacity alone doesn't do the job)
                    popup.css({display: 'none'});
                    });
                }, hideDelay);
            });
}


google.load('search', '1');

function mashupGoogleSearchCall(){
        var updated = false;
        var popupId = MASHUP_POPUP_PREFIX + this.id.substring(MASHUP_LINK_PREFIX.length);
        var trigger = jq(this);
        var popup = jq('#' + popupId);
        var query = popup.text();
        popup.html('<img src="loading.gif" alt="Loading...">');

        jq(trigger.get(0)).dblclick(
                function(){
                    if (!updated){
                        var gsearch = new google.search.WebSearch();
                        gsearch.setSearchCompleteCallback(this, searchComplete, new Array(gsearch, popupId));
                        gsearch.execute(query);
                        updated = true;
                    }
                }
        );
}


function searchComplete(gsearch, popupId) {
    // Grab our content div, clear it.
    var contentDiv = document.getElementById(popupId);
    contentDiv.innerHTML = '';

    // Check that we got results
    if (gsearch.results && gsearch.results.length > 0) {
        var results = gsearch.results;
        var title = document.createElement('h2');
        var status = document.createElement('div');
        var footer = document.createElement('div');
        var moreUrl = document.createElement('a');
        title.innerHTML = 'Google Search Results'
        status.innerHTML = addSeparator(gsearch.cursor.estimatedResultCount) + ' results';
        status.className = 'gsearch-status discreet';
        footer.className = 'gsearch-status';
        contentDiv.appendChild(title);
        contentDiv.appendChild(status);

        // Loop through our results, printing them to the page.
        for (var i = 1; i <= results.length; i++) {
            // For each result write it's title and image to the screen
            var result = results[i-1];
            contentDiv.appendChild(result.html);
        }
        moreUrl.innerHTML = 'See all results';
        moreUrl.target = '_blank';
        moreUrl.className = 'link-plain';
        moreUrl.href = gsearch.cursor.moreResultsUrl;
        footer.appendChild(moreUrl);
        contentDiv.appendChild(footer);
    }else{
        contentDiv.innerHTML = 'No results found';
    }
}

google.load('maps', '2');

function mashupGoogleMapsCall(){
        var updated = false;
        var popupId = MASHUP_POPUP_PREFIX + this.id.substring(MASHUP_LINK_PREFIX.length);
        var trigger = jq(this);
        var popup = jq('#' + popupId);
        var address = popup.text();
        popup.html('<img src="loading.gif" alt="Loading...">');

        jq(trigger.get(0)).dblclick(
                function(){
                    if (!updated){
                        var map_canvas = document.createElement('div');
                        var map = new GMap2(map_canvas);
                        var geocoder = new GClientGeocoder();
                        map_canvas.id = 'map_canvas';
                        map_canvas.className = 'map_canvas';
                        popup.empty();
                        popup.append(map_canvas);
                        geocoder.getLatLng(address, function(point) {
                                                        if (point) {
                                                            var center = new GLatLng(point.lat() + 1.5 , point.lng() - 1.5);
                                                            map.setCenter(center, 7);
                                                            var marker = new GMarker(point);
                                                            map.addOverlay(marker);
                                                        }
                                                    }
                        );
                        map.addControl(new GSmallZoomControl());
                        map.addControl(new GMapTypeControl());
                        jq('.map_canvas').click(function(){return false});
                        updated = true;
                    }
                }
        );
}

function mashupWikipediaCall(){
        var updated = false;
        var popupId = MASHUP_POPUP_PREFIX + this.id.substring(MASHUP_LINK_PREFIX.length);
        var trigger = jq(this);
        var popup = jq('#' + popupId);
        var title = popup.text();
        popup.html('<img src="loading.gif" alt="Loading...">');

        jq(trigger.get(0)).dblclick(
                function(){
                    if (!updated){
                        popup.load('wikipediaMashupView', {'title': title});
                        updated = true;
                    }
                }
        );
}


jq(document).ready(

    function () {
        /* Disable onclick for mashup links */
        jq('.googlesearch-link').click(function(){return false});
        jq('.wikipedia-link').click(function(){return false});
        jq('.googlemaps-link').click(function(){return false});

        /* Configure mashup links popups */
        jq('.googlesearch-link').each(mashupPopUps);
        jq('.wikipedia-link').each(mashupPopUps);
        jq('.googlemaps-link').each(mashupPopUps);

        /* Configure mashup calls */
        jq('.googlesearch-link').each(mashupGoogleSearchCall);
        jq('.wikipedia-link').each(mashupWikipediaCall);
        jq('.googlemaps-link').each(mashupGoogleMapsCall);
    }
);

jq(document).unload(
    /* Unload GoogleMaps */
    function () {
        GUnload();
    }
);
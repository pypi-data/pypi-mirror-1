/*
File: kupumashups_init.js

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

function initKupuMashupTools(editorId){
    var prefix = '#'+editorId+' ';

    var opendrawer = function(drawerid) {
        return function(button, editor) {
            drawertool.openDrawer(prefix+drawerid);
        };
    };

    /* Register mashups tools */
    var gsearchtool = new GoogleSearchTool();
    kupu.registerTool('gsearchtool', gsearchtool);

    var gmapstool = new GoogleMapsTool();
    kupu.registerTool('gmapstool', gmapstool);

    var wikipediatool = new WikipediaTool();
    kupu.registerTool('wikipediatool', wikipediatool);

    /* Mashups drawers */
    /* Register button and associate it with its drawer */
    var gsearchdrawerbutton = new KupuButton(prefix+'button.kupu-googlesearch',
                                          opendrawer('gsearchdrawer'));
    kupu.registerTool('gsearchdrawerbutton', gsearchdrawerbutton);

    var wikipediadrawerbutton = new KupuButton(prefix+'button.kupu-wikipedia',
                                          opendrawer('wikipediadrawer'));
    kupu.registerTool('wikipediadrawerbutton', wikipediadrawerbutton);

    var gmapsdrawerbutton = new KupuButton(prefix+'button.kupu-googlemaps',
                                          opendrawer('gmapsdrawer'));
    kupu.registerTool('gmapsdrawerbutton', gmapsdrawerbutton);


    /* Registering mashups drawers */
    /* Now associate the drawer to its html div and its respective tool */
    var gsearchdrawer = new GoogleSearchDrawer(prefix+'div.kupu-gsearchdrawer', gsearchtool);
    drawertool.registerDrawer(prefix+'gsearchdrawer', gsearchdrawer, kupu);

    var wikipediadrawer = new WikipediaDrawer(prefix+'div.kupu-wikipediadrawer', wikipediatool);
    drawertool.registerDrawer(prefix+'wikipediadrawer', wikipediadrawer, kupu);

    var gmapsdrawer = new GoogleMapsDrawer(prefix+'div.kupu-gmapsdrawer', gmapstool);
    drawertool.registerDrawer(prefix+'gmapsdrawer', gmapsdrawer, kupu);

}

/** 
Copyright (C) 2008  Goldmund, Wyldebeast & Wunderliebe

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
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
**/

$=jq;

$(document).ready(function(){

    var is_over_viewlet = 0; //This integer is needed to prevent over effect over column to interfere
	var originatingColumn = "";
    makedummy(); // Rebuild dummy
    $("#hiddenlist").hide();
    $(".mlango-viewlet").not(".nodrag").draggable({
		containment: "#content",
		'helper':'clone', //We use a clone of the viewlet, original is removed and put in hiddenlist, replaced at end
		zIndex:1000, 
		handle:".viewlet-toolbar",
		start: function(e, ui){
			originatingColumn = $(this).parents("div[class*=mlango-dashboard-col]").attr("id");
		    $("#hiddenlist").append($(this));
		    dropped_in_col = false;
	    },
		stop: function(e, ui){
		    if($('#mlango-dummy').parent().attr("id")=="hidden-list"){ //Check if dummy is in hiddenlist
				$('#col_listing').append($(this));    //If so, remove viewlet and put it in listing
		    } else { //If not, replace dummy with actual viewlet
				$('#mlango-dummy').replaceWith($(this));
		    }
		    makedummy(); //Rebuild dummy
		    is_over_viewlet = 0;
		    setTimeout("savePortletSettings('"+ $(this).attr("id") +"', '" + originatingColumn + "');", 5); //Timeout is needed to ensure all draganddrop is done, else some elements are doubled while saving
		}
	}).droppable({
	    accept: ".mlango-viewlet",
	    tolerance: 'pointer',
	    over: function(ev, ui) {
			this_parent_id =  $(this).parent().attr("id")
		    dummy_parent_id = $('#mlango-dummy').parent().attr("id")
		    if($(this).parent().attr("id") == "col_listing"){ return; }; //Don't want over effect for the viewlet-listing on right side
		    is_over_viewlet++; //Viewlet is over another viewlet, column over function will ignore
		    $(this).before( $('#mlango-dummy')); //Put viewlet infront of current viewlet
		    $('#mlango-dummy').show();
	    },
	    out: function(ev, ui) {
		    is_over_viewlet--; //Viewlet is no longer over another viewlet, column over function no longer ignores
		    this_parent_id =  $(this).parent().attr("id");
		    dummy_parent_id = $('#mlango-dummy').parent().attr("id");
			if (this_parent_id == dummy_parent_id) {
 	 	        $(this).parent().append( $('#mlango-dummy'));
		    }
	    }
    });
    $(".mlango-col").droppable({
	    accept: ".mlango-viewlet",  
	    tolerance: 'pointer',
	    activate: function(ev, ui) {
		    $('#mlango-dummy').css("height", $(ui.helper).height());
	    },
	    over: function(ev, ui){
		    if(is_over_viewlet > 0){ return; } //Check if viewlet is over another viewlet, if so ignore.
		    $(this).append( $('#mlango-dummy'));
		    $('#mlango-dummy').show();
	    }
    });
});


/**
 * Create dummy portlet to enable the position marker on the dashboard.
 */
function makedummy(){
    var dummy = document.createElement("li");
    dummy.setAttribute("id", "mlango-dummy");
    $("#hiddenlist").hide();
    $('#hiddenlist').append(dummy);    
}


/**
 * Store settings for a portlet after the stop 'event'.
 */
function savePortletSettings(portlet_id, originatingColumn) {

	var target = $('#' + portlet_id).parents("div.mlango-dashboard-col");
	var target_id = target.attr("id");
	var portlethash = portlet_id.replace("li_", "");

	elts = target.find("li").map(function () {return this.getAttribute("id");}).get();

	var i = elts.indexOf(portlet_id);
	
	// Store result of move on server.
	$.get('mlangoMovePortlet', {'portlethash':portlethash,
		'source_manager':originatingColumn, 'target_manager':target_id, 'position': i});
}

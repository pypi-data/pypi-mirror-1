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
$(document).ready(function(){

    var is_over_viewlet = 0; //This integer is needed to prevent over effect over column to interfere
    makedummy(); // Rebuild dummy
    $("#hiddenlist").hide();
    $(".mlango-viewlet").not(".nodrag").draggable({
	containment: "#content",
	'helper':'clone', //We use a clone of the viewlet, original is removed and put in hiddenlist, replaced at end
	zIndex:1000, 
	handle:".viewlet-toolbar",
	start: function(e, ui){
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
	    setTimeout("mlangosave();", 5); //Timeout is needed to ensure all draganddrop is done, else some elements are doubled while saving
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
    $('.remove').click(function(){
	//When clicking the remove button for a viewlet, move it to the col_listing
	$('#col_listing').append($(this).parents(".mlango-viewlet"));
	mlangosave();
    });
    $('.toggle').click(function() {
	//When you toggle (minimize/maximize) a viewlet, save
	//Actual minimize is done with KSS.
	mlangosave();
    });
    

});

function makedummy(){
    //Build the dummy from scratch
    var dummy = document.createElement("li");
    dummy.setAttribute("id", "mlango-dummy");
    $("#hiddenlist").hide();
    $('#hiddenlist').append(dummy);
    
}
function mlangosave() {
	    var data = "";
	    var minimized = "min=";
	    var mlangodashboard_id = $('#mlango-dashboard').attr('name');
	    $(".mlango-col").each( //Loop over all coluns
		function(){
		    var colid = ($(this).attr("id")+"="); //Get id of column + equal sign
		    data += colid; //Add id to data
		    $(this).find(".viewlet-content").each( //Loop over all viewlet-content
			function(){
			    var id = $(this).attr("id").split("_content")[0]; //Get id of viewlet
				if($(this).hasClass("minimized")){  //Check if content is minimized
				    minimized += id + "--"; //If so, add id to minimized
				}
				data += id + "--"; //Add viewlet-id to current column-id (example: col_1=viewletid--viewletid--viewletid--)
		    });
		     data += "&"; //Put seperator between columns data, (example: col_1=&col_2=viewletid--&col-3=viewletid2--)
		});
	    data += minimized + "&"; //Add minimized to data (exampl:  col_1=viewletid1&col_2=viewletid2--&min=viewletid1--)
	    data += "mlango-dashboard_id="+mlangodashboard_id + "&"; //add dashboard_id to end of data (mlango-dashboard_id=1000&)
	    jQuery.get('storeUserSettings',data); //Perform a GET request with storeUserSettings as target and data as paramters    
	   
    }

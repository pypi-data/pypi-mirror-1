//************************************************************************************
// Copyright (C) 2006, Massimo Beatini
//
// This software is provided "as-is", without any express or implied warranty. In 
// no event will the authors be held liable for any damages arising from the use 
// of this software.
//
// Permission is granted to anyone to use this software for any purpose, including 
// commercial applications, and to alter it and redistribute it freely, subject to 
// the following restrictions:
//
// 1. The origin of this software must not be misrepresented; you must not claim 
//    that you wrote the original software. If you use this software in a product, 
//    an acknowledgment in the product documentation would be appreciated but is 
//    not required.
//
// 2. Altered source versions must be plainly marked as such, and must not be 
//    misrepresented as being the original software.
//
// 3. This notice may not be removed or altered from any source distribution.
//
//************************************************************************************

/* 
THIS FILE HAS BEEN MODIFIED
Some modifications have been made to adapt this to TurboGears applications.
--Claudio Martinez
*/

//
// global variables
//
var isMozilla;
var objDiv = null;
var originalDivHTML = "";
var DivID = "";
var over = false;

mouse_pos_x = 0;
mouse_pos_y = 0;
offset_x = 0;
offset_y = 0;
mouse_dialog_offset_x = 0;
mouse_dialog_offset_y = 0;
dialog_window_offset_x = 0;
dialog_window_offset_y = 0;
dialog_pos_x = 0;
dialog_pos_y = 0;

//
// dinamically add a div to 
// dim all the page
//
function buildDimmerDiv() {
    document.write('<div id="dimmer" class="dimmer" style="width: 0px; height: 0px"></div>');
}

function displayFloatingDiv(divId, title, width, height, left, top) {
	DivID = divId;

    document.getElementById(divId).style.width = width + 'px';
    document.getElementById(divId).style.height = height + 'px';
    document.getElementById(divId).style.left = left + 'px';
    document.getElementById(divId).style.top = top + 'px';
	
	var addHeader;
	
	if (originalDivHTML == "")
	    originalDivHTML = document.getElementById(divId).innerHTML;
	
	addHeader = '<table style="width:' + width + 'px" class="floatingHeader">' +
	            '<tr><td ondblclick="void(0);" onmouseover="over=true;" onmouseout="over=false;" style="cursor:move;height:18px">' + title + '</td>' + 
	            '<td style="width:18px" align="right"><a href="javascript:hiddenFloatingDiv(\'' + divId + '\');void(0);">' + 
	            '<img alt="Close..." title="Close..." src="/tg_widgets/div_dialogs.css/close.jpg" border="0"></a></td></tr></table>';
	

    // add to your div an header	
	document.getElementById(divId).innerHTML = addHeader + originalDivHTML;
	
	
	document.getElementById(divId).className = 'dimming';
	document.getElementById(divId).style.visibility = "visible";


}

function hiddenFloatingDiv(divId) {
	document.getElementById(divId).innerHTML = originalDivHTML;
	document.getElementById(divId).style.visibility='hidden';
	document.getElementById('dimmer').style.visibility = 'hidden';
	document.getElementById('dimmer').style.height = '0px';
	document.getElementById('dimmer').style.width = '0px';
	document.getElementById('dimmer').style.top = '0px';
	document.getElementById('dimmer').style.left = '0px';
	
	DivID = "";
}

function MouseDown(e) {
    if (over) {
        objDiv = document.getElementById(DivID);
        mouse_dialog_offset_x = mouse_pos_x - parseInt(objDiv.style.left, 0);
        mouse_dialog_offset_y = mouse_pos_y - parseInt(objDiv.style.top, 0);
        // prevent selection on IE
        document.body.ondrag = function () { return false; }; 
        document.body.onselectstart = function () {return false;}
        return false; // prevent selection on mozilla/opera
    }
}

function MouseMove(e) {
    if (document.all) {
        mouse_pos_x = window.event.x + offset_x;
        mouse_pos_y = window.event.y + offset_y;
    } else {
        mouse_pos_x = e.pageX;
        mouse_pos_y = e.pageY;
    }
    
    update_offset(e);
    
    if (objDiv) {
        pos_x = mouse_pos_x - mouse_dialog_offset_x;
        pos_y = mouse_pos_y - mouse_dialog_offset_y;
        objDiv.style.left = pos_x + 'px';
        objDiv.style.top = pos_y + 'px';
    }
}

function open_dialog(dom_id, title, width, height, x, y, modal, on_open, on_close) {
    if (x == -1) {
        x = mouse_pos_x;
    }
    
    if (y == -1) {
        y = mouse_pos_y;
    }
    
    if (modal) {
        window_height = document.body.clientHeight;
        window_width = document.body.clientWidth;
        page_height = document.documentElement.clientHeight;
        page_width = document.documentElement.clientWidth;
        
        if (document.body.clientHeight > document.documentElement.clientHeight ||
            document.body.clientWidth > document.documentElement.clientWidth) {
            page_height = document.body.clientHeight;
            page_width = document.body.clientWidth;
            window_height = document.documentElement.clientHeight;
            window_width = document.documentElement.clientWidth;            
        }
        
        dimmer_div = document.getElementById('dimmer');
        dimmer_div.style.visibility = "visible";
        dimmer_div.style.top = '0px';
        dimmer_div.style.left = '0px';
        dimmer_div.style.height = page_height + ' px';
        dimmer_div.style.width = page_width + ' px';
        
        x = offset_x + (window_width / 2 - width / 2);
        y = offset_y + (window_height / 2 - height / 2);
    }
    
    // set a initial value for the position globals
    dialog_pos_x = x;
    dialog_pos_y = y;
    dialog_window_offset_x = x - offset_x;
    dialog_window_offset_y = y - offset_y;
    
    displayFloatingDiv(dom_id, title, width, height, x, y);
    
    if (on_open) {
        eval(on_open);
    }
       
}

function MouseUp() {
    document.body.ondrag = function () { return true; };
    document.body.onselectstart = function () {return true; };
    if (objDiv) {
        dialog_pos_x = parseInt(objDiv.style.left, 0);
        dialog_pos_y = parseInt(objDiv.style.top, 0);
        dialog_window_offset_x = dialog_pos_x - offset_x;
        dialog_window_offset_y = dialog_pos_y - offset_y;
    }
    objDiv = null;
}

function update_offset() {
    if (document.all) {
        if (document.documentElement) {
            // internet explorer when doctype is 4.01
            offset_x = document.documentElement.scrollLeft;
            offset_y = document.documentElement.scrollTop;
        } else {
            // internet explorer when doctype < 4.01
            offset_x = document.body.scrollLeft;
            offset_y = document.body.scrollTop;            
        }
    } else {
        offset_x = window.pageXOffset;
        offset_y = window.pageYOffset;
    }
}

function OnScroll(e) {
    update_offset();
    
    window.status = 'div_id=' + DivID;
    if (DivID) { // being showed
        alert('123123');
        //window.status = DivID;
        dialog_box = document.getElementById(DivID);
        current_x = parseInt(dialog_box.style.left, 0);
        current_y = parseInt(dialog_box.style.top, 0);
        
        move_dialog_y = offset_y - current_y;
        //move_dialog_y = dialog_pos_y - dialog_window_offset_y + offset_y;
        //move_dialog_y = dialog_pos_y + dialog_window_offset_y - offset_y;
        //move_dialog_y = dialog_pos_y + dialog_window_offset_y + offset_y;
        
        //dialog_box.innerHTML = 'off_y=' + offset_y + ' dialog_y=' + dialog_pos_y + 
        //                       ' dialog_off_y=' + dialog_window_offset_y + ' move_dialog_y=' + move_dialog_y;
        
        //dialog_pos_y = offset_x + dialog_window_offset_y;
        
        dialog_box.style.top = offset_y + dialog_window_offset_y + 'px';
        
        //new Effect.Move(dialog_box, {y: move_dialog_y});
        //new Effect.MoveBy(dialog_box, 10, 10);
    }
    return true;
}

function init() {
    // check browser
    isMozilla = (document.all) ? 0 : 1;


    if (isMozilla) {
        document.captureEvents(Event.MOUSEDOWN | Event.MOUSEMOVE | Event.MOUSEUP);
    }

    document.onmousedown = MouseDown;
    document.onmousemove = MouseMove;
    document.onmouseup = MouseUp;
    document.onscroll = OnScroll;

    // add the div
    // used to dim the page
	buildDimmerDiv();
}

// call init
init();

/*
 * Written by Robert Niederreiter, Squarewave Computing, BlueDynamics Alliance
 * 
 * intellidatetime.js
 * 
 * This file contains a modified version of the calendar_formfield.js from
 * plone_ecmascript, much simplyfied, since we can use exactly the input from
 * the calendar to submit. no more needs for complicated select dropdowns,
 * hidden input fields and other silly stuff handling
 */

function onIntelliDateUpdate(cal) {
	var date = {
    	'y': cal.date.getFullYear(),
    	'm': cal.date.getMonth() + 1,
    	'd': cal.date.getDate()
    };
    
    var format = cal.dateFormat;
    var value = '';
    var lastchar = null;
    var currchar;
    for (i = 0; i < format.length; i++) {
    	currchar = format[i];
        if (lastchar != currchar
            && (currchar == 'd'
                || currchar == 'm'
                || currchar == 'y')) {
            lastchar = currchar;
            value += date[currchar] + '.';
            continue;
        }
    }
    
    var input = cal.params.inputField;
    input.value = value.substring(0, value.length - 1);
    
    // cal.hide();
}

function showIntelliDateCalendar(input_id_anchor, input_id,
                                 yearStart, yearEnd) {
    
    var input_id_anchor = document.getElementById(input_id_anchor);
    var input_id = document.getElementById(input_id);
    
    var format = 'dd/mm/y'; // make me configurable
    var dateEl = input_id;
    var mustCreate = false;
    
    var cal = window.intellicalendar;

    var params = {
        'range': [yearStart, yearEnd],
        inputField: input_id
    };

    function param_default(pname, def) {
    	if (typeof params[pname] == "undefined") {
    		params[pname] = def;
    	}
    };

    param_default("inputField", null);
    param_default("displayArea", null);
    param_default("button", null);
    param_default("eventName", "click");
    param_default("ifFormat", "%Y/%m/%d");
    param_default("daFormat", "%Y/%m/%d");
    param_default("singleClick", true);
    param_default("disableFunc", null);
    param_default("dateStatusFunc", params["disableFunc"]); // takes precedence if both are defined
    param_default("dateText", null);
    param_default("firstDay", 1);
    param_default("align", "Bl");
    param_default("range", [1900, 2999]);
    param_default("weekNumbers", true);
    param_default("flat", null);
    param_default("flatCallback", null);
    param_default("onSelect", null);
    param_default("onClose", null);
    param_default("onUpdate", null);
    param_default("date", null);
    param_default("showsTime", false);
    param_default("timeFormat", "24");
    param_default("electric", true);
    param_default("step", 2);
    param_default("position", null);
    param_default("cache", false);
    param_default("showOthers", false);
    param_default("multiple", null);

    if (!(cal && params.cache)) {
        cal = new Calendar(params.firstDay,
                           null,
	                       onIntelliDateUpdate,
	                       function(cal) {
	                           cal.hide();
	                       }
	    );
	    
	    window.intellicalendar = cal,
	    cal.time24 = true;
	    cal.weekNumbers = true;
	    mustCreate = true;
    } else {
        cal.hide();
    }
    
    cal.showsOtherMonths = false;
    cal.yearStep = 2;
    cal.setRange(yearStart, yearEnd);
    cal.params = params;
    cal.setDateStatusHandler(null);
    cal.getDateText = null;
    cal.setDateFormat(format);
    
    if (mustCreate) {
	    cal.create();
        cal.refresh();
    }
    
    if (!params.position) {
        cal.showAtElement(input_id_anchor, null);
    } else {
        cal.showAt(params.position[0], params.position[1]);
    }
    
    return false;
}
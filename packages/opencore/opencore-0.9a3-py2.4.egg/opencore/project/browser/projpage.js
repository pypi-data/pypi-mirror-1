/*

On page load, the SortableManager:

- Finds the table by its id (sortable_table).
- Parses its thead for columns with a "mochi:format" attribute.
- Parses the data out of the tbody based upon information given in the
  "mochi:format" attribute, and clones the tr elements for later re-use.
- Clones the column header th elements for use as a template when drawing 
  sort arrow columns.
- Stores away a reference to the tbody, as it will be replaced on each sort.
- Performs the first sort.


On sort request:

- Sorts the data based on the given key and direction
- Creates a new tbody from the rows in the new ordering
- Replaces the column header th elements with clickable versions, adding an
   indicator (&uarr; or &darr;) to the most recently sorted column.

*/

function trimString (str) {
  str = this != window? this : str;
  return str.replace(/^\s+/g, '').replace(/\s+$/g, '');
}

String.prototype.trim = trimString;

SortableManager = function () {
    this.thead = null;
    this.tbody = null;
    this.columns = [];
    this.rows = [];
    this.sortState = {};
    this.sortkey = 0;
};

mouseOverFunc = function () {
    addElementClass(this, "over");
};

mouseOutFunc = function () {
    removeElementClass(this, "over");
};

ignoreEvent = function (ev) {
    if (ev && ev.preventDefault) {
        ev.preventDefault();
        ev.stopPropagation();
    } else if (typeof(event) != 'undefined') {
        event.cancelBubble = false;
        event.returnValue = false;
    }
};

var showThisMany=10

update(
SortableManager.prototype, {
    "showAllHandler": function(link) {
	link.onmousedown = ignoreEvent;
	link.onclick=this.onLetterClick('all');
    },

    "loadLetterHandlers": function(letterlist) {
	/***
	    setup handlers for alphabet
	***/
	//get links
	var lis = letterlist.getElementsByTagName('li');
	for (var i = 0; i < lis.length; i++) {
	    var li = lis[i];
	    link=li.getElementsByTagName('a')[0];
            link.onmousedown = ignoreEvent;
	    letter=link.getAttribute("name");
            link.onclick = this.onLetterClick(letter.trim());
	}
    },

    "initWithTable": function (table) {
        /***

            Initialize the SortableManager with a table object
        
        ***/

        // Find the thead
        this.thead = table.getElementsByTagName('thead')[0];
        // get the mochi:format key and contents for each column header
        var cols = this.thead.getElementsByTagName('th');
        for (var i = 0; i < cols.length; i++) {
            var node = cols[i];
            var attr = null;
            try {
                attr = node.getAttribute("mochi:format");
            } catch (err) {
                // pass
            }
            var o = node.childNodes;
            this.columns.push({
                "format": attr,
                "element": node,
                "proto": node.cloneNode(true)
            });
        }
        // scrape the tbody for data
        this.tbody = table.getElementsByTagName('tbody')[0];
        // every row
        var rows = this.tbody.getElementsByTagName('tr');
	log("rows " + rows.length)
        for (var i = 0; i < rows.length; i++) {
            // every cell
            var row = rows[i];
            var cols = row.getElementsByTagName('td');
            var rowData = [];
            for (var j = 0; j < cols.length; j++) {
                // scrape the text and build the appropriate object out of it
                var cell = cols[j];
                var obj = scrapeText(cell);
                switch (this.columns[j].format) {
                    case 'isodate':
                        obj = isoDate(obj);
                        break;
                    case 'str':
                        break;
                    case 'istr':
                        obj = obj.toLowerCase();
                        break;
                    // cases for numbers, etc. could be here
                    default:
                        break;
                }
                rowData.push(obj);
            }
            // stow away a reference to the TR and save it
            rowData.row = row.cloneNode(true);
            this.rows.push(rowData);

        }

        // do initial sort on first column
        this.drawSortedRows(this.sortkey, true, false, false);

    },

    "onSortClick": function (name) {
        /***

            Return a sort function for click events

        ***/
        return bind(function () {
            log('onSortClick', name);
            var order = this.sortState[name];
            if (order == null) {
                order = true;
            } else if (name == this.sortkey) {
                order = !order;
            }
            this.drawSortedRows(name, order, true, false);
        }, this);
    },

    "onLetterClick": function (letter) {
        /***

            Return a sort function for click events
	    on little alphabet

        ***/
        return bind(function () {
            this.drawSortedRows(0, true, true, letter);
        }, this);
    },

    "setVisibility": function(rows, regex) {
	/*** makes rows uncollapse and collapse by regex ***/
	for (var i = 0; i < rows.length; i++) {		
	    var row = rows[i];
	    row.style.display = ""; 

	    if(regex){
		cell = row.getElementsByTagName('td')[0];
		var txt = ''
		if (cell.textContent) {
		    txt = cell.textContent;
		}
		else if (cell.innerText) {
		    txt = cell.innerText; 
		}

		if(!txt.trim().match(regex)){
		    row.style.display = "none"; /* visibility='collapsed'; */
		}
	    }
	}
	
    },


    "drawSortedRows": 
	   function (key, forward, clicked, letter) {
        /***

            Draw the new sorted table body, and modify the column headers
            if appropriate

        ***/
        log('drawSortedRows', key, forward);
        this.sortkey = key;
        // sort based on the state given (forward or reverse)
        var cmp = (forward ? keyComparator : reverseKeyComparator);
        this.rows.sort(cmp(key));
	if(!letter){ 
	    // save it so we can flip next time
	    this.sortState[key] = forward; 
	}
        // get every "row" element from this.rows and make a new tbody
        var newBody = TBODY(null, map(itemgetter("row"), this.rows));
        // swap in the new tbody
        this.tbody = swapDOM(this.tbody, newBody);
	//do letter check
	if (letter){
	    var rows = this.tbody.getElementsByTagName('tr');
	    if(letter != 'all'){
		var regex = "^["+letter+letter.toUpperCase()+"]+";
		log("re:" + regex);
		regex = new RegExp(regex);
		this.setVisibility(rows, regex);
	    } else {
		this.setVisibility(rows, false);
	    }

	}
        for (var i = 0; i < this.columns.length; i++) {
            var col = this.columns[i];
            var node = col.proto.cloneNode(true);
            // remove the existing events to minimize IE leaks
            col.element.onclick = null;
            col.element.onmousedown = null;
            col.element.onmouseover = null;
            col.element.onmouseout = null;
            // set new events for the new node
            node.onclick = this.onSortClick(i);
            node.onmousedown = ignoreEvent;
            node.onmouseover = mouseOverFunc;
            node.onmouseout = mouseOutFunc;
            // if this is the sorted column
            if (key == i) {
                // \u2193 is down arrow, \u2191 is up arrow
                // forward sorts mean the rows get bigger going down
                var arrow = (forward ? "\u2193" : "\u2191");
                // add the character to the column header
                node.appendChild(SPAN(null, arrow));
                if (clicked) {
                    node.onmouseover();
                }
            }
 
            // swap in the new th
            col.element = swapDOM(col.element, node);
        }
    }
});

sortableManager = new SortableManager();

/* add our load events */

addLoadEvent(function () {
    sortableManager.initWithTable($('projects-table'));
});

addLoadEvent(function (){
		 sortableManager.showAllHandler($('abc-show-all'))
	     })

addLoadEvent(function () {
    sortableManager.loadLetterHandlers($('abc-click'));
});

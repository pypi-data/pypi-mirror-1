/**
 * User editable tabs for WYSIWYG HTML editors
 * 
 * Idea taken from form_tabbing.js.
 * 
 * @author Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>
 * 
 * @copyright Twinapex Research
 * 
 * @license GPL
 * 
 * @version 1.0
 * 
 * http://www.twinapex.com - High quality Javascript hackers for hire
 * 
 */

// Declare namespace
kuputabs = {}

// Generated tab ids
kuputabs.idCounter = 0;

/**
 * Tab content container
 * 
 * @param {Object} title, non-html user visible name
 * @param {Object} content, htmlish content
 */
kuputabs.Tab = function(title, open) {
	this.id = null; // Generated later
	this.open = open;
	this.title = title;
	this.content = jq('<div class="kuputab-content"><!-- Dynamically generated tab --></div>');
}

/**
 * Bootstrap tab fixing when the page is loaded
 * 
 * Mutates DOM tree suitable for Javascript based tab viewing.
 */
kuputabs.collectTabs = function() {
	
	// List of tabs as Tab instances
	kuputabs.log("Creating tabs");
	
	// Walk through all content nodes which contain tab elements
	jq("h2.kuputab-tab-definer, h2.kuputab-tab-definer-default").parent().each(function() {
	
		var tabs = [];
		
		var collecting = false;
		var curTab = null;
		
		var parent = this;
		
		kuputabs.log("Scanning field " + jq(parent).attr("id"));

		// Walk through all HTML nodes and if we match a tab title
		// walk forward and put all content into a tab,
		// remove the content node from the orignal container
		jq(this).contents().each(function() {
			var t = jq(this);
			
			kuputabs.log("Walking " + t.attr("id"));
							
			if(t.hasClass("kuputab-tab-definer") || t.hasClass("kuputab-tab-definer-default")) {		
			
				// Create new tab
				var open = t.hasClass("kuputab-tab-definer-default");

				kuputabs.log("Making tab" + t.text());

				var tab = new kuputabs.Tab(t.text(), open)
				tabs.push(tab)
				curTab = tab;
				
				// Remove handler definers, 
				// so reruns of init won't double create them
				t.removeClass("kuputab-tab-definer");
				t.removeClass("kuputab-tab-definer-default");
								
				parent.removeChild(this);
			} else {

				// Add node part to the current tab
				if(curTab != null) {
					parent.removeChild(this);	
					curTab.content.append(this);				
				}
			
			}
						
		});
	
		var container = kuputabs.constructContainer(tabs);
		jq(parent).append(container);			
	});
	
	// TODO: Automatically detect open tab from # URL prefix
	
	kuputabs.log("Found tab count:" + kuputabs.idCounter);	
}

/**
 * Create DOM tree for a tab container
 */
kuputabs.constructContainer = function(tabs) {
	
	kuputabs.log("Constructing tab container for tabs " + tabs.length);
	
	var cont = jq('<div class="kuputab-container"><!-- Dynamically generated tab  container --></div>');
	var selectors = jq('<ul class="kuputab-selectors"><!-- Dynamically generated tab selectors --></ul>');

	var i;
	
	if(tabs.length == 0) {
		return;
	}
	
	// Create tab selectors	
	for(i=0; i<tabs.length; i++) {
		var tab = tabs[i];
		var first = (i == 0);
		var last = (i == tabs.length - 1);
		
		kuputabs.log("Creating tab selector " + tab.title);
		
		tab.id = (kuputabs.idCounter++);
		
		var classes = "kuputab-selector";
		if(first) {
			classes += " kuputab-selector-first";
		}
		
		if(last) {
			classes += " kuputab-selector-last";
		}
			
		// generate <li><a><span> struct
		var clicker = jq("<li></li>");
		clicker.attr({ "class" : classes, "id" : "kuputab-selector-" + tab.id});
				
		var link = jq("<a></a>");		
		
		var classes;
		
		// Default open selector
		if(tab.open) {
			classes = "selected";
		} else {
			classes = "";
		}
		
		link.attr({
			id : "kuputab-link-" + tab.id,
			href : "#kuputab-content-" + tab.id,
			"class" : classes
		});

		link.append("<span>" + tab.title + "</span>");		
		
		// Register click handler
		link.click(kuputabs.click);
		
		clicker.append(link);
				
		selectors.append(clicker);
	}
	
	cont.append(selectors);
	
	// Create tab content
	for(i=0; i<tabs.length; i++) {
		var tab = tabs[i];
		var first = (i == 0);
		var last = (i == tabs.length - 1);
				
		// JQuery node containing content
		var content = tab.content;
		content.attr({"id": "kuputab-content-" + tab.id});
		if(tab.open) {
			// pass
		} else {
			tab.content.addClass("hidden");
		}
				
		cont.append(content);
	}	
	
	return cont;
}

/**
 * Click handlers for a tab container.
 * 
 * Hide all tabs and reveal the clicked tab.
 * 
 * @param {Object} container DOM object 
 */
kuputabs.click = function(e) {
	
	kuputabs.log("Caught tab selector click event");
	
	// Make sure we have the a elem selected if the click hits <span> or anonymous node
	var elem = jq(e.target);
	kuputabs.log("Clicked tab " + e.target + " " + elem.get(0).tagName);
	
	if (elem.get(0).tagName.toLowerCase() != "a") {
		elem = elem.parents("a");
	}
	var container = elem.parents(".kuputab-container");
	
	// convert kuputab-link-${id} to plain number
	var id = elem.attr("id");
	if(id == null) {
		alert("Invalid tab selector handler " + e.target);
		return;
	}
	
	id = id.replace(/^kuputab-link-/, "");
	
	kuputabs.log("Filtered id " + id);
	
	var selectors= container.find("li.kuputab-selector a");
	var panels = container.find("div.kuputab-content");

	kuputabs.log("Matches " + selectors.length + " selectors, " + panels.length + " contents");
	
	// Hide existing opened stuff
    selectors.removeClass('selected');
    panels.addClass('hidden');
	
	var panel = container.find("#kuputab-content-" + id);
	var selector = container.find("#kuputab-selector-" + id + " a");
	
	selector.addClass("selected");
	panel.removeClass("hidden");
	
	// Do not let click link event bubble
	return false;		
	
};

/**
 * Page on-load handler.
 */
kuputabs.init = function() {
	
	try {
		// Check if we are in edit or view mode
		if(document.designMode.toLowerCase() == "on") {
			// Edit mode document, do not tabify 
			// but let the user create the content
			return;
		} else {
			kuputabs.collectTabs();		
		}
	} catch(e) {
		kuputabs._printStackTrace(e);
	}
}

kuputabs.log = function(msg) {
	// TODO: Optimze, overload this with a proper logger
	if(typeof(console) != "undefined") {
		if(typeof(console.log) != "undefined") {
			console.log(msg);				
		}
	}
}

// Debug functions - copied from ecmaunit.js
kuputabs._printStackTrace = function(exc){
	
	function print(msg) {
		kuputabs.log(msg);
	}
	
	print(exc);
	
	if (!exc.stack) {
		print('no stacktrace available');
		return;
	};
	var lines = exc.stack.toString().split('\n');
	var toprint = [];
	for (var i = 0; i < lines.length; i++) {
		var line = lines[i];
		if (line.indexOf('ecmaunit.js') > -1) {
			// remove useless bit of traceback
			break;
		};
		if (line.charAt(0) == '(') {
			line = 'function' + line;
		};
		var chunks = line.split('@');
		toprint.push(chunks);
	};
	toprint.reverse();
	
	for (var i = 0; i < toprint.length; i++) {
		print('  ' + toprint[i][1]);
		print('    ' + toprint[i][0]);
	};
	print();
}


jq(kuputabs.init);

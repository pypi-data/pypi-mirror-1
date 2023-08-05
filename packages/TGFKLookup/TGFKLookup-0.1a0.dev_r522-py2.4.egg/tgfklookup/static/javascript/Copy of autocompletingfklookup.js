AutoCompletingFKLookupManager = function (id, textid, lastIDResult, searchController, 
                                idSearchParam, textSearchParam, resultName, 
                                onlySuggest, spinnerOnImg) {
	this.id = id;
    this.idField = null;
	this.textid = textid;
	this.textField = null;
	this.searchController = searchController;
	this.idSearchParam = idSearchParam;
    this.textSearchParam = textSearchParam;
	this.resultName = resultName;
	this.onlySuggest = onlySuggest;
	this.spinnerOnImg = spinnerOnImg;
	this.selectedResultRow = 0;
	this.numResultRows = 0;
	this.specialKeyPressed = false;
	this.isShowingResults = false;
	this.textHasFocus = false;
    this.idHasFocus = false;
	this.sugestionBoxMouseOver = false;
	this.processCount = 0;
	this.lastSearch = null;
	this.spinner = null;
	this.spinnerStatus = 'off';
	this.lastKey = null;
	this.delayedRequest = null;
	this.hasHiddenValue = false;
	this.lastTextResult = null;
	this.lastIDResult = lastIDResult;
    this.keyDownForID = false;
    this.keyDownForText = false;
	bindMethods(this);
};

AutoCompletingFKLookupManager.prototype.initialize = function() {
	// Text field must be set after page renders
	this.textField = getElement(this.textid);
	this.idField = getElement(this.id);
	this.spinner = getElement("autoCompletingFKLookupSpinner"+this.id);
	this.spinnerOffImg = getNodeAttribute(this.spinner,'src');

	updateNodeAttributes(this.textField, {
		"onkeyup": this.theKeyUpForText,
		"onkeydown": this.theKeyDownForText,
        "onkeypress": this.onKeyPress,
		"onblur": this.textLostFocus,
		"onfocus": this.textGotFocus,
		"autocomplete": "off"
	});
	
	updateNodeAttributes(this.idField, {
		"onkeyup": this.theKeyUpForID,
        "onkeydown": this.theKeyDownForID,
		"onblur": this.idLostFocus,
		"onfocus": this.idGotFocus
	});
	
	// Ensure the initial value doesn't get discarded
    // TODO VER
	this.lastIdResult = this.idField.value;
	if (this.idField.value != '') {
        this.delayedRequest = callLater(0.2, this.doDelayedRequestForID);
    }
};

AutoCompletingFKLookupManager.prototype.spinnerToggle = function(newStatus) {
	if (this.spinner && this.spinnerStatus != newStatus) {
		if (this.spinnerStatus == 'on') {
			this.spinnerStatus = 'off';
			this.spinner.src = this.spinnerOffImg;
		} else {
			this.spinnerStatus = 'on';
			this.spinner.src = this.spinnerOnImg;
		}
	}
}

AutoCompletingFKLookupManager.prototype.textLostFocus = function(event) {
	this.textHasFocus = false;
    this.keyDownForText = false;
	if (!this.sugestionBoxMouseOver || this.lastKey == 9) {
		// We only clear the suggestion box when the mouse is not
		// over it or when the user pressed tab. So if the user
		// clicked an item we don't delete the table before the
		// onClick event happens
		this.lastKey = null;
		this.clearResults();
	}
}

AutoCompletingFKLookupManager.prototype.textGotFocus = function(event) {
	this.textHasFocus = true;
}

AutoCompletingFKLookupManager.prototype.idLostFocus = function(event) {
	this.idHasFocus = false;
    this.keyDownForID = false;
}

AutoCompletingFKLookupManager.prototype.idGotFocus = function(event) {
	this.idHasFocus = true;
}

AutoCompletingFKLookupManager.prototype.onKeyPress = function(event) {
    // prevents opera from submiting the form or moving the display
    return !(window.event && (window.event.keyCode == 13));
}

AutoCompletingFKLookupManager.prototype.theKeyDownForText = function(event) {
    this.keyDownForText = true;
    
	// Deal with crappy browser implementations
	event=event||window.event;
	var key=event.keyCode||event.which;
	this.lastKey = key;
    
	// Used to stop processing of further key functions
	this.specialKeyPressed = false;

	// Used when all text is selected then deleted
	// Getting selected text has major cross browswer problems
	// This is gross, but if you are smarter then me (most likely) please fix this
	if (key == 8 || key == 46) {
		checkIfCleared = function checkIfCleared(theManager) {
			if (theManager.textField.value.length == 0) {
				theManager.idField.value = '';
			}
		}
		callLater(0.1, checkIfCleared, this);
	}
	
	// Only perform auto complete functions if there are results to do something with
	if (this.numResultRows > 0) {
		// What key was pressed?
		switch(key) {
			// Enter Key
			case 13:
				var autoCompletingFKLookupSelectedRow = getElement("autoCompletingFKLookup"+this.id+this.selectedResultRow);
				if ((this.onlySuggest) && autoCompletingFKLookupSelectedRow == null){
                    this.clearResults(); 
 		            break;} 
              
                var theCell = getElementsByTagAndClassName("TD", null, autoCompletingFKLookupSelectedRow)[0];
					
				var theCellHidden;			
				if (this.hasHiddenValue) {
					theCellHidden = getElementsByTagAndClassName("TD", null, autoCompletingFKLookupSelectedRow)[1];
				} else {
					theCellHidden = getElementsByTagAndClassName("TD", null, autoCompletingFKLookupSelectedRow)[0];
				}
				
				var autoCompletingFKLookupText = scrapeText(theCell);
				var autoCompletingFKLookupHidden = scrapeText(theCellHidden);
				this.textField.value = autoCompletingFKLookupText;
				this.lastTextResult = autoCompletingFKLookupText;
				this.idField.value = autoCompletingFKLookupHidden;
				this.lastHiddenResult = autoCompletingFKLookupHidden;	
				this.clearResults();

				break;
			// Escape Key
			case 27:
					this.clearResults();
					break;
			// Up Key
			case 38:
				if(this.selectedResultRow > 0) {
					this.selectedResultRow--;
				}
				this.updateSelectedResult();
				break;
			// Down Key
			case 40:
				if(this.selectedResultRow < this.numResultRows - (this.selectedResultRow == null ? 0 : 1)) {
					if (this.selectedResultRow == null) {
						this.selectedResultRow = 0;
					} else {
						this.selectedResultRow++;
					}
				}
				this.updateSelectedResult();
				break;
			default:
				//pass
		}
                // Make sure other functions know we performed an autocomplete function
                if (key == 13 || key == 27 || key == 38 || key == 40)
                    this.specialKeyPressed = true;
	}
	return !this.specialKeyPressed;
};

AutoCompletingFKLookupManager.prototype.updateSelectedResult = function() {
	// TODO: Add code to move the cursor to the end of the line
	for( var i=0; i<this.numResultRows; i++) {
		if(this.selectedResultRow == i) {
			swapElementClass("autoCompletingFKLookup"+this.id+i, "autoTextNormalRow", "autoTextSelectedRow");
		} else {
			swapElementClass("autoCompletingFKLookup"+this.id+i, "autoTextSelectedRow", "autoTextNormalRow");
		}
	}
}

AutoCompletingFKLookupManager.prototype.clearResults = function() {
	// Remove all the results
	var resultsHolder = getElement("autoCompletingFKLookupResults"+this.id);
	replaceChildNodes(resultsHolder, null);

	// Clear out our result tracking
	this.selectedResultRow = 0;
	this.numResultRows = 0;
	this.lastSearch = null;
}

AutoCompletingFKLookupManager.prototype.displayResultsFromID = function(result) {
    if (result[this.resultName][0]) {
        this.textField.value = result[this.resultName][0][1];
    } else {
        this.textField.value = '';
    }
    
    this.processCount = this.processCount - 1;
	if (this.processCount == 0) {
		this.spinnerToggle('off');
	}
}

AutoCompletingFKLookupManager.prototype.displayResultsFromText = function(result) {
	// if the field lost focus while processing this request, don't do anything
	if (!this.textHasFocus) {
		this.updateSelectedResult();
		this.processCount = this.processCount - 1;
		if (this.processCount == 0) {
			this.spinnerToggle('off');
		}
		return false;
	}
	var fancyTable = TABLE({"class": "autoTextTable",
					"name":"autoCompletingFKLookupTable"+this.id,
					"id":"autoCompletingFKLookupTable"+this.id},
			       null);
	var fancyTableBody = TBODY(null,null);
	// Track number of result rows and reset the selected one to the first
	var textItems = result[this.resultName];
	this.numResultRows = textItems.length;
	if (this.onlySuggest) this.selectedResultRow = null;
    else this.selectedResultRow = 0;

	// Grab each item out of our JSON request and add it to our table
	this.isShowingResults = false;
	
	this.hasHiddenValue = isArrayLike(textItems[0]);
	
	for ( var i in textItems ) {
		var currentItem = textItems[i];
		var currentItemValue = textItems[i];
		if (this.hasHiddenValue) {
			currentItem = currentItem[1];
			currentItemValue = currentItemValue[0];
		}
				
		var rowAttrs = {
			"class": "autoTextNormalRow",
			"name":"autoCompletingFKLookup"+this.id+i,
			"id":"autoCompletingFKLookup"+this.id+i,
			"onmouseover":"AutoCompletingFKLookupManager"+this.id+".sugestionBoxMouseOver = true; AutoCompletingFKLookupManager"+this.id+".selectedResultRow="+i+"; AutoCompletingFKLookupManager"+this.id+".updateSelectedResult();",
			"onclick":"p = new Object; p.keyCode=13; AutoCompletingFKLookupManager"+this.id+".theKeyDownForText(p);",
			"onmouseout":"AutoCompletingFKLookupManager"+this.id+".sugestionBoxMouseOver = false; "
		};

		if (typeof result.options!="undefined" && result.options.highlight) {
			var searchedText = currentItem.toLowerCase().match(this.textField.value.toLowerCase());
			var end = searchedText.index + searchedText[0].length;
			var currentRow = TR(rowAttrs,
					    TD(null,
					       createDOM("nobr", null, SPAN({"class": "autoTextHighlight"}, currentItem.substr(searchedText.index, searchedText[0].length)),
					       SPAN(null, currentItem.substr(end))
					       )));
			if (this.hasHiddenValue)
				appendChildNodes(currentRow, TD({"class": "autoTextHidden"}, SPAN(null, currentItemValue)));
		} else {
			var currentRow = TR(rowAttrs,
					    TD(null,
					       createDOM("nobr", null, SPAN(null, currentItem)
					       )));
			if (this.hasHiddenValue)
				appendChildNodes(currentRow, TD({"class": "autoTextHidden"}, SPAN(null, currentItemValue)));
		}
		appendChildNodes(fancyTableBody, currentRow);

		// Found at least 1 result
		this.isShowingResults = true;
	}
	appendChildNodes(fancyTable, fancyTableBody);

	// Swap out the old results with the newly created table
	var resultsHolder = getElement("autoCompletingFKLookupResults"+this.id);
	replaceChildNodes(resultsHolder, fancyTable);

	var textField = getElement(this.textField);
	var p = document.getElementById("autoCompletingFKLookupResults"+this.id);
	if (p) {
		p.style.left = getLeft(textField)+"px";
		p.style.top = getBottom(textField)+"px";
	}

	this.updateSelectedResult();
	this.processCount = this.processCount - 1;
	if (this.processCount == 0) {
		this.spinnerToggle('off');
	}
}

AutoCompletingFKLookupManager.prototype.doDelayedRequestForID = function () {
    return this.doDelayedRequest('id');
}

AutoCompletingFKLookupManager.prototype.doDelayedRequestForText = function () {
    return this.doDelayedRequest('text');
}

AutoCompletingFKLookupManager.prototype.doDelayedRequest = function (type) {
	this.delayedRequest = null;

	// Check again if the field is empty, if it is, we wont search.
	if (!this.textField.value && type=='text') {
		this.clearResults();
		return false;
	}

	// Get what we are searching for
	var resultName = this.resultName;

	this.processCount = this.processCount + 1;
	this.spinnerToggle('on');

	var params = { "tg_format" : "json",
		       "tg_random" : new Date().getTime()};
	
    if (type == 'id') {
        this.lastSearch = this.idField.value;
        params[this.idSearchParam] = this.idField.value;
    } else {
        this.lastSearch = this.textField.value;
        params[this.textSearchParam] = this.textField.value;
    }
    
	var d = loadJSONDoc(this.searchController + "?" + queryString(params));
    
    if (type == 'id') {
        d.addCallback(this.displayResultsFromID);
    } else {
        d.addCallback(this.displayResultsFromText);
    }
}

AutoCompletingFKLookupManager.prototype.theKeyUpForText = function(event) {
    // Stop processing if key wasn't pressed on the TEXT field
    if (!this.keyDownForText) return false;
    
	// Stop processing if a special key has been pressed. Or if the last search requested the same string
	if (this.specialKeyPressed || (this.textField.value==this.lastSearch)) return false;

	// if this.textField.value is empty we don't need to schedule a request. We have to clear the list.
	if (!this.textField.value) {
		if (this.delayedRequest)
			this.delayedRequest.cancel();
		this.clearResults();
		return false;
	}

	// If theKeyUp is activated and there is an old JSON request
	// scheduled for execution, cancel the old request and
	// schedule a new one. The cancellation ensures that we won't
	// spam the server with JSON requests.
	if (this.delayedRequest)
		this.delayedRequest.cancel();

	// If the user has not typed anything for 200 ms, we can be
	// reasonably sure that he or she wants to the auto completions.
	this.delayedRequest = callLater(0.2, this.doDelayedRequestForText);
	
	if(this.lastIDResult == this.textField.value) {
		this.idField.value = this.lastHiddenResult;
	} else {
		this.idField.value = '';
	}

	return true;
};

AutoCompletingFKLookupManager.prototype.theKeyDownForID = function(event) {
    this.keyDownForID = true;
}

AutoCompletingFKLookupManager.prototype.theKeyUpForID = function(event) {
    if (!this.keyDownForID) return false;
    this.keyDownForID = false;

	// Stop processing if a special key has been pressed. Or if the last search requested the same string
	if ((this.idField.value==this.lastSearch)) return false;

    // if a key was pressed, we clear the text
    this.textField.value = '';    

	// if this.textField.value is empty we don't need to schedule a request. We have to clear the list.
	if (!this.idField.value) {
		if (this.delayedRequest)
			this.delayedRequest.cancel();
		this.clearResults();
		return false;
	}

	// If theKeyUp is activated and there is an old JSON request
	// scheduled for execution, cancel the old request and
	// schedule a new one. The cancellation ensures that we won't
	// spam the server with JSON requests.
	if (this.delayedRequest)
		this.delayedRequest.cancel();
    
	// If the user has not typed anything for 200 ms, we can be
	// reasonably sure that he or she wants to the auto completions.
	this.delayedRequest = callLater(0.2, this.doDelayedRequestForID);
    
	return true;
};

function getLeft(s) {
    return getParentOffset(s,"offsetLeft")
}

function getTop(s) {
    return getParentOffset(s,"offsetTop")
}

function getBottom(s) {
    return s.offsetHeight+getTop(s)
}

function getParentOffset(s,offsetType) {
    var parentOffset=0;
    while(s) {
        parentOffset+=s[offsetType];
        s=s.offsetParent
    }
    return parentOffset
}

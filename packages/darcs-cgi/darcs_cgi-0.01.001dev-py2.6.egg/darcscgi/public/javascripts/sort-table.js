function setupSortedTables(className,order){
    var tableTags = document.getElementsByTagName("table");
    for (var i=0; i < tableTags.length; i++){
        if (tableTags[i].className == className){
            new sortableTable(tableTags[i],order);
        }
    }
}

function sortableTable(tableElement,order){
    this.tableProperties = {
            // width: 1-col, 2-col, 3-col, ... n-col
        width:0,
            // position: 0-col, 1-col, 2-col, ... (n-1)-col
        position:-1,
            // sorting: 0-col, 1-col, 2-col, ... (n-1)-col
        sorting:new Array(),
        cssHeaderBackground:new Array()
    };
    this.tableProperties.sorting[0]=order;
    this.initializeHandler(tableElement);
}

sortableTable.prototype.initializeHandler = function(tableElement){
    this.addEvent(tableElement,"click",this.tableHandler());

    this.tableProperties.width = this.getWidth(tableElement);
    this.setSortingArray(this.tableProperties.width);

    var tableHeader = tableElement.getElementsByTagName("thead")[0];
    var tableHeaderRow = "";
    var increment = 0;
    while (increment<tableHeader.childNodes.length && tableHeaderRow === ""){
        var childNode = tableHeader.childNodes[increment];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "tr"){
            tableHeaderRow = childNode;
        }
        increment++;
    }
    this.backupCssRow(tableHeaderRow,this.tableProperties.cssHeaderBackground);
}

sortableTable.prototype.backupCssRow = function(rowElement,cssBackupArray){
    var element = 0;
    for (var i=0; i<rowElement.childNodes.length; i++){
        var childNode = rowElement.childNodes[i];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "th"){
            cssBackupArray[element] = childNode.style.backgroundColor;
            element++;
        }
    }
}

sortableTable.prototype.toggleCellCss = function(cellElement,cssBackupArray,newCellCss){
    var parentRow = cellElement.parentNode;
    var element = 0;
    for (var i=0; i<parentRow.childNodes.length; i++){
        var childNode = parentRow.childNodes[i];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "th"){
            if (!childNode.isSameNode(cellElement)){
                childNode.style.backgroundColor = cssBackupArray[element];
            }
            else{
                childNode.style.backgroundColor = newCellCss;
            }
            element++;
        }
    }
}

sortableTable.prototype.setSortingArray = function(width){
    for(var i=0; i<width; i++){
        // 0    no sorting
        // 1    desc sort
        // 2    asc sort
        this.tableProperties.sorting[i] = 0;
    }
}

sortableTable.prototype.zeroSortingArray = function(){
    for(var i=0; i<this.tableProperties.sorting.length; i++){
        this.tableProperties.sorting[i] = 0;
    }
}

sortableTable.prototype.tableHandler = function(){
    var tableClosedThis = this;
    return function(event){
        event.preventDefault();
        var target = event.target;
        var tableRowsArray = new Array();
        if (target.parentNode.parentNode.tagName.toLowerCase() == "thead"){
            tableClosedThis.tableProperties.position = tableClosedThis.getPosition(target);
            tableRowsArray = tableClosedThis.inputNodes(event.currentTarget);

            // If no sorting set ascending sort flag
            // If descending set ascending sort flag
            if (tableClosedThis.tableProperties.sorting[tableClosedThis.tableProperties.position-1] == 0 || tableClosedThis.tableProperties.sorting[tableClosedThis.tableProperties.position-1] == 1){
                tableClosedThis.zeroSortingArray();
                tableClosedThis.tableProperties.sorting[tableClosedThis.tableProperties.position-1] = 2;
            }
            // If ascending set descending sort flag
            else if (tableClosedThis.tableProperties.sorting[tableClosedThis.tableProperties.position-1] == 2){
                tableClosedThis.zeroSortingArray();
                tableClosedThis.tableProperties.sorting[tableClosedThis.tableProperties.position-1] = 1;
            }

            tableRowsArray.sort(tableClosedThis.sortNodes());
            tableClosedThis.appendReplace(event.currentTarget, tableRowsArray);
            tableClosedThis.toggleCellCss(target,tableClosedThis.tableProperties.cssHeaderBackground,"rgb(180,180,230)");
        }
    }
}

sortableTable.prototype.getWidth = function(tableElement){
    var tableHead = tableElement.getElementsByTagName("thead")[0];
    var width = 0;
    var increment = 0;
    var tableHeadRow = "";
    while (increment<tableHead.childNodes.length && tableHeadRow === ""){
        var childNode = tableHead.childNodes[increment];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "tr"){
            tableHeadRow = childNode;
        }
        increment++;
    }
    for(var i=0; i<tableHeadRow.childNodes.length;i++){
        if (tableHeadRow.childNodes[i].nodeType == Node.ELEMENT_NODE && tableHeadRow.childNodes[i].tagName.toLowerCase() == "th"){
            width++;
        }
    }
    return width;
}

sortableTable.prototype.getPosition = function(node){
    var parentRow = node.parentNode;
    var position = -1;
    var increment = 0;
    while (increment<parentRow.childNodes.length && position<0){
        var childNode = parentRow.childNodes[increment];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "th"){
            if (childNode.isSameNode(node)){
                position = increment+1;
            }
        }
        increment++;
    }
    return position;
}

sortableTable.prototype.getWidthAndPosition = function(node){
    var parentRow = node.parentNode;
    var locationsObject = {
        position:0,
        width:0
    }
    for(var i=0; i<parentRow.childNodes.length;i++){
        var childNode = parentRow.childNodes[i];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "th"){
            locationsObject.width++;
            if (childNode.isSameNode(node)){
                locationsObject.position=locationsObject.width;
            }
        }
    }
    return locationsObject;
}

sortableTable.prototype.inputNodes = function(table){
    var tableBody = table.getElementsByTagName("tbody")[0];
    var tableRowsArray = new Array();
    var increment = 0;
    for(var i=0; i<tableBody.childNodes.length;i++){
        var childNode = tableBody.childNodes[i];
        if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "tr"){
            tableRowsArray[increment] = childNode;
            increment++;
        }
    }
    return tableRowsArray;
}

sortableTable.prototype.sortNodes = function() {
    var sortClosedThis = this;
    return function(a,b){
        function getTextValue(tableRow){
            var nodes = 0;
            var elements = 0;
            var text = "";
            while(elements < sortClosedThis.tableProperties.width && elements < sortClosedThis.tableProperties.position && text == ""){
                var childNode = tableRow.childNodes[nodes];
                if (childNode.nodeType == Node.ELEMENT_NODE && childNode.tagName.toLowerCase() == "td"){
                    elements++;
                    if (elements == sortClosedThis.tableProperties.position){
                        text = childNode.childNodes[0].nodeValue;
                    }
                }
                nodes++;
            }
            return text;
        }

        var aText = getTextValue(a);
        var bText = getTextValue(b);

        if (/^([0-9.]+)\s?(Gb|Mb)\s?$/.test(aText) && /^([0-9.]+)\s?(Gb|Mb)\s?$/.test(bText)){
            aText = parseFloat(aText);
            bText = parseFloat(bText);
        }
        else {
            aText = aText.toLowerCase();
            bText = bText.toLowerCase();
        }

        // If 1(descending) or 0(no order) make descending
        if (sortClosedThis.tableProperties.sorting[sortClosedThis.tableProperties.position-1] == 0 || sortClosedThis.tableProperties.sorting[sortClosedThis.tableProperties.position-1] == 1){
            return ((aText < bText) ? -1 : ((aText > bText) ? 1 : 0));
        }
        // If 2(ascending) make ascending
        else if (sortClosedThis.tableProperties.sorting[sortClosedThis.tableProperties.position-1] == 2){
            return ((aText > bText) ? -1 : ((aText < bText) ? 1 : 0));
        }
        // failsafe case, make ascending
        else {
            return ((aText > bText) ? -1 : ((aText < bText) ? 1 : 0));
        }
    }
}

sortableTable.prototype.appendReplace = function(table, sortedTableRowsArray){
    var tableBody = table.getElementsByTagName("tbody")[0];
    var arrayLength = sortedTableRowsArray.length;
    for (var i=arrayLength-1; i>=0; i--){
        tableBody.appendChild(sortedTableRowsArray[i]);
    }
}

/////////////////////////////////////////////////////
// simple event helper functions
/////////////////////////////////////////////////////
sortableTable.prototype.addEvent = function(element, type, fn) {
    if (element.addEventListener) {
        element.addEventListener(type, fn, false);
    } else if (element.attachEvent) {
        element.attachEvent('on'+type, fn);
    }
    return element;
}
sortableTable.prototype.removeEvent = function(element, type, fn) {
    if (element.removeEventListener) {
        element.removeEventListener(type, fn, false);
    } else if (element.detachEvent) {
        element.detachEvent('on'+type, fn);
    }
    return element;
}

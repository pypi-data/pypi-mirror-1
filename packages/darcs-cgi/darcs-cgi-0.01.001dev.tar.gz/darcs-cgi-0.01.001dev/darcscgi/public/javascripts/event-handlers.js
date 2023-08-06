/////////////////////////////////////////////////////
// simple event helper functions
/////////////////////////////////////////////////////
function addEvent(element, type, fn) {
    if (element.addEventListener) {
        element.addEventListener(type, fn, false);
    } else if (element.attachEvent) {
        element.attachEvent('on'+type, fn);
    }
    return element;
}
function removeEvent(element, type, fn) {
    if (element.removeEventListener) {
        element.removeEventListener(type, fn, false);
    } else if (element.detachEvent) {
        element.detachEvent('on'+type, fn);
    }
    return element;
}

// Area update functions.

function requestUpdateArea(url, sourceAreasStr, targetName, targetAreasStr, elementPath) {

    var fieldNames = new Array();
    var targetFieldNames = new Array();

    for (var i = 0; i < document.forms.length; i++) {
        var form = document.forms[i];
        for (var j = 0; j < form.elements.length; j++) {
            var fieldName = form.elements[j].name;
            checkField(fieldName, sourceAreasStr, fieldNames);
            checkField(fieldName, targetAreasStr, targetFieldNames);
        }
    }

    return _requestUpdate(url, fieldNames, targetName, targetFieldNames, elementPath);
}

// Field list update functions.

function requestUpdate(url, fieldNamesStr, targetName, targetFieldNamesStr, elementPath) {

    return _requestUpdate(url, fieldNamesStr.split(","), targetName, targetFieldNamesStr.split(","), elementPath);
}

// Internal functions.

function checkField(fieldName, areasStr, areaFieldNames) {

    // Process each area name.

    var areaArray = areasStr.split(",");
    for (var i = 0; i < areaArray.length; i++) {
        var areaName = areaArray[i];

        // Skip empty area names (arising through empty elements in the CSV list).

        if (areaName == "") {
            continue;
        }

        if (fieldName.indexOf(areaName) == 0) {
            areaFieldNames.push(fieldName);
        }
    }
}

function _requestUpdate(url, fieldNames, targetName, targetFieldNames, elementPath) {

    // Note that XMLHttpRequest access may be denied if Mozilla believes that
    // this resource's URL and the supplied URL are different.

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url, false);

    // Add the element path specification.

    var requestBody = ("element-path=" + elementPath);

    // Send the controlling field value.

    requestBody += addFields(fieldNames, false);
    requestBody += addFields(targetFieldNames, true);

    // Load the remote document with the given parameters sent as text in the request body.

    xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlhttp.send(requestBody);

    // Parse the result document.

    var newDocument = Sarissa.getDomDocument();
    newDocument = (new DOMParser()).parseFromString(xmlhttp.responseText, "text/xml");

    // Find the definition of the affected field in the result document.

    var newElement = newDocument.getElementById(targetName);
    var targetElement = document.getElementById(targetName);

    // Insert the new definition into the current document.

    if (newElement != null && targetElement != null) {
        var importedElement = document.importNode(newElement, true);
        targetElement.parentNode.replaceChild(importedElement, targetElement);
        //importedElement.setAttribute("style", "background-color:red;");
    }

    // NOTE: Test Konqueror bug.

    //showMismatch(targetFieldNameArray);

    return false;
}

function addFields(fieldNames, disable) {

    var requestBody = "";

    // Process each target field name.
    // Add the values of the dependent fields.

    for (var i = 0; i < fieldNames.length; i++) {
        var fieldName = fieldNames[i];

        // Skip empty field names (arising through empty elements in the CSV list).

        if (fieldName == "") {
            continue;
        }

        // Find the values of the target field.

        var fieldValue;
        var fieldNodes = document.getElementsByName(fieldName);
        for (var v = 0; v < fieldNodes.length; v++) {

            // Test for different field types.

            if (fieldNodes[v].options) {
                for (var opt = 0; opt < fieldNodes[v].options.length; opt++) {
                    if (fieldNodes[v].options[opt].selected) {
                        fieldValue = fieldNodes[v].options[opt].value;
                        requestBody += ("&" + encodeURIComponent(fieldName) + "=" + encodeURIComponent(fieldValue));
                    }
                }
            } else if (fieldNodes[v].type != 'checkbox' && fieldNodes[v].type != 'radio' || fieldNodes[v].checked) {
                fieldValue = fieldNodes[v].value;
                requestBody += ("&" + encodeURIComponent(fieldName) + "=" + encodeURIComponent(fieldValue));
            }
        }

        // NOTE: Konqueror hack: disable fields.

        if (disable) {
            disableFields(fieldName);
        }
    }

    return requestBody;
}

function disableFields(targetFieldName) {

    for (var i = 0; i < document.forms.length; i++) {
        var form = document.forms[i];
        for (var j = 0; j < form.elements.length; j++) {
            if (form.elements[j].name == targetFieldName) {
                form.elements[j].name = "";
            }
        }
    }
}

function showMismatch(targetFieldNameArray) {

    // Show how the number of field elements with a given name can be different
    // from the number known to the DOM Level 0 part of the API.

    for (var h = 0; h < targetFieldNameArray.length; h++) {
        var targetFieldName = targetFieldNameArray[h];
        var targetFieldNodes = document.getElementsByName(targetFieldName);
        alert("Nodes for " + targetFieldName + ": " + targetFieldNodes.length);

        var count = 0;
        for (var i = 0; i < document.forms.length; i++) {
            var form = document.forms[i];
            for (var j = 0; j < form.elements.length; j++) {
                if (form.elements[j].name == targetFieldName) {
                    count++;
                }
            }
        }
        alert("Fields for " + targetFieldName + ": " + count);
    }
}

// vim: tabstop=4 expandtab shiftwidth=4

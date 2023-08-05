/*
 * SmartPrintNG - high-quality export of Plone content to
 * PDF, RTF, ODT, WML and DOCX
 *
 * (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
 */

var in_progres = false;


// remove stuff from the copied content region

function cleanupContent(node) {

    var arr = node.getElementsByTagName('div');
    for (var i=0; i<arr.length; i++) {
        var classname= arr[i].className;
        if (classname.indexOf('documentActions') != -1 || 
            classname.indexOf('documentByLine') != -1) {
            arr[i].parentNode.removeChild(arr[i]);
        }
    }

    var arr = node.getElementsByTagName('p');
    for (var i=0; i<arr.length; i++) {
        if (arr[i].id == 'link-presentation') {
            arr[i].parentNode.removeChild(arr[i]);
        }
    }

    var arr = node.getElementsByTagName('div');
    for (var i=0; i<arr.length; i++) {
        if (arr[i].id == 'smartprint') {
            arr[i].parentNode.removeChild(arr[i]);
        }
    }
}

// return either the 'content' element or the 'region-content' element

function getContentElement() {

    var el = $('content');
    if (! el)
        el = $('region-content');


    if (! el) 
        alert('No DOM node with id "region-content" or "content" found'); 

    return el;
}


function openControl() {

    if (! $('smartprint')) {

        var divContent  = getContentElement().cloneNode(true);
        if (! divContent) {
            alert('Error: the element with id=content could not be found!');
            return;
        }

        var newdiv = document.createElement('div');
        newdiv.id = 'smartprint';
        getContentElement().appendChild(newdiv);
    } else {

        if (in_progres) {
            alert('Conversion in progres...please wait');
            return;
        }

        closeControl();
    }
}

function closeControl() {
    Element.remove('smartprint');
}


// open the SP control and show the selection HTML snippet

function showResponse(request) {
    if ($('smartprint'))
        $('smartprint').innerHTML = request.responseText;
}

function smartPrintSelection(url, template) {

    openControl();

    var url = url + '/' + template;
    var r = new Ajax.Request(url, {method: 'GET',
                                   onComplete: showResponse
                            });

}


function startConversion(url) {

    var divContent  = getContentElement().cloneNode(true);
    if (! divContent) {
        alert('Error: the element with id=content could not be found!');
        return;
    }

    // Not sure if we should cleanup the HTML on the server side.
    cleanupContent(divContent);

    // put HTML into the form in order to generate a query string from it
    $('smartprint-html').value = divContent.innerHTML

    var postBody= Form.serialize('smartprint-selection-form');

    in_progres = true;

    // Load "in-progres" page
    var r = new Ajax.Request(url + '/sp_progres', {
                              method: 'GET',
                              asynchronous: false,
                              onComplete: showResponse
                            });

    var r2 = new Ajax.Request(url + '/smartPrintConvert', {
                               method: 'POST',
                               asynchronous: true,
                               postBody: postBody,
                               requestHeaders: ['content-type', 'application/x-www-form-urlencoded'],
                               onComplete: function(request) {
                                    in_progres = false;
                                    closeControl();
                                    if (request.status == 200) {
                                        var filename = request.responseText;
                                        document.location = url + '/smartPrintDeliver?filename=' + filename;
                                    } else {
                                        var status = request.status;
                                        alert('Conversion failed (Error code: ' + status + ')');
                                    }
                               },
                               onFailure: function(request){
                                   in_progres = false;
                                   var status = request.status;
                                   alert('Conversion failed (Error code: ' + status + ')');
                                   closeControl();
                               }
                            });
}

/*
 * SmartPrintNG - high-quality export of Plone content to
 * PDF, RTF, ODT, WML and DOCX
 *
 * (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
 *
 * reviewed by SauZheR to use JQuery framework
 */

var in_progres = false;

var $j = jQuery.noConflict();

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

    var el = $j('#content');
    if (! el[0])
        el = $j('#region-content');


    if (! el[0])
        alert('No DOM node with id "region-content" or "content" found');

    return el;
}


function openControl() {

    if (! $j('#smartprint')[0]) {

        var divContent  = getContentElement().clone(true);
        if (! divContent) {
            alert('Error: the element with id=content could not be found!');
            return;
        }

        var newdiv = document.createElement('div');
        newdiv.id = 'smartprint';
        getContentElement().append(newdiv);
    } else {

        if (in_progres) {
            alert('Conversion in progres...please wait');
            return;
        }

        closeControl();
    }
}

function closeControl() {
    $j('#smartprint').remove();
}


// open the SP control and show the selection HTML snippet

function showResponse(request) {
    if ($j('#smartprint'))
        $j('#smartprint')[0].innerHTML = request.responseText;
}

function smartPrintSelection(url, template) {

    openControl();

    var url = url + '/' + template;
    var r = $j.ajax( {url: url,
                    type: 'GET',
                    complete: showResponse
                            });

}


function startConversion(url) {

    var divContent  = getContentElement().clone(true);
    if (! divContent) {
        alert('Error: the element with id=content could not be found!');
        return;
    }
    divContent =divContent[0]
    // Not sure if we should cleanup the HTML on the server side.
    cleanupContent(divContent);

    // put HTML into the form in order to generate a query string from it
    $j('#smartprint-html')[0].value = divContent.innerHTML

    var postBody= $j('#smartprint-selection-form').serialize();

    in_progres = true;

    // Load "in-progres" page
    var r = $j.ajax( {url: url + '/sp_progres',
                              type: 'GET',
                              asynchronous: false,
                              complete: showResponse
                            });

    var r2 = $j.ajax({url:url + '/smartPrintConvert',
                               type: 'POST',
                               asynchronous: true,
                               data: postBody,
                               requestHeaders: ['content-type', 'application/x-www-form-urlencoded'],
                               complete: function(request) {
                                    in_progres = false;
                                    closeControl();
                                    if (request.status == 200) {
                                        var filename = request.responseText;
                                        document.location = url + '/smartPrintDeliver?filename=' + encodeURIComponent(filename);
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

// only for Plone without kss

function getElementsByClassName(oElm, strTagName, strClassName){
    var arrElements = (strTagName == "*" && oElm.all)? oElm.all : oElm.getElementsByTagName(strTagName);
    var arrReturnElements = new Array();
    strClassName = strClassName.replace(/\-/g, "\\-");
    var oRegExp = new RegExp("(^|\\s)" + strClassName + "(\\s|$)");
    var oElement;
    for(var i=0; i<arrElements.length; i++){
        oElement = arrElements[i];      
        if(oRegExp.test(oElement.className)){
            arrReturnElements.push(oElement);
        }   
    }
    return (arrReturnElements)
}

function FCKeditor_OnComplete( editorInstance )
{
    editorInstance.Events.AttachEvent( 'OnAfterLinkedFieldUpdate', finalizePublication ) ;
}

// start all instances found in the page
FCKeditor_Plone_Init = function () {
    var fckContainers = getElementsByClassName (document, 'div', 'fckContainer');
    for(var i=0; i<fckContainers.length; i++){
        var fckContainer = fckContainers [i];
        var fckContainerId = fckContainer.getAttribute('id');
        var inputname = fckContainerId.replace("_fckContainer","");
        FCKeditor_Plone_start_instance (fckContainer, inputname);
    }     
}

registerPloneFunction(FCKeditor_Plone_Init);

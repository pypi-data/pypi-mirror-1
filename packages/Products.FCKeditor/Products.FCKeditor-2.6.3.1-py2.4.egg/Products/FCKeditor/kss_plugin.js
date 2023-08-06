

/* Base kukit plugins for fckeditor*/

kukit.actionsGlobalRegistry.register("plone-initFCKeditor", function(oper) {
    oper.evaluateParameters([], {}, 'plone-initFCKeditor action'); 
    kukit.log('start the kss treatment');    
    var fckContainer = oper.node;
    FCKeditor_OnComplete = function ( editorInstance ) {      
        kukit.log('attach events on standard base_edit form submit');
        editorInstance.Events.AttachEvent( 'OnAfterLinkedFieldUpdate', finalizePublication ) ;
        var oField = editorInstance.LinkedField;      
        oField.setAttribute('class', 'fcklinkedField');          
        kukit.fo.fieldUpdateRegistry.register(oField,
                {editor: null,
                 node: oField,
                 doInit: function() {            
                    var self = this;         
                    Submit_inline = function ( ) {    
                        oForm = new kukit.fo.CurrentFormLocator(self.node).getForm();
                        Save_inline (oField.name, oForm, editorInstance);                 
                        }                     
                    kukit.log('redefine the Save command to save content inline');
                    editorInstance.Commands.GetCommand('Save').Execute = Submit_inline ;
                    },                 
                 doUpdate: function() {              
                    finalizePublication(editorInstance);
                    kukit.log('update field when clicking on submit or saving inline');
                    }
                 });        
    }     
    var fckContainerId = fckContainer.getAttribute('id');
    var inputname = fckContainerId.replace("_fckContainer","");     
    kukit.logDebug('launch FCKEditor for field ' + inputname);  
    FCKeditor_Plone_start_instance (fckContainer, inputname);   
    kukit.logDebug('plone-initFCKeditor action done.'); 
});

kukit.commandsGlobalRegistry.registerFromAction('plone-initFCKeditor', 
    kukit.cr.makeSelectorCommand);

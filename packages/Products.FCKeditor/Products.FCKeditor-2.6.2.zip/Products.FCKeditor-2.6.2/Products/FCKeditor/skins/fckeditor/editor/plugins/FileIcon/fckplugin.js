/*
 * FCKeditor - The text editor for internet
 * Copyright (C) 2003-2004 Frederico Caldeira Knabben
 * 
 * Licensed under the terms of the GNU Lesser General Public License:
 * 		http://www.opensource.org/licenses/lgpl-license.php
 * 
 * For further information visit:
 * 		http://www.fckeditor.net/
 * 
 * File Name: fckplugin.js
 * 	This is the plugin definition file for file icon.
 * 
 * Version:  2.0 RC3
 * Modified: 2005-01-27 11:20:10
 * 
 * File Authors:
 * 		Andrey Grebnev (andrey.grebnev@blandware.com)
 */

// Register the related commands.
FCKCommands.RegisterCommand(
    'FileIcon',
    new FCKDialogCommand(
        // XXX why the translation system doesn't work ?
        //FCKLang.DlgFileIconTitle,
        //FCKLang.DlgFileIconTitle,
        'Insert file icon',
        'Insert file icon',
        FCKConfig.PluginsPath + 'FileIcon/fileicon.html',
        330,
        280
    )
);

// Create the "FileIcon" toolbar button.
var oFileIcon = new FCKToolbarButton('FileIcon', FCKLang['DlgFileIconTitle']);
oFileIcon.IconPath = FCKConfig.PluginsPath + 'FileIcon/fileicon.gif';

// 'FileIcon' is the name used in the Toolbar config.
FCKToolbarItems.RegisterItem('FileIcon', oFileIcon);

FCKConfig.FileIconPath = FCKConfig.PluginsPath + "FileIcon/icons/";
FCKConfig.FileIconImages = [ 
    'ai','avi','bmp','cs','dll','doc','exe','fla','gif','ico','html','jpg','js',
    'mdb','mp3','pdf','png','ppt','rdp','swf','txt','vsd','xls','xml','zip'
] ;

FCKConfig.FileIconColumns = 6 ;

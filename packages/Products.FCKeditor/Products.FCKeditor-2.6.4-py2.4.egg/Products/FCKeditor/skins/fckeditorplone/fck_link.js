var targetFieldId = 'uri';
var prefixURI = '';


function winBrowse(url, targetId, prefix)
{
  targetFieldId = targetId;
  prefixURI = prefix;
  top_win = (screen.height)/20 ;
  left_win = (screen.width)/20 ;
  agt = navigator.userAgent.toLowerCase();
  if (agt.indexOf('netscape') != -1 || agt.indexOf('gecko')!= -1) {
    win_h = parseInt(top.innerHeight*7/8) ;
    win_w = parseInt(top.innerWidth*4/5) ;
  }
  else {
    win_h = parseInt(document.body.clientHeight*7/8) ;
    win_w = parseInt(document.body.clientWidth*4/5) ;
  }
  stringwin = "width=" + win_w + ",height=" + win_h + ",top=" + top_win + ",left=" + left_win + ",alwaysRaised=yes,toolbar=no,scrollbars=no,resizable";
  inf = window.open(url,"inf",stringwin);
  inf.blur();
  inf.focus();
}

function SetUrl( url )
{
  var oField  = document.getElementById(targetFieldId);
  url = url.replace(/(.\/resolveuid)/g, '/resolveuid');
  if (oField) {
     oField.value = prefixURI + url ;
  }
}

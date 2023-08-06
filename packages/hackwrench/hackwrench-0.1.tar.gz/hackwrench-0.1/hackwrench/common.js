
/*if(!window.openTab){
    document.addEventListener("keydown", function(evt){
	    if(evt.which==116 || (evt.which==82 && evt.ctrlKey)){
		// ctrl+r or f5 to reload //114
		window.location.reload();
	    }
	    else if(evt.which==78 && evt.ctrlKey){
		// ctrl+n to open new window //110
		window.open('');
	    }
	    }, false);
}*/

window.openTab=function(url){
    console.log('__new_tab "'+url+'"');
}

// ctrl+click on middle click on link to open it in a new tab
var anchors = document.getElementsByTagName("a");
for(var i=0; i<anchors.length; i++){
    if(!anchors[i].click_patched){
	anchors[i].addEventListener("click", function(evt){
	    if(evt.button == 1 || (evt.button==0 && evt.ctrlKey)){
		window.openTab(this.href);
		evt.cancelBubble = evt.cancel = true;
		return evt.returnValue = false;
	  }
    }, false);
    anchors[i].click_patched=true;
   }
}
anchors=null;


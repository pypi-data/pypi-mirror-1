/************************************************************************************************************
(C) www.dhtmlgoodies.com, November 2005

Update log:

December 20th, 2005 : Version 1.1: Added support for rectangle indicating where object will be dropped
January 11th, 2006: Support for cloning, i.e. "copy & paste" items instead of "cut & paste"
January 18th, 2006: Allowing multiple instances to be dragged to same box(applies to "cloning mode")

This is a script from www.dhtmlgoodies.com. You will find this and a lot of other scripts at our website.	

	Terms of use:
You are free to use this script as long as the copyright message is kept intact. However, you may not
redistribute, sell or repost it without our permission.

Thank you!

www.dhtmlgoodies.com
Alf Magne Kalleland

************************************************************************************************************/
/************************************************************************************************************
May 29th, 2008 : Modified for PlateCom project.
************************************************************************************************************/

/* VARIABLES YOU COULD MODIFY */
var boxSizeArray = [4,4,4,3,7];	// Array indicating how many items there is rooom for in the right column ULs

var arrow_offsetX = -5;	// Offset X - position of small arrow
var arrow_offsetY = 0;	// Offset Y - position of small arrow

var arrow_offsetX_firefox = -6;	// Firefox - offset X small arrow
var arrow_offsetY_firefox = 6; // Firefox - offset Y small arrow

var verticalSpaceBetweenListItems = 3;	// Pixels space between one <li> and next	
										// Same value or higher as margin bottom in CSS for #dhtmlgoodies_dragDropContainer ul li,#dragContent li

										
var indicateDestionationByUseOfArrow = true;	// Display arrow to indicate where object will be dropped(false = use rectangle)

var cloneSourceItems = true;	// Items picked from main container will be cloned(i.e. "copy" instead of "cut").	
var cloneAllowDuplicates = false;	// Allow multiple instances of an item inside a small box(example: drag Student 1 to team A twice

/* END VARIABLES YOU COULD MODIFY */

var dragDropTopContainer = false;
var dragTimer = -1;
var dragContentObj = false;
var contentToBeDragged = false;	// Reference to dragged <li>
var contentToBeDragged_src = false;	// Reference to parent of <li> before drag started
var contentToBeDragged_next = false; 	// Reference to next sibling of <li> to be dragged
var destinationObj = false;	// Reference to <ul> or <li> where element is dropped.
var dragDropIndicator = false;	// Reference to small arrow indicating where items will be dropped
var ulPositionArray = new Array();
var mouseoverObj = false;	// Reference to highlighted DIV

var MSIE = navigator.userAgent.indexOf('MSIE')>=0?true:false;
var navigatorVersion = navigator.appVersion.replace(/.*?MSIE (\d\.\d).*/g,'$1')/1;

var expanded_terms = {};

var indicateDestinationBox = false;
function getTopPos(inputObj)
{		
  var returnValue = inputObj.offsetTop;
  while((inputObj = inputObj.offsetParent) != null){
	if(inputObj.tagName!='HTML')returnValue += inputObj.offsetTop;
  }
  return returnValue;
}

function getLeftPos(inputObj)
{
  var returnValue = inputObj.offsetLeft;
  while((inputObj = inputObj.offsetParent) != null){
	if(inputObj.tagName!='HTML')returnValue += inputObj.offsetLeft;
  }
  return returnValue;
}
	
function cancelEvent()
{
	return false;
}
function initDrag(e)	// Mouse button is pressed down on a li
{
	//debug_print("initDrag");

	if(document.all)e = event;
	var st = Math.max(document.body.scrollTop,document.documentElement.scrollTop);
	var sl = Math.max(document.body.scrollLeft,document.documentElement.scrollLeft);
	
	term = this.id.substring("dragimage_".length, this.id.length)
	contentToBeDragged = document.getElementById(term);
	contentToBeDragged_src = contentToBeDragged.parentNode;
	if(contentToBeDragged.parentNode.id == 'allItems') {
		//contentToBeDragged = copy(contentToBeDragged)
	}
	else {
		//cloneSourceItems = false;
	}
	//debug_print("contentToBeDragged.id: " + contentToBeDragged.id);
	//debug_print(" contentToBeDragged.left: " + getLeftPos(contentToBeDragged));

	dragTimer = 0;
	dragContentObj.style.left = e.clientX + sl + 'px';
	dragContentObj.style.top = e.clientY + st + 'px';
	//contentToBeDragged = document.getElementById(term);

	contentToBeDragged_next = false;
	if(contentToBeDragged.nextSibling){
		contentToBeDragged_next = contentToBeDragged.nextSibling;
		if(contentToBeDragged.tagName && contentToBeDragged_next.nextSibling)contentToBeDragged_next = contentToBeDragged_next.nextSibling;
	}
	timerDrag();
	return false;
}

var unique = 1;

function copy(e)
{
	var eId      = e;
	var copyE    = eId.cloneNode(true);
	var cLength  = copyE.childNodes.length -1;
	copyE.id     = remove_copy_sufix(e.id) + '-copy' + unique;

	for(var i = 0; cLength >= i;  i++)	{
		if(copyE.childNodes[i].id) {
			var cNode   = copyE.childNodes[i];
			var firstId = cNode.id;
			cNode.id    = remove_copy_sufix(firstId) + '-copy' + unique;
		}
	}
	unique++;
	return copyE;
}

function remove_copy_sufix(id)
{
	if(id.indexOf('-copy') >= 0)
		return id.substr(0, id.indexOf('-copy'));
	else
		return id;
}

function timerDrag()
{
	if(dragTimer>=0 && dragTimer<10){
		dragTimer++;
		setTimeout('timerDrag()',10);
		return;
	}
	if(dragTimer==10){
		
		if(cloneSourceItems && (contentToBeDragged.parentNode.id=='allItems' || contentToBeDragged.id.substr(0, 3) == 'all')){
			contentToBeDragged = copy(contentToBeDragged);
			/*newItem = contentToBeDragged.cloneNode(true);
			newItem.onmousedown = contentToBeDragged.onmousedown;
			contentToBeDragged = newItem;*/
		}
		dragContentObj.style.display='block';
		dragContentObj.appendChild(contentToBeDragged);
	}
}



function moveDragContent(e)
{
	if(dragTimer<10){
		if(contentToBeDragged && contentToBeDragged_src.id != 'allItems'){
			if(contentToBeDragged_next){
				contentToBeDragged_src.insertBefore(contentToBeDragged,contentToBeDragged_next);
			}else{
				contentToBeDragged_src.appendChild(contentToBeDragged);
			}	
		}
		return;
	}
	if(document.all)e = event;
	var st = Math.max(document.body.scrollTop,document.documentElement.scrollTop);
	var sl = Math.max(document.body.scrollLeft,document.documentElement.scrollLeft);
	
	
	dragContentObj.style.left = e.clientX + sl + 'px';
	dragContentObj.style.top = e.clientY + st + 'px';
	
	if(mouseoverObj)mouseoverObj.className='';
	destinationObj = false;
	dragDropIndicator.style.display='none';
	if(indicateDestinationBox)indicateDestinationBox.style.display='none';
	var x = e.clientX + sl;
	var y = e.clientY + st;
	var width = dragContentObj.offsetWidth;
	var height = dragContentObj.offsetHeight;
	
	var tmpOffsetX = arrow_offsetX;
	var tmpOffsetY = arrow_offsetY;
	if(!document.all){
		tmpOffsetX = arrow_offsetX_firefox;
		tmpOffsetY = arrow_offsetY_firefox;
	}

	for(var no=1;no<ulPositionArray.length;no++){ // excludes source box
		var ul_leftPos = ulPositionArray[no]['left'];	
		var ul_topPos = ulPositionArray[no]['top'];	
		var ul_height = ulPositionArray[no]['height'];
		var ul_width = ulPositionArray[no]['width'];
		
		if((x+width) > ul_leftPos && x<(ul_leftPos + ul_width) && (y+height)> ul_topPos && y<(ul_topPos + ul_height)){
			var noExisting = ulPositionArray[no]['obj'].getElementsByTagName('li').length;
			if(indicateDestinationBox && indicateDestinationBox.parentNode==ulPositionArray[no]['obj'])noExisting--;
			dragDropIndicator.style.left = ul_leftPos + tmpOffsetX + 'px';
			var subLi = ulPositionArray[no]['obj'].getElementsByTagName('li');
			
			var clonedItemAllreadyAdded = false;
			if(cloneSourceItems && !cloneAllowDuplicates){
				original_id_1 = remove_copy_sufix(contentToBeDragged.id);
				for(var liIndex=0;liIndex<subLi.length;liIndex++){
					original_id_2 = remove_copy_sufix(subLi[liIndex].id)
					if(original_id_1 == original_id_2)clonedItemAllreadyAdded = true;
				}
				if(clonedItemAllreadyAdded)continue;
			}
			
			for(var liIndex=subLi.length-1;liIndex>=0;liIndex--){
				var tmpLeft = getLeftPos(subLi[liIndex]);
				var tmpRight = getLeftPos(subLi[liIndex]) + subLi[liIndex].offsetWidth;
				var tmpTop = getTopPos(subLi[liIndex]);
				var tmpBottom = getTopPos(subLi[liIndex]) + subLi[liIndex].offsetHeight;
				if(!indicateDestionationByUseOfArrow){
					if(y>tmpTop && x>tmpLeft){
						destinationObj = subLi[liIndex];
						indicateDestinationBox.style.display='block';
						subLi[liIndex].parentNode.insertBefore(indicateDestinationBox,subLi[liIndex]);
						break;
					}
				}else{							
					if(tmpTop <= y && y <= tmpBottom && tmpLeft <= x && x <= tmpRight){

						/***********************************************************************/
						/*document.getElementById('debug').innerHTML =
								('liIndex: ' + liIndex) +
								(' x: ' + x) +
								(' y: ' + y);
						if(tmpLeft)
							document.getElementById('debug').innerHTML += ' tmpLeft: ' + tmpLeft;
						if(tmpTop)
							document.getElementById('debug').innerHTML += ' tmpTop: ' + tmpTop;*/
						/***********************************************************************/

						destinationObj = subLi[liIndex];
						dragDropIndicator.style.left = tmpLeft + tmpOffsetX + 'px';
						dragDropIndicator.style.top = tmpTop + tmpOffsetY + 'px';
						dragDropIndicator.style.display='block';
						break;
					}
				}					
				
				if(!indicateDestionationByUseOfArrow){
					if(indicateDestinationBox.style.display=='none'){
						indicateDestinationBox.style.display='block';
						ulPositionArray[no]['obj'].appendChild(indicateDestinationBox);
					}
					
				}else{
					// ultimo lugar (abajo de todo)
					if(subLi.length>0 && dragDropIndicator.style.display=='none'){
						dragDropIndicator.style.left = getLeftPos(subLi[subLi.length-1]) + subLi[subLi.length-1].offsetWidth + tmpOffsetX + 'px';
						dragDropIndicator.style.top = getTopPos(subLi[subLi.length-1]) + tmpOffsetY + 'px';
						dragDropIndicator.style.display='block';
					}
					if(subLi.length==0){
						dragDropIndicator.style.top = ul_topPos + arrow_offsetY + 'px'
						dragDropIndicator.style.display='block';
					}
				}
				
				if(!destinationObj)destinationObj = ulPositionArray[no]['obj'];
				mouseoverObj = ulPositionArray[no]['obj'].parentNode;
				mouseoverObj.className='mouseover';
				return;
			}
		}
	}
}

function debug_print(str)
{
	document.getElementById('debug').innerHTML += str + "<br>";
}

function debug_replace(str)
{
	document.getElementById('debug').innerHTML = str + "<br>";
}

/* End dragging 
Put <li> into a destination or back to where it came from.
*/	
function dragDropEnd(e)
{
	//debug_print("dragDropEnd");

	if(dragTimer==-1)return;
	if(dragTimer<10){
		dragTimer = -1;
		return;
	}
	dragTimer = -1;
	if(document.all)e = event;	
	if(cloneSourceItems && (!destinationObj || (destinationObj && (destinationObj.id=='allItems' || destinationObj.parentNode.id=='allItems')))){
		contentToBeDragged.parentNode.removeChild(contentToBeDragged);
	}else{	
		if(destinationObj){
			// drop all source elements
			if(contentToBeDragged.id.substr(0, 3) == 'all')
			{
				insert_all_elements_from_to(contentToBeDragged_src, destinationObj);
				contentToBeDragged.parentNode.removeChild(contentToBeDragged);
			}
			else
				insert_element_at(contentToBeDragged, destinationObj);

			mouseoverObj.className='';
			destinationObj = false;
			dragDropIndicator.style.display='none';
			if(indicateDestinationBox){
				indicateDestinationBox.style.display='none';
				document.body.appendChild(indicateDestinationBox);
			}
			contentToBeDragged = false;
			initDragDropScript()
			return;
		}		
		if(contentToBeDragged_next){
			contentToBeDragged_src.insertBefore(contentToBeDragged,contentToBeDragged_next);
		}else{
			contentToBeDragged_src.appendChild(contentToBeDragged);
		}
	}
	contentToBeDragged = false;
	dragDropIndicator.style.display='none';
	if(indicateDestinationBox){
		indicateDestinationBox.style.display='none';
		document.body.appendChild(indicateDestinationBox);
		
	}
	mouseoverObj = false;
	initDragDropScript()
}

function insert_all_elements_from_to(sourceObj, destinationObj)
{
	var lis = sourceObj.getElementsByTagName('li');
	var lis_copy = Array(lis.length);
	for(var no=0;no<lis.length;no++)
		lis_copy[no] = lis[no];
	for(var no=0;no<lis_copy.length;no++){
		li = lis_copy[no];
		if(li.id.substr(0, 3) != 'all' && !is_item_in(li, destinationObj)) {
			if(sourceObj.id == 'allItems')
				insert_element_at(copy(li), destinationObj);
			else
				insert_element_at(li, destinationObj);
		}
	}
}

function is_item_in(li, destinationObj)
{
	subLi = destinationObj.getElementsByTagName('li');
	original_id_1 = remove_copy_sufix(li.id)
	item_exists = false;
	for(var liIndex=0;liIndex<subLi.length;liIndex++){
		original_id_2 = remove_copy_sufix(subLi[liIndex].id)
		if(original_id_1 == original_id_2)item_exists = true;
	}
	return item_exists;
}

function insert_element_at(contentToBeDragged, destinationObj)
{
	if(destinationObj.tagName.toLowerCase()=='ul')
		destinationObj.appendChild(contentToBeDragged);
	else
		destinationObj.parentNode.insertBefore(contentToBeDragged, destinationObj);
}


/* 
Preparing data to be saved 
*/
function saveDragDropNodes()
{
	var saveString = "";
	var uls = dragDropTopContainer.getElementsByTagName('ul');
	for(var no=0;no<uls.length;no++){	// LOoping through all <ul>
		var lis = uls[no].getElementsByTagName('li');
		for(var no2=0;no2<lis.length;no2++){
			if(saveString.length>0)saveString = saveString + ";";
			saveString = saveString + uls[no].id + '|' + lis[no2].id;
		}	
	}		
	document.getElementById('conceptsRelations').value = saveString;
	//document.getElementById('saveContent').innerHTML = 'Ready to save these nodes: ' + saveString.replace(/;/g,';<br>') + 'Format: ID of ul |(pipe) ID of li;(semicolon)<br>You can put these values into a hidden form fields, post it to the server and explode the submitted value there';
}

function initDragDropScript()
{
	//debug_print("initDragDropScript");

	dragContentObj = document.getElementById('dragContent');
	dragDropIndicator = document.getElementById('dragDropIndicator');
	dragDropTopContainer = document.getElementById('dhtmlgoodies_dragDropContainer');
	document.documentElement.onselectstart = cancelEvent;;
	var listItems = dragDropTopContainer.getElementsByTagName('li');	// Get array containing all <li>
	var itemHeight = false;
	//debug_print("listitems: " + listItems.length);
	for(var no=0;no<listItems.length;no++){
		term = listItems[no].id
		if(!itemHeight)itemHeight = listItems[no].offsetHeight;

		dragimage = document.getElementById('dragimage_' + term)
		dragimage.onmousedown = initDrag;
		dragimage.onselectstart = cancelEvent;
		if(MSIE && navigatorVersion/1<6){
			dragimage.style.cursor='hand';
		}
	}

	var mainContainer = document.getElementById('dhtmlgoodies_mainContainer');
	var uls = mainContainer.getElementsByTagName('ul');
	itemHeight = itemHeight + verticalSpaceBetweenListItems;
	/*for(var no=0;no<uls.length;no++){
		uls[no].style.height = itemHeight * boxSizeArray[no]  + 'px';
	}*/
	
	var leftContainer = document.getElementById('dhtmlgoodies_listOfItems');
	var itemBox = leftContainer.getElementsByTagName('ul')[0];
	
	document.documentElement.onmousemove = moveDragContent;	// Mouse move event - moving draggable div
	document.documentElement.onmouseup = dragDropEnd;	// Mouse move event - moving draggable div
	
	var ulArray = dragDropTopContainer.getElementsByTagName('ul');
	for(var no=0;no<ulArray.length;no++){
		ulPositionArray[no] = new Array();
		ulPositionArray[no]['left'] = getLeftPos(ulArray[no]);	
		ulPositionArray[no]['top'] = getTopPos(ulArray[no]);	
		ulPositionArray[no]['width'] = ulArray[no].offsetWidth;
		ulPositionArray[no]['height'] = ulArray[no].clientHeight;
		ulPositionArray[no]['obj'] = ulArray[no];
	}
	
	if(!indicateDestionationByUseOfArrow){
		indicateDestinationBox = document.createElement('li');
		indicateDestinationBox.id = 'indicateDestination';
		indicateDestinationBox.style.display='none';
		document.body.appendChild(indicateDestinationBox);
	}

	saveDragDropNodes();
}

function view_concept(term)
{
	if(!expanded_terms[term]) {
		expanded_terms[term] = true;
		document.getElementById('dhtmlgoodies_mainContainer').innerHTML +=
			"\n\t\t\t\t<div>\n\t\t\t\t\t<p>" + term + "" +"\n\t\t\t\t\t<ul id=\"box1\">\n\t\t\t\t\t" + "\n\t\t\t\t" + ""
		initDragDropScript()
	}
}

function timerInit() {
	initDragDropScript()
	setTimeout('timerInit()', 100);
}

window.onload = timerInit;

// KSS client actions
/*kukit.more_selectors = {};
kukit.more_selectors.AfterConceptOpenedEventBinder = function() {
	debug_print("binding 3...")
};
kukit.more_selectors.AfterConceptOpenedEventBinder.prototype.__bind_initDragDropScriptEvent__ = function(name, func_to_bind, oper) {
    // validate and set parameters
    oper.completeParms([], {'count': '3'}, 'AfterConceptOpenedEventBinder event binding');
    oper.evalInt('count', 'AfterConceptOpenedEventBinder event binding');
    if (oper.parms.count < 1)
        throw 'Parameter count must be > 0, "' + oper.parms.count + '"';
    // overwrite countsomuch
    this.countsomuch = oper.parms.count;
    this.count = this.countsomuch;
    // Just bind the event via the native event binder
    oper.parms = {};

	debug_print("binding 1...")

    kukit.pl.NativeEventBinder.__bind__('initDragDropScriptEvent', func_to_bind, oper);
};
kukit.more_selectors.AfterConceptOpenedEventBinder.prototype.__default_initDragDropScriptEvent__ = function(oper) {
	oper.completeParms([], {}, 'AfterConceptOpenedEventBinder event');

	debug_print("binding 2...")

    this.__trigger_event__('initDragDropScriptEvent', {}, oper.node);
};
kukit.er.eventRegistry.register(null, 'initDragDropScriptEvent', kukit.more_selectors.AfterConceptOpenedEventBinder, null, null);*/
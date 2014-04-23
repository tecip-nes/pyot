
$("#hoststable").flexigrid({
	url: '/hostsList',
	method: 'GET',
	dataType: 'json',
	colModel : [
	    {display: 'Id', name : 'id', width : 48, sortable : false, align: 'left'}, 
	    {display: 'IP', name : 'ip6address', width : 180, sortable : false, align: 'left'},
	    {display: 'Time Added', name : 'timeadded', width : 150, sortable : false, align: 'left'},        
	    {display: 'Last Seen', name : 'lastSeen', width : 150, sortable : false, align: 'left'},
		],
	buttons : [
		   		{name: 'Details', bclass: 'delete', onpress : act},
		   		{name: 'Select All', bclass: 'delete', onpress : act},
		   		{name: 'DeSelect All', bclass: 'delete', onpress : act},
		   		{separator: true}
		   		],	
	sortname: "timeadded",
	sortorder: "desc",
	usepager: true,
	useRp: true,
	rp: 15,
	showTableToggleBtn: true,
	width: 650,
	onSubmit: addFormData,
	height: 250
});

//This function adds paramaters to the post of flexigrid. You can add a verification as well by return to false if you don't want flexigrid to submit			
function addFormData(){
	//passing a form object to serializeArray will get the valid data from all the objects, but, if the you pass a non-form object, you have to specify the input elements that the data will come from
	var dt = $('#sform').serializeArray();
	$("#hoststable").flexOptions({params: dt});
	return true;
}


$('#sform').submit(function (){
	$('#hoststable').flexOptions({newp: 1}).flexReload();
	return false;
});

function reloadTable(){
    $('#hoststable').flexReload();
    setTimeout("reloadTable()",5000);
}


reloadTable();

function makeList(grid){
    var items = $('.trSelected',grid);
    var itemlist ='';
    for(i=0;i<items.length-1;i++){
        itemlist+= items[i].id.substring(3)+",";
    }
    itemlist+= items[i].id.substring(3);
    return itemlist;
}

function opSelection(com, itemList){
	if (com == 'Details') {
		var Url = "/resources";
	}
	window.location.href = Url+'?'+"id=" + itemList;
	}

function act(com, grid){
    if (com == 'Select All')
    {
        $('.bDiv tbody tr',grid).addClass('trSelected');
    }

    if (com == 'DeSelect All')
    {
        $('.bDiv tbody tr',grid).removeClass('trSelected');
    }
	if (com == 'Details') {
		if($('.trSelected',grid).length>0){
                 var itemlist = makeList(grid);
                 opSelection(com, itemlist);
         } else {
             return false;
         } 
	} 
}


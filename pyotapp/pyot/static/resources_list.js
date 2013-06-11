

if (hostid != ''){
	$("#resourcetable").flexigrid({
		url: '/resourceList',
		method: 'GET',
		dataType: 'json',
		colModel : [
		            {display: 'Id', name : 'id', width : 40, sortable : false, align: 'left'}, 
		            {display: 'Uri', name : 'timeadded', width : 200, sortable : false, align: 'left'},
		            {display: 'Host', name : 'response', width : 180, sortable : false, align: 'left'},
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
}

//This function adds paramaters to the post of flexigrid. You can add a verification as well by return to false if you don't want flexigrid to submit			
function addFormData(){
	//passing a form object to serializeArray will get the valid data from all the objects, but, if the you pass a non-form object, you have to specify the input elements that the data will come from
	var dt = $('#sform').serializeArray();
	
	if (hostid != ''){
		$('#resourcetable').flexOptions({query: hostid, qtype: 'id'});
	}
	return true;
}


$('#sform').submit(function (){
	$('#resourcetable').flexOptions({newp: 1}).flexReload();
	return false;
});

function reloadTable(){
	$('#resourcetable').flexReload();	
}

$(document).ready(function() {
    var source = new EventSource('/pushUpdate/Host');

    source.addEventListener("pushUpdate", function(e) {
        if (e.data == 'T')
                reloadTable();
    });
});

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
	
//	$.ajax({
//		type: "GET",
//		url: Url,
//		data: "id=" + itemList,
//		success: function(msg){
//		setFeedback(msg);
//	}
//	});	
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

function gotoRes(id){
	var Url = "/resource/"+id;
	window.location.href = Url;
}

/*
$("#lista").smartupdater({
	url : "{% url filelist %}"
	}, function (data) {
		document.getElementById("lista").innerHTML=data;
	}
);
$("#lista").smartupdater("setTimeout",{{ refresh_js }});
 */



function setFeedback(msg){
	$("#feedback").html(msg);
}

function startCoap(id){
	
    $.ajax({
          type: "GET",
          url: "/startServer/"+id,
          success: function(msg){
                     setFeedback(msg);
                   }
     });
}

function stopCoap(id){
	
    $.ajax({
          type: "GET",
          url: "/stopServer/"+id,
          success: function(msg){
                     setFeedback(msg);
                   }
     });
}

function shutdown(){
	$.ajax({
		type: "GET",
		url: "/shutdown",
		success: function(msg){
		}
	});	
}

$("#workers").flexigrid({
	url: '/getServerStatus',
	method: 'GET',
	dataType: 'json',
	colModel : [
	    {display: 'Name', name : 'name', width : 48, sortable : false, align: 'left'}, 
	    {display: 'Prefix', name : 'prefix', width : 50, sortable : false, align: 'left'},
	    {display: 'Start/Stop', name : 'startstop', width : 150, sortable : false, align: 'left'},        
	    {display: 'Worker Status', name : 'wstatus', width : 150, sortable : false, align: 'left'},
	    {display: 'RD Server Status', name : 'rstatus', width : 150, sortable : false, align: 'left'},
		],
	sortname: "name",
	sortorder: "desc",
	width: 650,
	//onSubmit: addFormData,
	height: 250
});




function reloadTable(){
	console.log("updating ");
    $('#workers').flexReload();
    setTimeout("reloadTable()",5000);
}

reloadTable();
/*
$(document).ready(function() {
    var source = new EventSource('/getServerStatus');
    //var events_dom = $("#workers");

    source.addEventListener("serverStatus", function(e) {
    	obj = JSON.parse(e.data);
    	console.log("updating " + obj);
    	$("#workers").flexAddData(eval(obj));
    	
    	//alert(obj.count);
      	
         //events_dom.html(h);
    });
});*/

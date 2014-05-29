
function setFeedback(msg){
	$("#feedback").html(msg);
}

function startCoap(){
	
    $.ajax({
          type: "GET",
          url: "/startServer",
          success: function(msg){
                     setFeedback(msg);
                   }
     });
}

function stopCoap(){
	
    $.ajax({
          type: "GET",
          url: "/stopServer",
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


$(document).ready(function() {
    var source = new EventSource('/getServerStatus');
    var events_dom = $("#feedback");

    source.addEventListener("serverStatus", function(e) {
         events_dom.html("<div>" + e.data + "</div>");
    });
});

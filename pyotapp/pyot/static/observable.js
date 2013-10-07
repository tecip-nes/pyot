
function obs(id){
	var duration = document.getElementById('duration').value;
	var handler = document.getElementById('handler').value;
	var ren = document.getElementById('renew').checked;	
	$.ajax({
		type: "GET",
		url: "/observe",
		data: "id=" + id + "&duration=" + duration +"&handler=" + handler +"&renew=" + ren,
		success: function(msg){
		setFeedback(msg);
	}
	});
}

var options = {
		lines: { show: true },
		points: { show: true },
};



var placeholder = $("#placeholder");

function setOpacity(value) {
	document.getElementById('placeholder').style.opacity = value/10;
	document.getElementById('placeholder').style.filter = 'alpha(opacity=' + value*10 + ')';
}


$(document).ready(function() {
    var arr = [];
    var t=0;
    document.getElementById('feedback').value = '';
    var source = new EventSource('/obsLast/'+rid+'/');
    
    source.addEventListener("obsLast", function(e) {
    		if (e.data =='none'){
			setOpacity(5);
			return;
		}
    		setOpacity(10);
		arr.push(([t , parseInt(e.data)]));	
		t++;

		$.plot(placeholder,[{
			label: "Data",
			data: arr,
			lines: { show: true }
		}],
		{
			yaxis: {
			min: 0
		}
		}
		);
    });
});




$("#subList").smartupdater({
	url : '/subList/'+rid+'/'}, function (data) {
	document.getElementById("subList").innerHTML=data;});

$("#subList").smartupdater("setTimeout", 1000);





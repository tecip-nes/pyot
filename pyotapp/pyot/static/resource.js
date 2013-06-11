
function setFeedback(msg){
	var separator = '****************\n';
        d = new Date();
        date = d.getHours().toString() + '.'+d.getMinutes().toString() +  '.'+ d.getSeconds().toString() + ': ';
	document.getElementById('feedback').value = date + msg + '\n' + separator + document.getElementById('feedback').value;
}


function req(op, id){
	
	payload = document.getElementById('payload').value;
    $.ajax({
          type: "GET",
          url: "/opRes",
          data: "op=" + op +"&id=" + id +'&pd=' + payload,
          success: function(msg){
                     setFeedback(msg);
                   }
     });
}



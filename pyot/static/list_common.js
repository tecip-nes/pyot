
function setFeedback(msg){
	var separator = '****************\n';
        d = new Date(hours, minutes, seconds);
        date = d.toUTCString();
	document.getElementById('feedback').value = date + msg + '\n' + separator + document.getElementById('feedback').value;
}

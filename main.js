var text_area;
var text_data;

window.onload = function(){
    text_area = document.getElementById('sendText');
    text_data = text_area.value;
    setInterval(reload, 2000);
}

function reload(){
    if (!(document.getElementById('sendText').value == text_data)){
        text_data = text_area.value;
        console.log("change");
        console.log(this.text_data);
    }
  } 

function onLoad() {
    var navig = document.getElementById("navigation");
        
    var paths = window.location.pathname.split("/");
    var html = new Array();
    var links = new Array();
                
    for(var i=0; i<paths.length-1; i++) {
        links.push(paths[i]);
        html.push('<a href="' + links.join('/') + '/">' + paths[i] + '</a>');
    }
    navig.innerHTML = html.join('/');
}

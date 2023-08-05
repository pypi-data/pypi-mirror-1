/* handles the query submission and result handling */

/* this is taken from an apple developer connection article:
http://developer.apple.com/internet/webcontent/xmlhttpreq.html */

var queryservice = "http://" + window.location.hostname + ":" + window.location.port + "/query/query";
var sparql;
var popupmsg;

function Query(service) {
    var service = service;
    
    function init() {
        var req;
    // branch for native XMLHttpRequest object
        if(window.XMLHttpRequest && !(window.ActiveXObject)) {
            try {
                req = new XMLHttpRequest();
            } catch(e) {
                req = false;
            }
        // branch for IE/Windows ActiveX version
        } else if(window.ActiveXObject) {
            try {
                req = new ActiveXObject("Msxml2.XMLHTTP");
            } catch(e) {
                try {
                    req = new ActiveXObject("Microsoft.XMLHTTP");
                } catch(e) {
                	req = false;
                }
    	    }
        }    
        
        return req;
    }

    function queryReqChange(req, successCb, errorCb) {
        // only if req shows "loaded"
        if (req.readyState == 4) {
            popupmsg.style.display = "none";
            
            // only if "OK"
            if (req.status == 200) {
                // ...processing statements go here...
                if(successCb)
                    // The success callback handles a Javascript object
                    // with the sparql result data structure
                    successCb(eval('(' + req.responseText + ')'));
            } else {
                if(errorCb)
                    errorCb(req.statusText, req.responseText);
            }
        }
    }
    
    this.query = function(query, successCb, errorCb) {
        // initialize a new request object
        var req = init();
        
        if(req) {
            query = query.replace(/[' ']+/g, "+");
            query = escape(query);    
        
            req.onreadystatechange = function() {
                queryReqChange(req, successCb, errorCb);
            };
            
            popupmsg.style.display = "block";
            
            req.open("GET", service + '?query=' + query + '&format=json', true);
            req.setRequestHeader('ACCEPT', 'application/sparql-results+json');
            req.send("");
    	}
    }
}

function sparqlResultHTML(sparqlResults) {
    var domnode = document.getElementById('results');

    // remove any existing result trees
    while(domnode.childNodes.length > 0) {
        domnode.removeChild(domnode.childNodes[0]);
    }
    
    table = document.createElement("table");
    tablehead = document.createElement("thead");
    tablebody = document.createElement("tbody");
    
    headvars = sparqlResults.head.vars;

    domnode.appendChild(table);

    table.appendChild(tablehead);
    table.appendChild(tablebody);
            
    tr = document.createElement("tr");

    tablehead.appendChild(tr);    
    
    for(i=0; i<headvars.length; i++) {
        th = document.createElement("th");
        tr.appendChild(th);
        th.appendChild(document.createTextNode(headvars[i]));
    }
    
    bindings = sparqlResults.results.bindings;
    
    for(i=0; i<bindings.length; i++) {
        tr = document.createElement("tr");
        tablebody.appendChild(tr);
        
        if(i%2 == 0) {
            tr.setAttribute('class', 'even');
        } else {
            tr.setAttribute('class', 'odd');
        }
        
        for(j=0; j<headvars.length; j++) {
            td = document.createElement("td");
            tr.appendChild(td);

            try {
                var value = bindings[i][headvars[j]].value;
            } catch (e) {
                td.appendChild(document.createTextNode(''));
                value = ''
            } finally {
               td.appendChild(document.createTextNode(value));
            }

        }
        
/*        for(j=0; j<bindings[i].length; j++) {
            td = document.createElement("td");
            tr.appendChild(td);
            
            td.appendChild(document.createTextNode(bindings));
        }
*/        
    }
}

function sparqlError(status, msg) {
    var errorNode = document.getElementById('errormsg');

    if(errorNode.childNodes.length > 1) {
        errorNode.removeChild(errorNode.childNodes[1]);
    }
    
    errorNode.appendChild(document.createTextNode(msg));
}

function addQueryLinks(query) {
    var linkNode = document.getElementById('resultlinks');

    while(linkNode.childNodes.length > 0) {
        linkNode.removeChild(linkNode.childNodes[0]);
    }

    if(!query)
        return
    
    a = document.createElement('a');
    a.setAttribute('href', query + '&format=xml');
    a.appendChild(document.createTextNode('xml'));    
    linkNode.appendChild(a);
    linkNode.appendChild(document.createTextNode(', '));
    a = document.createElement('a');
    a.setAttribute('href', query + '&format=json');
    a.appendChild(document.createTextNode('json'));    
    linkNode.appendChild(a);
}

function executeQuery(form) {
    var query = form.query.value;
    
    // clears any previous sparql error messages
    sparqlError('','');
    var querylink = query.split(' ').join('+');    
    querylink = escape(querylink);
    link = queryservice + '?query=' + querylink
    addQueryLinks(link);
    //getResults(queryservice + '?query=' + query + '&format=json');
    
    sparql.query(query, sparqlResultHTML, sparqlError);
}

/* popup message showing that a query is executing */
function popupMessageInit() {
    var globaldoc = document.getElementById("container");
    var container = document.createElement("div");
    var content = document.createElement("div");
    
    globaldoc.appendChild(container);
    
    container.appendChild(content);
    container.style.display = "none";
    container.style.position = "relative";    
    container.style.border = "1px dotted #369"; 
    container.style.margin = "50px auto";
    container.style.background = "#def";
    container.style.width = "250px";
    container.style.height = "150px";
    
    content.style.position = "absolute";
    container.style.margin = "0px auto";
    content.innerHTML = "Query executing...";
    
    return container;
}

function init() {
    sparql = new Query(queryservice);
    popupmsg = popupMessageInit();
}

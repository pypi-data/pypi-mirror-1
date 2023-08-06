var current_index = null;

var handleIndexClick = function(index) {
  $('#sparql_form').attr('action', '/query/' + this.name);

  $("#index_list > a[@name=" + this.name + "]").removeClass("link");
  $("#index_list > a[@name=" + this.name + "]").addClass("index_link_selected");  

  $("#index_list > a[@name=" + current_index + "]").removeClass("index_link_selected");
  $("#index_list > a[@name=" + current_index + "]").addClass("link");

  current_index = this.name;
}

var showIndices = function(indices) {
  var html = '';
  for(i in indices) {
    index_name = indices[i];
    html = '<a href="#" class="link" id="index_link" name="' + index_name + '">' + index_name + '</a>';
      
    if(i != indices.length-1)
        html += ' | '
        
    $("#index_list").append(html)
  }

  if(current_index == null) {
    $("#index_list > a[@name=query]").removeClass("link");
    $("#index_list > a[@name=query]").addClass("index_link_selected");
    current_index = "query";
  }
  
  $("#index_list > a").click(handleIndexClick);  
}

var processSPARQLResults = function(results) {
  // clean out results table and any lingering error message
  $("#errormsg").empty();
  $("#query_activity").empty();
  $("#results_table").empty();
  
  headvars = results.head.vars;
  bindings = results.results.bindings;

  html = '<thead><tr>';
  for(i in headvars) {
    html += '<th>' + headvars[i] + '</th>';
  }
  html += '</tr></thead><tbody>';
  
  for(i in bindings) {
    html += '<tr>';
    //alert(bindings[i]);
    for(j in headvars) {
        try {
            var value = bindings[i][headvars[j]].value;
        } catch (e) {
            value = ''
        } finally {
            html += '<td>' + value + '</td>';
        }
    }
    html += '</tr>'
//    $("#results_table").append(html);

  }
  
  html += '</tbody>';
  $("#results_table").append(html);
  
  $("#results_table").tablesorter({widgets: ['zebra']});  
}

// tell the server what type of content we except to get back
// start the animation for query status
var modifyRequest = function(XMLHttpRequest) { 
    XMLHttpRequest.setRequestHeader('Accept', 'application/json, text/javascript, application/sparql-results+json, text/plain')
	 html = "<img src=../static/img/busy.gif>";
    $("#query_activity").append(html);
    return true; 
}

var queryError = function(XMLHttpRequest, textStatus, errorThrown) {
    $("#errormsg").empty();
    $("#query_activity").empty();
    $("#errormsg").append(XMLHttpRequest.responseText);
}

$(document).ready(function() {
  
  $.getJSON('../system/indices/', 
      function(data){
          showIndices(data);
      });

  var options = { 
        // dataType identifies the expected content type of the server response 
    dataType:  'json',
    beforeSend: modifyRequest,
    error: queryError,
        // success identifies the function to invoke when the server response 
        // has been received 
    success:   processSPARQLResults,
    target:     '#query_result'
  };
  
  // bind form using ajaxForm
  $('#sparql_form').ajaxForm(options); 

});

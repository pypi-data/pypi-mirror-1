
$(document).ajaxError(function(){
    if (window.console && window.console.error) {
        console.error(arguments);
    }
});

var showGraphs = function(graphs) {
  $("#graphs").empty();

  for(i in graphs) {
    graph_uri = graphs[i]

    if(graph_uri[0] == '/')
        graph_uri = graph_uri.slice(1);
    
    var html = '<a href="' + graph_uri + '" >' + graphs[i] + 
'</a> (<a href="http://dataviewer.zitgist.com/?uri=' + 
encodeURIComponent(document.location.href + graph_uri) + 
'">Zitgist</a>)<br/>';
    $("#graphs").append(html); }
};


var showCollections = function(collections) {

  $("#collections").empty();
  
  for(i in collections) {
    var html = '<a href="#" id="#collection_link" name="' + collections[i] + '">' + collections[i] + '</a><br/>'
    $("#collections").append(html)
  }

  $("#collections > a").click(handleCollectionClick);
};

var showNavigation = function(collection) {
  $("#navigation").empty();
  
  var paths = collection.split("/");
  var links = new Array();
  
  $("#navigation").append('/<a href="#" id="#collection_link" name="/">root</a>');
  
  for(var i=0; i<paths.length-1; i++) {
    links.push(paths[i]);
    $("#navigation").append('/<a href="#" id="#collection_link" name="' + links.join('/') + '">' + paths[i] + '</a>');
  }

  $("#navigation > a").click(handleCollectionClick);  
}

var handleCollectionClick = function() {
  collectionRetrieve(this.name);
}

var collectionRetrieve = function(collection) {

  // make sure that a collection doesnt start with / for the join
  if (collection[0] == '/')
    collection = collection.slice(1);
  
  // make sure that the collection ends with / for request
  if (collection != '' && collection[collection.length-1] != '/')
    collection += '/';
    
  $.getJSON('system/collections/' + collection, 
      function(data){
          showNavigation(collection);
          showGraphs(data.graphs);
          showCollections(data.collections);
      });
};

 $(document).ready(function() {
    collectionRetrieve('/');
 })

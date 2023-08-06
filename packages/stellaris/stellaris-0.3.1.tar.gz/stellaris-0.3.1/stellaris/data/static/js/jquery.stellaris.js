/*
Stellaris protocol implementation in JavaScript
 */
(function($) {
	 $.stellaris = $.stellaris || {};

	 $.stellaris.Options = {
		  service: "http://localhost/"
	 };

	 $.stellaris.init = function(options) {
		  var options = $.extend({}, $.stellaris.Options, options);
		  $.stellaris.Options = options;
	 };

	 $.stellaris.query = function(query, callback) {		  
		  //		  var options = $.extend(options, $.stellaris.Options)
		  var query = query;
		  var options = $.extend({}, $.stellaris.Options);
		  $.ajax({url: options.service + "query/query", 
					 type: "POST",
						  dataType: "json",
						  data: {query: query, format: "json"}, 
						  success: callback,
						  error: function(req, errstr, exc) { alert(errstr); }
				});

	 };


	 
	 $.stellaris.create = function(graph_name, content, callback) {		  
		  //		  var options = $.extend(options, $.stellaris.Options)
		  var options = $.extend({}, $.stellaris.Options);
		  $.ajax({url: options.service,
						  type: "POST",
						  data: content,
						  contentType: "application/rdf+xml",
						  processData: false,
						  success: callback,
						  error: function(req, errstr, exc) { alert("Error creating page: " + errstr); },
						  beforeSend: function(xhr) {xhr.setRequestHeader("Slug", graph_name);}
				});

	 };

	 $.stellaris.replace_or_create = function(graph_name, content, callback) {		  
		  //		  var options = $.extend(options, $.stellaris.Options)
		  var options = $.extend({}, $.stellaris.Options);
		  $.ajax({url: options.service + graph_name + "?modification=replace",
						  type: "PUT",
						  data: content,
						  contentType: "application/rdf+xml",
						  processData: false,
						  success: callback,
						  error: function(req, errstr, exc) { $.stellaris.create(graph_name, content, callback) },
				});

	 };
	 
})(jQuery);
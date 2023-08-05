	
	function error(message) {
		var console = window.open("",'console',"width="+400+",height="+400+",status=yes,dependent=yes,resizable=yes,scrollbars=yes");
		console.document.write(message);
		console.document.close();
	}
	

	/*
		receives javascript from the given url + args and evaluates it
	*/
	function runRemoteJS(url, args) {
		doCall(url, function (x) {eval(x);}, args);
	}
	
	function doCall(url, wrapper, args) {
		var req = openConnection();
		if (url.indexOf('?') == -1) {
			url = url + "?";
		}
		for (var key in args) { 
		    if (key=='_mjax_named') {
		        for (var k in args[key]) {
    			    url = url + '&' + escape(k) + "=" + escape(args[key][k] || '');
			    }
		    }
		    else {
    			url = url + '&' + escape(key) + "=" + escape(args[key] || '');
		    }
		}

		url = url + "&_rnd=" + new Date().getTime()

		req.open("GET", url);

		req.onreadystatechange = function () {
			if (req.readyState != 4) {
				return;
			}
			
			//var s = getResponse();
			var s = req.responseText;
			if (s) {
				try {
					wrapper(s);
				}
				catch (e) {
					error(e + "<br/><br/>\n\nArgument:\n<br/>" + s);
				}
			}

		}
		req.send(null);
		delete req;
		
	}

		
	function openConnection () {
		var conn = null;
		try {
			conn = new ActiveXObject("Msxml2.XMLHTTP");
		} 
		catch (e) {
			try {
				conn = new ActiveXObject("Microsoft.XMLHTTP");
			} 
			catch (oc) { }
		}
		if(!conn && typeof XMLHttpRequest != "undefined") {
			conn = new XMLHttpRequest();	
		}
		
		if (!conn) {
			error("XMLHttp connection object not defined on this browser");
		}
		return conn;
	}	



	/*
		given the id of a document element, a url, and argument hash, populates the given document
		element with the results of the url + args
	*/
	function populateDOM(id, url, args) {
		doCall(url, function (x) {
			var elem = document.getElementById(id);
			if (elem) {
				elem.innerHTML = x;
			}
			else {
				error("No such element '" + id + "'");
			}
		},
		args);
	}
	
	function writeDOM(id, string) {
		var elem = document.getElementById(id);
		if (elem) {
			elem.innerHTML = string;
		}
	}
	
		

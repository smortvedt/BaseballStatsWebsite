const myHeading = document.querySelector('h1');
myHeading.textContent = 'Hello world!';

function teamDropdownShow() {
  document.getElementById("teamDropdown").classList.toggle("show");
}

function yearDropdownShow() {
  document.getElementById("yearDropdown").classList.toggle("show");
}

function updateTeamDropdown(teamId) {
  document.querySelector('#teamDropdownBtn').textContent = teamId;
}

function updateYearDropdown(yearId) {
  document.querySelector('#yearDropdownBtn').textContent = yearId;
}

function getStatsOnClick() {
  var team = document.getElementById('teamDropdownBtn').textContent;
  var year = document.getElementById('yearDropdownBtn').textContent;
  if (!(team=="Select Team" || year == "Select Year")){
    var query = "?teamid="+team+"&yearid="+year
    getStatsQuery(query)
  }
}

function getStatsQuery(query){
  var path = "http://127.0.0.1:5000/api/roster"
  var client = new HttpClient();
  client.get(path+query, function(response) {
      document.querySelector('#stats').textContent = response;
      return
  });
}

window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

var HttpClient = function() {
    this.get = function(aUrl, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        if ("withCredentials" in anHttpRequest) {
          // Check if the XMLHttpRequest object has a "withCredentials" property.
          // "withCredentials" only exists on XMLHTTPRequest2 objects.
          anHttpRequest.withCredentials=false;
          anHttpRequest.open("GET", aUrl);
        } else if (typeof XDomainRequest != "undefined") {
          // Otherwise, check if XDomainRequest.
          // XDomainRequest only exists in IE, and is IE's way of making CORS requests.
          anHttpRequest = new XDomainRequest();
          anHttpRequest.open("GET", aUrl);
        }
        
        anHttpRequest.onreadystatechange = function() {
            if (anHttpRequest.readyState == 4 && anHttpRequest.status == 200){
                aCallback(anHttpRequest.responseText);
            }
        }

        // anHttpRequest.open( "GET", aUrl );
        anHttpRequest.send( null );
    }
}

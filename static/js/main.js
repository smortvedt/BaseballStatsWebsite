var teamAndYearBool = false
var careerBool = false
var allTimeBool = false

function teamDropdownShow() {
  document.getElementById("teamDropdown").classList.toggle("show");
}

function yearDropdownShow() {
  document.getElementById("yearDropdown").classList.toggle("show");
}

function allTimeDropdownShow() {
  document.getElementById("allTimeDropdown").classList.toggle("show");
}

function updateTeamDropdown(teamId) {
  document.querySelector('#teamDropdownBtn').textContent = teamId;
}

function updateYearDropdown(yearId) {
  document.querySelector('#yearDropdownBtn').textContent = yearId;
}

function updateAllTimeDropdown(stat) {
  document.querySelector('#allTimeDropdownBtn').textContent = stat;
}

function careerStatsButtonClick(){
  careerBool=true
  allTimeBool=false
  teamAndYearBool=false
  hideTeamYearButtons()
  showCareerStatsNameInputs()
  document.getElementById("allTimeDropdownBtn").style.display="none"
}

function allTimeButtonClick(){
  careerBool=false
  allTimeBool=true
  teamAndYearBool=false
  hideTeamYearButtons()
  hideCareerStatsNameInputs()
  document.getElementById("allTimeDropdownBtn").style.display="block"
}

function teamAndYearButtonClick(){
  careerBool=false
  allTimeBool=false
  teamAndYearBool=true
  showTeamYearButtons()
  hideCareerStatsNameInputs()
  document.getElementById("allTimeDropdownBtn").style.display="none"
}

function showTeamYearButtons(){
  document.getElementById("teamDropdownBtn").style.display="block"
  document.getElementById("yearDropdownBtn").style.display="block"
}

function hideTeamYearButtons(){
  document.getElementById("teamDropdownBtn").style.display="none"
  document.getElementById("yearDropdownBtn").style.display="none"
}

function showCareerStatsNameInputs(){
  document.getElementById("firstNameLabel").style.display="inline-block"
  document.getElementById("firstName").style.display="inline-block"
  document.getElementById("lastNameLabel").style.display="inline-block"
  document.getElementById("lastName").style.display="inline-block"
}

function hideCareerStatsNameInputs(){
  document.getElementById("firstNameLabel").style.display="none"
  document.getElementById("firstName").style.display="none"
  document.getElementById("lastNameLabel").style.display="none"
  document.getElementById("lastName").style.display="none"
}

function getStatsOnClick() {
  if (teamAndYearBool){
    var team = document.getElementById('teamDropdownBtn').textContent;
    var year = document.getElementById('yearDropdownBtn').textContent;
    if (!(team=="Select Team" || year == "Select Year")){
      var query = "?teamid="+team+"&yearid="+year
      getStatsQuery(query)
    }
  }
  else if (careerBool){
    var firstName = document.getElementById('firstName').value;
    var lastName = document.getElementById('lastName').value;
    if (firstName && lastName){
      var query = "?nameFirst="+firstName+"&nameLast="+lastName;
      var people = getPeopleQuery(query)
    }
  }
  else if (allTimeBool){
    var stat = document.getElementById('allTimeDropdownBtn').textContent;
    if (stat!="Select Stat"){
      allTimeStats(stat)
    }
  }
}

function allTimeStats(stat){
  var query = "?stat="+stat
  var path = "http://127.0.0.1:5000/api/all_time_stats"
  //var path = "http://smortvedt.pythonanywhere.com/api/all_time_stats"
  var client = new HttpClient();
  client.get(path+query, function(response) {
      var results = JSON.parse(response).results
      var oldHeader = document.getElementsByTagName("thead")[0]
      var header = document.createElement("thead");
      var row = header.insertRow(0);     
      var cell = row.insertCell(0);
      var cell1 = row.insertCell(1)
      cell.innerHTML = "Name"
      cell1.innerHTML = stat
      oldHeader.parentNode.replaceChild(header,oldHeader)
      var table = document.getElementById("stats")
      var oldTableBody = document.getElementsByTagName("tbody")[0]
      var tableBody = document.createElement("tbody");
      var len = results.length
      for (var i =0; i<len;i++){
        var row = tableBody.insertRow(0)
        var cell = row.insertCell(0)
        var cell1 = row.insertCell(1)
        var name = results[len-i-1].namefirst +' '+ results[len-i-1].namelast
        cell.innerHTML = name
        cell1.innerHTML = results[len-i-1][stat]
      }
      oldTableBody.parentNode.replaceChild(tableBody,oldTableBody)
  });
}

function getPeopleQuery(query){
  //var path = "http://127.0.0.1:5000/api/people"
  var path = "http://smortvedt.pythonanywhere.com/api/people"

  var client = new HttpClient();
  client.get(path+query, function(response) {
      var results = JSON.parse(response).results
      var table = document.getElementById("stats")
      var oldTableBody = table.getElementsByTagName("tbody")[0]
      var tableBody = document.createElement('tbody')
      oldTableBody.parentNode.replaceChild(tableBody,oldTableBody)
      for (var i =0; i<results.length;i++){
        var playerID = results[i].playerID
        tableBody = getCareerStats(playerID,tableBody)
      }
    });
}

function getCareerStats(playerID,tableBody){
  var path = "http://127.0.0.1:5000/api/people/"+playerID+"/career_stats"
  //var path = "http://smortvedt.pythonanywhere.com/api/people/people/"+playerID+"career_stats"
  var client = new HttpClient();
  client.get(path, function(response) {
      var results = JSON.parse(response).results
      var table = document.getElementById("stats")
      var oldHeader = document.getElementsByTagName("thead")[0]
      var header = document.createElement("thead");
      var row = header.insertRow(0);     
      var cell = row.insertCell(0);
      var cell1 = row.insertCell(1)
      var cell2 = row.insertCell(2)
      var cell3 = row.insertCell(3)
      var cell4 = row.insertCell(4)
      var cell5 = row.insertCell(5)
      var cell6 = row.insertCell(6)
      cell.innerHTML = "Name"
      cell1.innerHTML = "Games Played"
      cell2.innerHTML = "Hits"
      cell3.innerHTML = "At Bats"
      cell4.innerHTML = "Batting Average"
      cell5.innerHTML = "First Year"
      cell6.innerHTML = "Last Year"
      oldHeader.parentNode.replaceChild(header,oldHeader)
      var tableBody = table.getElementsByTagName("tbody")[0]
      for (var i =0; i<results.length;i++){
        var row = tableBody.insertRow(0)
        var cell = row.insertCell(0)
        var cell1 = row.insertCell(1)
        var cell2 = row.insertCell(2)
        var cell3 = row.insertCell(3)
        var cell4 = row.insertCell(4)
        var cell5 = row.insertCell(5)
        var cell6 = row.insertCell(6)
        var name = results[i].namefirst +' '+ results[i].namelast
        cell.innerHTML = name
        cell1.innerHTML = results[i].g_all
        cell2.innerHTML = results[i].H
        cell3.innerHTML = results[i].AB
        cell4.innerHTML = results[i].AVG
        cell5.innerHTML = results[i].first_year
        cell6.innerHTML = results[i].last_year
      }
      return tableBody
  });

}

function getStatsQuery(query){
  var path = "http://127.0.0.1:5000/api/roster"
  //var path = "http://smortvedt.pythonanywhere.com/api/roster"

  var client = new HttpClient();
  client.get(path+query, function(response) {
      var results = JSON.parse(response).results
       var oldHeader = document.getElementsByTagName("thead")[0]
      var header = document.createElement("thead");
      var row = header.insertRow(0);     
      var cell = row.insertCell(0);
      var cell1 = row.insertCell(1)
      var cell2 = row.insertCell(2)
      var cell3 = row.insertCell(3)
      var cell4 = row.insertCell(4)
      cell.innerHTML = "Name"
      cell1.innerHTML = "Games Played"
      cell2.innerHTML = "Hits"
      cell3.innerHTML = "At Bats"
      cell4.innerHTML = "Batting Average"
      oldHeader.parentNode.replaceChild(header,oldHeader)
      var table = document.getElementById("stats")
      var oldTableBody = table.getElementsByTagName("tbody")[0]
      var tableBody = document.createElement('tbody')
      for (var i =0; i<results.length;i++){
        var row = tableBody.insertRow(0)
        var cell = row.insertCell(0)
        var cell1 = row.insertCell(1)
        var cell2 = row.insertCell(2)
        var cell3 = row.insertCell(3)
        var cell4  = row.insertCell(4)
        var name = results[i].namefirst +' '+ results[i].namelast
        cell.innerHTML = name
        cell1.innerHTML = results[i].g_all
        cell2.innerHTML = results[i].H
        cell3.innerHTML = results[i].AB
        cell4.innerHTML = results[i].AVG
      }
      oldTableBody.parentNode.replaceChild(tableBody,oldTableBody)
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

        anHttpRequest.send( null );
    }
}

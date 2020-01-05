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
      var results = JSON.parse(response).results
      var table = document.getElementById("stats")
      var oldTableBody = table.getElementsByTagName("tbody")[0]
      var tableBody = document.createElement('tbody')
      for (var i =0; i<results.length;i++){
        var row = tableBody.insertRow(0)
        var cell = row.insertCell(0)
        var cell1 = row.insertCell(1)
        var cell2 = row.insertCell(2)
        var cell3 = row.insertCell(3)
        var name = results[i].namefirst +' '+ results[i].namelast
        cell.innerHTML = name
        cell1.innerHTML = results[i].g_all
        cell2.innerHTML = results[i].H
        cell3.innerHTML = results[i].AB
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

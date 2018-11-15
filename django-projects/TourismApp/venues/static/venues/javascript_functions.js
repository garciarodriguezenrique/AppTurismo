

function hideMarkersOutsideOfRoute(){
    for (e in markers){
        if (!Object.keys(route).includes(markers[e].getTitle())){
            markers[e].setVisible(false);
        }
    }
}


function removeDuplicatesByName(jsonArray){
    var seenNames = {};
    jsonArray = jsonArray.filter(function(currentObject) {
        if (currentObject.name in seenNames) {
            return false;
        } else {
            seenNames[currentObject.name] = true;
            return true;
        }
    });
    return jsonArray;
}

function deleteMarkers(){
    for(i=0; i<markers.length; i++){
        markers[i].setMap(null);
    }
    markers = []
    document.getElementById("sidenav").innerHTML = "";
}


function getDistanceFromUserPosition(){
    var transport;
    transport = document.getElementById("transport").value;

    destinations = []
    for (venue in route){
        destinations.push(route[venue]);
    }
    if (transport=="transit-bus"){
        distanceMatrixService.getDistanceMatrix({
            origins: [user_position],
            destinations: destinations,
            travelMode: "TRANSIT",
            transitOptions: {
                modes: ['BUS'],
                routingPreference: 'FEWER_TRANSFERS'
            },
            unitSystem: google.maps.UnitSystem.METRIC,
        }, distanceMatrixSortCallback);
    } else if (transport=="transit-subway"){
        distanceMatrixService.getDistanceMatrix({
            origins: [user_position],
            destinations: destinations,
            travelMode: "TRANSIT",
            transitOptions: {
                modes: ['SUBWAY'],
                routingPreference: 'FEWER_TRANSFERS'
            },
            unitSystem: google.maps.UnitSystem.METRIC,
        }, distanceMatrixSortCallback);
    } else if (transport=="DRIVING"){
        distanceMatrixService.getDistanceMatrix({
            origins: [user_position],
            destinations: destinations,
            travelMode: "DRIVING",
            drivingOptions: {
                departureTime: new Date(Date.now()),  //new Date(Date.now() + N) siendo N el nº de milisegundos desde ahora
                trafficModel: 'bestguess'
            },
            unitSystem: google.maps.UnitSystem.METRIC,
        }, distanceMatrixSortCallback);
    } else {
        distanceMatrixService.getDistanceMatrix({
            origins: [user_position],
            destinations: destinations,
            travelMode: transport,
            unitSystem: google.maps.UnitSystem.METRIC,
        }, distanceMatrixSortCallback);
    }
          
}


function distanceMatrixSortCallback(response, status){
    if (status == 'OK') {
        var origins = response.originAddresses;
        var destinations = response.destinationAddresses;
        var max_distance = 0;
        var waypoints = [];
        //var stops = [];
        var currentFarthestPoint;
           
        stops = [];
        stopsIndex = 0;
        stops.push({"venue_addr":origins[0], "distance":0.0});
        var results = response.rows[0].elements;
        for (var j = 0; j < results.length; j++) {
            var element = results[j];
            var distance = element.distance.text.replace(",",".");
            var duration = element.duration.text;
            var from = origins[0];
            var to = destinations[j];
            element = {"venue_addr":to, "distance":parseFloat(distance.split(" ")[0])}
            stops.push(element)
        }
        //hay que insertar user_position en la primera posicion de stops. Usar from/origins[0]
        stops = stops.sort(function(a, b) {return a.distance - b.distance}); //Puntos de la ruta ordenados de más cercano a más lejano.

        //bucle for: calcular las rutas entre todos los elementos tal que a-b, b-c, c-d
        //for (i=0; i<stops.length-1; i++) {console.log("route "+i+" - "+(i+1));}
        hideMarkersOutsideOfRoute();
        displaySegment();
        /*for (i=0; i<stops.length-1; i++){
              console.log(i);
              if (i == stops.length - 2){
                  last = true;
              }
              var directionsDisplay = new google.maps.DirectionsRenderer({map: map});
              directionsDisplay.setOptions( { suppressMarkers: true } );
              directionsDisplay.setPanel(document.getElementById('right-panel'));
              calculateAndDisplayRoute(directionsDisplay, stops[i]['venue_addr'], stops[i+1]['venue_addr'], last);
        }*/
    }      
}


//Utilidad principal refrescar horas de buses/metro. Podría usarse para recalcular un segmento con otro medio de transporte, aunque no es recomendable ya que el orden de los componentes de la ruta se determina en base al medio de transporte indicado inicialmente. Si consigo implementar una versión en la que a cada paso se determine el siguiente elemento más cercano, así sí que tendra sentido.
function updateCurrentSegment(){
    calculateAndDisplayRoute(currentSegment["from"], currentSegment["to"]);
}

function pageReload(){
    location.reload();
}

function displaySegment(){
    console.log(stops);
    if (stops.length>0){
        if (stopsIndex == stops.length-1){
            stops = [];
            stopsIndex = 0;
            alert("Fin de trayecto");
        } else {
            currentSegment["from"]=stops[stopsIndex]['venue_addr'];
            currentSegment["to"]=stops[++stopsIndex]['venue_addr'];
            calculateAndDisplayRoute(currentSegment["from"], currentSegment["to"]);
        }
    }
}

function showAllMarkers(){
    for (e in markers){
        markers[e].setVisible(true);
    }
}

function hideAllMarkers(){
    for (e in markers){
        markers[e].setVisible(false);
    }
}

function calculateRouteControl(controlDiv, map) {
    //Borde
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = '#fff';
    controlUI.style.border = '2px solid #fff';
    controlUI.style.borderRadius = '50%';
    controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
    controlUI.style.cursor = 'pointer';
    controlUI.style.marginBottom = '22px';
    controlUI.style.textAlign = 'center';
    controlDiv.appendChild(controlUI);

    //Interior
    var controlText = document.createElement('div');
    controlText.style.color = 'rgb(25,25,25)';
    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '16px';
    controlText.style.lineHeight = '38px';
    controlText.style.paddingLeft = '5px';
    controlText.style.paddingRight = '5px';
    controlText.innerHTML = 'Calcular ruta';
    controlUI.appendChild(controlText);

    //Evento
    controlUI.addEventListener('click', function() {
        getDistanceFromUserPosition();
    });

}


function calculateAndDisplayRoute(from, to) {

    //Display options
    //directionsDisplay.setOptions( { suppressMarkers: true } );
    directionsDisplay.setPanel(document.getElementById('right-panel'));

    var transport;
    transport = document.getElementById("transport").value;

    if (transport == "transit-bus"){
        console.log("transit-bus: "+transport);
        directionsService.route({
            origin: from,
            destination: to,
            travelMode: 'TRANSIT',
            transitOptions: {
                modes: ['BUS'],
                routingPreference: 'FEWER_TRANSFERS' //La hora del siguiente bus depende de departureTime, así que si queremos que la hora de salida del bus tenga cierto margen por si la parada está más o menos lejos, poner un departureTime + X tiempo.
            },
            unitSystem: google.maps.UnitSystem.METRIC
        }, routeCallback);
    } else if (transport == "transit-subway"){
        console.log("transit-subway: "+transport);
        directionsService.route({
            origin: from,
            destination: to,
            travelMode: 'TRANSIT',
            transitOptions: {
                modes: ['SUBWAY'],
                routingPreference: 'FEWER_TRANSFERS'
            },
            unitSystem: google.maps.UnitSystem.METRIC
        }, routeCallback);
    } else if (transport == "DRIVING"){
        console.log("transit-driving: "+transport);
        directionsService.route({
            origin: from,
            destination: to,
            travelMode: 'DRIVING',
            drivingOptions: {
                departureTime: new Date(Date.now()),  //new Date(Date.now() + N) siendo N el nº de milisegundos desde ahora
                trafficModel: 'bestguess'
            },
            unitSystem: google.maps.UnitSystem.METRIC
        }, routeCallback);
    } else {
        console.log("transit-walking-bicylcing: "+transport);
        directionsService.route({
            origin: from,
            destination: to,
            travelMode: transport,
            unitSystem: google.maps.UnitSystem.METRIC
        }, routeCallback);
    }
}

function routeCallback(response, status) {
    if (status === 'OK') {
        console.log(response);
        hideMarkersOutsideOfRoute();
        directionsDisplay.setDirections(response);
    } else {
        window.alert('Directions request failed due to ' + status);
    }
}

function addToRoute(name, lat, lng) {
    var checkBox = document.getElementById("check_"+name);
    if (checkBox.checked == true){
        console.log("true");
        route[name] = new google.maps.LatLng(lat, lng) //{"lat":lat, "lng":lng};
    } else {
        console.log("false");
        delete route[name];
    }
}

//Función para el evento click en los elementos del panel lateral. Si hay otra ventana abierta la cierra antes de mostrar la seleccionada.
function myclick(i) {
    if (typeof open_marker !== 'undefined'){
        open_marker.infoWindow.close();
    }
    google.maps.event.trigger(markers[i], "click");
    open_marker = markers[i];
}


function placeMarkers(venue_list){
    var side_bar_html = "";
    var sorted = venue_list.sort(function(a, b) {return b.rating - a.rating}); //Ordena los lugares de mayor a menor valoración.
    sorted = removeDuplicatesByName(sorted);
    Object.keys(sorted).forEach(function(venue) {

        venue_name = sorted[venue]['name']
        venue_coordinates = sorted[venue]['geometry']['location']
    
        contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading">'+venue_name+'</h1>'+
            '<div id="bodyContent">'+
            '<p><b>'+venue_name+'</b></p>'+
            '<p>Attribution: '+venue_name+', <a href="https://www.google.es/#q='+venue_name+'">'+
            'Más información</a><BR>'+
            '<button onclick="calculateAndDisplayRoute('+ venue_coordinates["lat"] +','+ venue_coordinates["lng"] +')">Ir!</button>'+
            '</p>'+
            '</div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString
        });

        var marker = new google.maps.Marker({
            position : new google.maps.LatLng(venue_coordinates["lat"], venue_coordinates["lng"]),
            map : map,
            infoWindow: infowindow,
            title: venue_name
        });

             
        google.maps.event.addListener(marker, 'click', function() {
            if (typeof open_marker !== 'undefined'){
                open_marker.infoWindow.close();
            }
            map.setCenter(this.position);
            this.infoWindow.open(map, this);
            open_marker = this;
        });
               
           
	//Se añade el evento click a los elementos del panel lateral
        //href="javascript:myclick(' + (markers.length) + ')"
        
        detail_ref = '<a href="'+sorted[venue]['reference']+'/">Más detalles</a>'
               
        side_bar_html += '<a href="javascript:myclick(' + (markers.length) + ')">'
            + venue_name + " | " 
            + (sorted[venue]['rating']  !== 0 ?  sorted[venue]['rating'] + " | " : "" )
            + '<input type="checkbox" id="check_'+venue_name+'" onclick="addToRoute('+"'"+venue_name+"'"+','+venue_coordinates["lat"]+','+venue_coordinates["lng"]+')"></a>'
            + " | "
            + detail_ref;
            //Aquí iría el enlace para las vistas detalle con href

            markers.push(marker);
        });
        console.log("Se añade el contenido del menu lateral")
        document.getElementById("sidenav").innerHTML = side_bar_html;
}







      //Como a raíz del problema con el filtro de distancia la puntuación sería el único criterio, eliminamos el filtrado por puntuación
      //y hacemos que esa sea la ordenación por defecto. Se mantiene este código en caso de que posteriormente se añadan otras posibilidades de filtrado.

      /*function sortResults(){
          criteria = document.getElementById('criteria').value
          side_bar_html = ""
          if (criteria == "rating") {
              var sorted = j.sort(function(a, b) {return b.rating - a.rating})
              Object.keys(sorted).forEach(function(venue) {
                  venue_coordinates = sorted[venue]['geometry']['location']
                  side_bar_html += '<a href="javascript:myclick(' + (markers.length) + ')">'
                  + sorted[venue]['name'] + " | " 
                  + (sorted[venue]['opening_hours']  !== 0 ?  sorted[venue]['opening_hours'] + " | " : "" )
                  + (sorted[venue]['rating']  !== 0 ?  sorted[venue]['rating'] + " | " : "" )
                  + '<input type="checkbox" id="check_'+sorted[venue]['name']+'" onclick="addToRoute('+"'"+sorted[venue]['name']+"'"+','+venue_coordinates["lat"] +','+venue_coordinates["lng"]+')"></a>'
                  + " | ";
              });
              document.getElementById("sidenav").innerHTML = side_bar_html;
          } else if (criteria == "closest"){
              
          } 
      }*/


//----------------------------------------------------------------------------------------------------------------------------------------
      function getDistanceFromPosition(position){
          destinations = []
              for (venue in route){
                  destinations.push(route[venue]);
	      }
              distanceMatrixService.getDistanceMatrix({
                  origins: position,
                  destinations: destinations,
                  travelMode: travel_mode,
                  unitSystem: google.maps.UnitSystem.METRIC,
              }, distanceMatrixSort2Callback);
      }

      function distanceMatrixSort2Callback(response, status){
          if (status == 'OK') {
              var origins = response.originAddresses;
              var destinations = response.destinationAddresses;
              var max_distance = 0;
              var waypoints = [];
              //var stops = [];
              var currentFarthestPoint;

              stops = [];
              stopsIndex = 0;
              stops.push({"venue_addr":origins[0], "distance":0.0});
              var results = response.rows[0].elements;
              for (var j = 0; j < results.length; j++) {
                  var element = results[j];
                  var distance = element.distance.text.replace(",",".");
                  var duration = element.duration.text;
                  var from = origins[0];
                  var to = destinations[j];
                  console.log(from+" - "+to+" = "+distance);
                  element = {"venue_addr":to, "distance":distance}
                  stops.push(element)
              }
              //hay que insertar user_position en la primera posicion de stops. Usar from/origins[0]
              stops = stops.sort(function(a, b) {return a.distance - b.distance}); //Puntos de la ruta ordenados de más cercano a más lejano.

              //bucle for: calcular las rutas entre todos los elementos tal que a-b, b-c, c-d
              //for (i=0; i<stops.length-1; i++) {console.log("route "+i+" - "+(i+1));}
              hideMarkersOutsideOfRoute();
              displaySegment();
              /*for (i=0; i<stops.length-1; i++){
                  console.log(i);
                  if (i == stops.length - 2){
                      last = true;
                  }
                  var directionsDisplay = new google.maps.DirectionsRenderer({map: map});
                  directionsDisplay.setOptions( { suppressMarkers: true } );
                  directionsDisplay.setPanel(document.getElementById('right-panel'));
                  calculateAndDisplayRoute(directionsDisplay, stops[i]['venue_addr'], stops[i+1]['venue_addr'], last);
              }*/
          }      
      }

      //----------------------------------------------------------------------------------------------------------------------------------------      



      

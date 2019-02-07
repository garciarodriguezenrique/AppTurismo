function getClassName(category){
    if (category.includes('food')){
        return "fa d-inline fa-utensils mr-2";
    } else if (category.includes('bowling_alley')){
        return "fa d-inline fa-bowling-ball mr-2";
    } else if (category.includes('movie_theater')){
        return "fa d-inline fa-film mr-2";
    } else if (category.includes('spa')){
        return "fa d-inline fa-spa mr-2";
    } else if (category.includes('stadium')){
        return "fa d-inline fa-futbol mr-2";
    } else if (category.includes('zoo')){
        return "fa d-inline fa-paw mr-2";
    } else if (category.includes('leisure')){
        return "fa d-inline fa-gamepad mr-2";
    } else if (category.includes('art_gallery')){
        return "fa d-inline fa-image mr-2";
    } else if (category.includes('library')){
        return "fa d-inline fa-book-reader mr-2";
    } else if (category.includes('museum')){
        return "fa d-inline fa-landmark mr-2";
    } else if (category.includes('religious_emplacements')){
        return "fa d-inline fa-church mr-2";
    } else if (category.includes('public_emplacements')){
        return "fa d-inline fa-monuments mr-2";
    } else if (category.includes('campground')){
        return "fa d-inline fa-campground mr-2";
    } else if (category.includes('car_rental')){
        return "fa d-inline fa-car mr-2";
    } else if (category.includes('atm')){
        return "fa d-inline fa-hand-holding-usd mr-2";
    } else if (category.includes('parking')){
        return "fa d-inline fa-parking mr-2";
    } else if (category.includes('gas_station')){
        return "fa d-inline fa-gas-pump mr-2";
    } else if (category.includes('police')){
        return "fa d-inline fa-shield-alt mr-2";
    } else if (category.includes('book_store')){
        return "fa d-inline fa-book mr-2";
    } else if (category.includes('clothing_store')){
        return "fa d-inline fa-tshirt mr-2";
    } else if (category.includes('convenience_store')){
        return "fa d-inline fa-shopping-cart mr-2";
    } else if (category.includes('hardware_store')){
        return "fa d-inline fa-laptop mr-2";
    } else if (category.includes('shopping_mall')){
        return "fa d-inline fa-shopping-bag mr-2";
    } else if (category.includes('hospital')){
        return "fa d-inline fa-hospital mr-2";
    } else if (category.includes('pharmacy')){
        return "fa d-inline fa-briefcase-medical mr-2";
    } else if (category.includes('bar')){
        return "fa d-inline fa-beer mr-2";
    } else if (category.includes('night_club')){
        return "fa d-inline fa-cocktail mr-2";
    } else if (category.includes('airport')){
        return "fa d-inline fa-plane mr-2";
    } else if (category.includes('bus_station')){
        return "fa d-inline fa-bus-alt mr-2";
    } else if (category.includes('train_station')){
        return "fa d-inline fa-train mr-2";
    } else if (category.includes('subway_station')){
        return "fa d-inline fa-subway mr-2";
    } else if (category.includes('taxi_stand')){
        return "fa d-inline fa-taxi mr-2";
    }
}

function showMarkers(){
    for (e in markers){
        markers[e].setVisible(true);
    }
}

function hideMarkers(){
    for (e in markers){
        markers[e].setVisible(false);
        markers[e].setMap(null);
    }
}


function hideMarkersOutsideOfRoute(){
    for (e in markers){
        if (!Object.keys(route).includes(markers[e].getTitle())){
            markers[e].setVisible(false);
        }
    }
}

function addToRoute(name, lat, lng) {
    var checkBox = document.getElementById("check_"+name);
    if (checkBox.checked == true){
        console.log("true");
        route[name] = {"lat":lat, "lng":lng};//new google.maps.LatLng(lat, lng) //{"lat":lat, "lng":lng};
    } else {
        console.log("false");
        delete route[name];
    }
}

function getCategorySpanish(category){

    var category_name = ""

    if (category.includes('restaurant')){
        category_name += "restaurante, ";
    } 
    if (category.includes('meal_takeaway')){
        category_name += "comida para llevar, ";
    } 
    if (category.includes('amusement_park')){
        category_name += "parque de juegos, ";
    } 
    if (category.includes('bowling_alley')){
        category_name += "bolera, ";
    } 
    if (category.includes('movie_theater')){
        category_name += "cine, ";
    } 
    if (category.includes('spa')){
        category_name += "spa/centro de belleza, ";
    } 
    if (category.includes('zoo')){
        category_name += "zoo, ";
    } 
    if (category.includes('art_gallery')){
        category_name += "fotografía, ";
    } 
    if (category.includes('library')){
        category_name += "biblioteca, ";
    } 
    if (category.includes('museum')){
        category_name += "museo, ";
    } 
    if (category.includes('religious_emplacements')){
        category_name += "templo religioso, ";
    } 
    if (category.includes('public_emplacements')){
        category_name += "espacio público, ";
    }
    if (category.includes('campground')){
        category_name += "camping, ";
    }
    if (category.includes('car_rental')){
        category_name += "alquiler de coches, ";
    }
    if (category.includes('atm')){
        category_name += "cajero, ";
    }
    if (category.includes('parking')){
        category_name += "parking, ";
    }
    if (category.includes('gas_station')){
        category_name += "gasolinera, ";
    }
    if (category.includes('police')){
        category_name += "policía, ";
    }
    if (category.includes('book_store')){
        category_name += "librería, ";
    }
    if (category.includes('clothing_store')){
        category_name += "tienda de ropa, ";
    } 
    if (category.includes('convenience_store')){
        category_name += "supermercado/hipermercado, ";
    } 
    if (category.includes('hardware_store')){
        category_name += "tienda de electrónica, ";
    } 
    if (category.includes('shopping_mall')){
        category_name += "centro comercial, ";
    } 
    if (category.includes('other_stores')){
        category_name += "otros, ";
    }
    if (category.includes('hospital')){
        category_name += "hospital, ";
    } 
    if (category.includes('pharmacy')){
        category_name += "farmacia, ";
    }
    if (category.includes('bar')){
        category_name += "bar, ";
    } 
    if (category.includes('night_club')){
        category_name += "club, ";
    }
    if (category.includes('airport')){
        category_name += "aeropuerto, ";
    } 
    if (category.includes('bus_station')){
        category_name += "parada/estación de bus, ";
    } 
    if (category.includes('train_station')){
        category_name += "parada/estación de tren ";
    }
    if (category.includes('subway_station')){
        category_name += "parada/estación de metro, ";
    }
    if (category.includes('taxi_stand')){
        category_name += "parada de taxis, ";
    }   

    return category_name.substring(0, category_name.length - 2);
    
}


function deg2rad(deg) {
  return deg * (Math.PI/180)
}

function getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2) {
  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2-lat1);  // deg2rad 
  var dLon = deg2rad(lon2-lon1); 
  var a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ; 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c; // Distance in km
  return d;
}


function removeDuplicatesByName(jsonArray){
    var seenNames = {};
    jsonArray = jsonArray.filter(function(currentObject) {
        if (currentObject.venue_name in seenNames) {
            return false;
        } else {
            seenNames[currentObject.venue_name] = true;
            return true;
        }
    });
    return jsonArray;
}

function formatCategories(category_list){
    var finalString = "";
    for (category in category_list){
        finalString += category_list[category].split(" ")[0]+"|";
    }
    return finalString.substring(0, finalString.length - 1);
}

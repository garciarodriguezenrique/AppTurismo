
food=["restaurant","meal_delivery","meal_takeaway"]
restaurant=["restaurant","meal_delivery"]
meal_takeaway=["meal_takeaway","meal_delivery"]

leisure=["amusement_park","bowling_alley","casino","movie_theater","spa","stadium","zoo"]
amusement_park=["amusement_park"]
bowling_alley=["bowling_alley"]
casino=["casino"]
movie_theater=["movie_theater"]
spa=["spa"]
stadium=["stadium"]
zoo=["zoo"]

culture=["art_gallery","library","museum","church","city_hall","synagogue","mosque","hindu_temple","park","monument"]
monument=["monument"]
art_gallery=["art_gallery"]
library=["library"]
museum=["museum"]
religious_emplacements = ["synagogue", "church", "mosque", "hindu_temple"]
park=["park"]
public_emplacements=["city_hall","park"]

services=["campground","car_rental","atm","parking","gas_station","police","rv_park","lodging"]
lodging=["lodging"]
campground=["campground","rv_camp"]
car_rental=["car_rental"]
atm=["atm"]
parking=["parking"]
gas_station=["gas_station"]
police=["police"]


shopping=["book_store","clothing_store","convenience_store","department_store","electronics_store","hardware_store","florist","jewelry_store","pet_store","shopping_mall","store","supermarket"]
book_store=["book_store"]
clothing_store=["clothing_store"]
convenience_store=["convenience_store","department_store","supermarket"]
hardware_store=["hardware_store","electronics_store"]
shopping_mall=["shopping_mall"]
other_stores=["pet_store","jewelry_store","florist"]


medical_services=["doctor","hospital","pharmacy"]
hospital=["doctor","hospital"]
pharmacy=["pharmacy"]

bar_and_clubs=["bar","cafe","night_club"]
bar=["bar","cafe"]
night_club=["night_club"]

transport=["airport","bus_station","train_station","subway_station","taxi_stand"]
airport=["airport"]
bus_station=["bus_station"]
train_station=["train_station"]
subway_station=["subway_station"]
taxi_stand=["taxi_stand"] 

other=["park"]

CATEGORIES = {'food':food, 'restaurant':restaurant, 'meal_takeaway':meal_takeaway,
'leisure':leisure, 'amusement_park':amusement_park, 'bowling_alley':bowling_alley, 'casino':casino, 'movie_theater':movie_theater, 'spa':spa, 'stadium':stadium, 'zoo':zoo, 
'culture':culture, 'art_gallery':art_gallery, 'museum':museum, 'library':library, 'religious_emplacements':religious_emplacements, 'public_emplacements':public_emplacements, 'monument':monument, 'park':park,
'services':services, 'campground':campground, 'car_rental':car_rental, 'atm':atm, 'parking':parking, 'gas_station':gas_station, 'police':police, 'lodging':lodging,
'shopping':shopping, 'book_store':book_store, 'clothing_store':clothing_store, 'convenience_store':convenience_store, 'hardware_store':hardware_store, 'shopping_mall':shopping_mall, 'other_stores':other_stores,
'medical_services':medical_services, 'hospital':hospital, 'pharmacy':pharmacy, 
'bar_and_clubs':bar_and_clubs, 'bar':bar, 'night_club':night_club,
'transport':transport, 'airport':airport, 'bus_station':bus_station, 'train_station':train_station, 'subway_station':subway_station, 'taxi_stand':taxi_stand,
'other':other}


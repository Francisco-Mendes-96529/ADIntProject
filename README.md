# ADInt Project

Repository for ADInt Project

## Part 1

We need to make the compoments as independet as possible.

### TaskList

1. [X] QRCodeGenerator
2. [X] FoodService
   	1. [X] User App
	2. [X] Admin App
3. [X] RoomService
  	1. [X] User App
  	2. [X] Admin App
4. [X] Check-in App
5. [X] Message App

### QRCodeGenerator

- Form -> input string
- Get QRCode man

Doesn't matter how it will be implemented later.

### Food Service

- Store a list of restaurants and evaluations.
- Users evaluate a with an integer -> link table to the the restaurants
- Users are stored in another table (implement later with Fenix, QRContext) -> use userId
- Managed by the admin application
- User validation/ chech in will be handled on the QRContext
- User has to be check in to do the evaluation

Now: do 2 endpoints:

1. /evaluate -> return template with a form with a userId, restaurantId and Evaluation; Submit Button.
2. /postevaluation -> sqlalchemy stuff.

evaluate will migrate to the QRContext.

### Room Service

1. Save the weekday and start and end times
2. Receive JSON file to update schedule

## Part 2

### QRContext

#### Authentication
- [x] (F 1) Login on FENIX

#### Restaurants and canteens
- [x] (F 2) See the current menu
- [x] (F 3) Check-in in a restaurant
- [x] (F 4) Check-out from a restaurant
- [x] (F 5) Evaluate the meal at the restaurant that they checked in

#### Classrooms
- [x] (F 6) See a room schedule
- [x] (F 7) Verify if the next class in the room is from one enrolled course
- [x] (F 8) Check-in a class that is taking place in the room
- [x] (F 9) Check-out a class

#### Study room
- [x] (F 10) Check-in and assign an enrolled class to a study period
- [x] (F 11) Check-out a study period

#### Other users:
- [ ] <s>~~(F 12) Show a personal QRCode~~</s>
- [x] (F 13) Send messages to users that are in the same room
	- [x] Update messages every 30s
    	- [x] Update users
- [ ] <s>~~(F 14) Send messages to users that presented their their QRCode~~</s>


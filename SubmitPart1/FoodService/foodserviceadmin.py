from xmlrpc import client

# Define the XML-RPC server URL
SERVER_URL = "http://localhost:5002/api"

# Create an XML-RPC proxy
proxy = client.ServerProxy(SERVER_URL, allow_none=True)


def newRestaurant():
    try:
        name = input("Enter the name of the new restaurant: ")
        result = proxy.newRestaurant(name)
        print(f"Restaurant created: {result}")
    except Exception as e:
        print(f"Error creating restaurant: {str(e)}")


def newMenu():
    try:
        resId = input("Enter the Restaurant Id: ")
        food = input("Enter the new food to add to the Menu: ")
        result = proxy.newMenu(food, resId)
        print(f"{result}")
    except Exception as e:
        print(f"Error creating menu: {str(e)}")


def delRestaurant():
    try:
        resId = input("Enter the Restaurant Id to delete: ")
        result = proxy.delRestaurant(resId)
        print(f"Restaurant deleted: {result}")
    except Exception as e:
        print(f"Error deleting restaurant: {str(e)}")


def delMenu():
    try:
        menuId = input("Enter the Menu Id to delete: ")
        result = proxy.delMenu(menuId)
        print(f"Menu deleted: {result}")
    except Exception as e:
        print(f"Error deleting menu: {str(e)}")


def listRestaurants():
    try:
        restaurants = proxy.getRestaurant()
        print("List of Restaurants:")
        for restaurant in restaurants:
            print(restaurant)
    except Exception as e:
        print(f"Error listing restaurants: {str(e)}")


def showMenu():
    try:
        id = input(
            "Enter the Restaurant ID to view menu (press Enter to view all menus): "
        )
        id = int(id) if id.isdigit() else None
        result = proxy.getMenu(id)
        if result:
            if id:
                print(f"Menu for Restaurant id {id}")
                for entry in result:
                    print(entry)
            else:
                for res in result:
                    print(f"Menu for Restaurant id {res['resId']}")
                    for entry in res["menu"]:
                        print(entry)
        else:
            print("Restaurant not found")
    except Exception as e:
        print(f"Error updating menu: {str(e)}")


def showRatings():
    try:
        id = input("Enter the Restaurant ID to show ratings: ")
        id = int(id)
        evaluations = proxy.getRatings(id)
        if evaluations:
            print(f"Evaluations for Restaurant ID {id}:")
            for evaluation in evaluations:
                print(evaluation)
        elif evaluations is None:
            print(f"Restaurant with ID {id} does not exist")
        else:
            print(f"Restaurant with ID {id} has no evaluations")
    except Exception as e:
        print(f"Error showing evaluations: {str(e)}")


def main_loop():
    while True:
        print("Options:")
        print("1. Create a new restaurant")
        print("2. Create a new menu")
        print("3. Delete a restaurant")
        print("4. Delete a menu")
        print("5. List all restaurants")
        print("6. View a restaurant's menu")
        print("7. Show ratings for a restaurant")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            newRestaurant()
        elif choice == "2":
            newMenu()
        elif choice == "3":
            delRestaurant()
        elif choice == "4":
            delMenu()
        elif choice == "5":
            listRestaurants()
        elif choice == "6":
            showMenu()
        elif choice == "7":
            showRatings()
        elif choice == "8":
            break
        else:
            print("Invalid choice. Please try again.")
        input()


if __name__ == "__main__":
    main_loop()

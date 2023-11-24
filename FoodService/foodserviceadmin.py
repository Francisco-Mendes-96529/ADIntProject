from xmlrpc import client
import argparse

# Define the XML-RPC server URL
SERVER_URL = "http://localhost:5000/api"

# Create an XML-RPC proxy
proxy = client.ServerProxy(SERVER_URL, allow_none=True)


def newRestaurant(args):
    # Implement the logic to create a restaurant on the server
    try:
        result = proxy.newRestaurant(args.name)
        print(f"Restaurant created: {result}")
    except Exception as e:
        print(f"Error creating restaurant: {str(e)}")


def newMenu(args):
    try:
        result = proxy.newMenu(args.food, args.resId)
        print(f"Menu created: {result}")
    except Exception as e:
        print(f"Error creating restaurant: {str(e)}")


def delRestaurant(args):
    # Implement the logic to create a restaurant on the server
    try:
        result = proxy.delRestaurant(args.resId)
        print(f"Restaurant deleted: {result}")
    except Exception as e:
        print(f"Error deleting restaurant: {str(e)}")


def delMenu(args):
    try:
        result = proxy.delMenu(args.menuId)
        print(f"Menu deleted: {result}")
    except Exception as e:
        print(f"Error deleting menu: {str(e)}")


def list_restaurants(args):
    # Implement the logic to list restaurants from the server
    try:
        restaurants = proxy.getRestaurant()
        print("List of Restaurants:")
        for restaurant in restaurants:
            print(restaurant)
    except Exception as e:
        print(f"Error listing restaurants: {str(e)}")


def showMenu(args):
    # Implement the logic to update the menu of a restaurant on the server
    try:
        result = proxy.getMenu(args.id)
        if result:
            if args.id:
                print(f"Menu for Restaurant id {args.id}")
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


def showRatings(args):
    # Implement the logic to show evaluations for a restaurant on the server
    try:
        evaluations = proxy.getRatings(args.id)
        if evaluations:
            print(f"Evaluations for Restaurant ID {args.id}:")
            for evaluation in evaluations:
                print(evaluation)
        else:
            print(f"Restaurant with ID {args.id} has no evaluations")
    except Exception as e:
        print(f"Error showing evaluations: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Restaurant Admin CLI App")

    subparsers = parser.add_subparsers(
        title="Actions", dest="action", help="Available actions"
    )

    # Subparser for 'new' action

    new_parser = subparsers.add_parser("new", help="Create a new restaurant or menu")
    new_subparser = new_parser.add_subparsers(
        title="New Actions", dest="newaction", help="Available Actions for New"
    )

    # New Restaurant
    newRestaurantParser = new_subparser.add_parser(
        "restaurant", help="Create a New Restaurant"
    )
    newRestaurantParser.add_argument("name", help="New Restaurant Name")

    # New Menu for Restaurant
    newMenuParser = new_subparser.add_parser("menu", help="New Menu for Restaurant")
    newMenuParser.add_argument("resId", help="Restaurant Id")
    newMenuParser.add_argument("food", help="New food to add to the Menu")

    # Subparser for 'del' action

    del_parser = subparsers.add_parser("del", help="Del restaurant or menu")
    del_subparser = del_parser.add_subparsers(
        title="Del Actions", dest="delaction", help="Available Actions for Del"
    )

    # Del Restaurant
    delRestaurantParser = del_subparser.add_parser(
        "restaurant", help="Delete a Restaurant"
    )
    delRestaurantParser.add_argument("resId", help="Restaurant id to Delete")

    # Del Menu for Restaurant
    delMenuParser = del_subparser.add_parser("menu", help="Delete Menu for Restaurant")
    delMenuParser.add_argument("menuId", help="Menu Id to Delete")

    # Subparser for 'list' action
    list_parser = subparsers.add_parser("restaurants", help="List all restaurants")

    # Subparser for 'update' action
    menu_parser = subparsers.add_parser("menu", help="View a restaurant's menu")
    menu_parser.add_argument("--id", required=False, help="Restaurant ID", type=int)

    # Subparser for 'evaluations' action
    ratings_parser = subparsers.add_parser(
        "ratings", help="Show ratings for a restaurant"
    )
    ratings_parser.add_argument("id", help="Restaurant ID", type=int)

    args = parser.parse_args()

    if args.action == "new":
        if args.newaction == "restaurant":
            newRestaurant(args)
        elif args.newaction == "menu":
            newMenu(args)
    if args.action == "del":
        if args.delaction == "restaurant":
            delRestaurant(args)
        elif args.delaction == "menu":
            delMenu(args)
    elif args.action == "restaurants":
        list_restaurants(args)
    elif args.action == "menu":
        showMenu(args)
    elif args.action == "ratings":
        showRatings(args)


if __name__ == "__main__":
    main()

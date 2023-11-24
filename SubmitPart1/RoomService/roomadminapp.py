from xmlrpc import client

# Define the XML-RPC server URL
SERVER_URL = "http://localhost:5003/api"

# Create an XML-RPC proxy
proxy = client.ServerProxy(SERVER_URL, allow_none=True)

def newSpace():
    try:
        space_id = input("Space Id: ")
        name = input("Name: ")

        print(proxy.newSpace(space_id, name))

    except Exception as e:
        print(f"Error adding space: {e}")

def getSpaces():
    try:
        spaces = proxy.getSpacesDict()
        print('List of Spaces:')
        for space in spaces:
            print(space)
    except Exception as e:
        print(f"Error listing spaces: {e}")

def getScheduleBySpace():
    try:
        space_id = input("Space Id: ")
        events = proxy.getScheduleDictBySpace(space_id)
        if events == None:
            print(f"Space with Id {space_id} not found.")
        elif events:
            print('Schedule:')
            for event in events:
                print(event)
        else:
            print("No events schedule.")
    except Exception as e:
        print(f"Error listing space schedule: {e}")

def updateSchedule():
    try:
        # Get the JSON file name from user input
        json_filename = input('JSON file name: ')

        # Read the JSON data from the file
        with open(json_filename, 'r') as file:
            data = file.read()

        print(proxy.updateSchedule(data))
    except Exception as e:
        print(f"Error updating space schedule: {e}")

def main():
    while True:
        print('\nChoose one option:')
        print('1. Add a space')
        print('2. List all spaces')
        print('3. List schedule for a space')
        print('4. Update schedule with a JSON file')
        print('Q. Quit')

        option = input('\nOption: ')

        if option == "1":
            newSpace()

        elif option == "2":
            getSpaces()

        elif option == "3":
            getScheduleBySpace()

        elif option == "4":
            updateSchedule()

        elif option == "Q" or option == "q":
            break

        else:
            print("\nInvalid choice. Please try again.")

        input()


if __name__ == "__main__":
    main()            
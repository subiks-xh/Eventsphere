import json
import os
from event import Event, Attendee, Vendor

FILE_NAME = "data.json"

def loadData():
    if not os.path.exists(FILE_NAME):
        return {"events": [], "vendors": [], "ticket_counter": 1001}
    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)
            if isinstance(data, list):
                return {"events": data, "vendors": [], "ticket_counter": 1001}
            return data
    except:
        return {"events": [], "vendors": [], "ticket_counter": 1001}

def saveData(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def createEvent():
    data = loadData()
    event_id = input("Enter Event ID: ").strip()
    if not event_id:
        print("ID empty")
        return
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            print("ID exists")
            return
    event_name = input("Enter Name: ").strip()
    if not event_name:
        print("Name empty")
        return
    date = input("Enter Date: ").strip()
    time = input("Enter Time: ").strip()
    venue = input("Enter Venue: ").strip()
    resources = input("Enter Resources: ").strip()
    status = "Planning"

    new_event = Event(event_id, event_name, date, time, venue, resources, status)
    data["events"].append(new_event.to_dict())
    saveData(data)
    print("Event created")

def viewEvents():
    data = loadData()
    if not data["events"]:
        print("No events")
        return
    for event in data["events"]:
        print("ID:", event['event_id'])
        print("Name:", event['event_name'])
        print("Date:", event['date'])
        print("Time:", event['time'])
        print("Venue:", event['venue'])
        print("Resources:", event['resources'])
        print("Status:", event['status'])
        print("---")

def searchEvent():
    data = loadData()
    event_id = input("Enter ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            print("ID:", event['event_id'])
            print("Name:", event['event_name'])
            print("Date:", event['date'])
            print("Time:", event['time'])
            print("Venue:", event['venue'])
            print("Resources:", event['resources'])
            print("Status:", event['status'])
            return
    print("Event not found")

def updateEvent():
    data = loadData()
    event_id = input("Enter ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            new_name = input("New Name: ").strip()
            if new_name:
                event["event_name"] = new_name
            new_date = input("New Date: ").strip()
            if new_date:
                event["date"] = new_date
            new_time = input("New Time: ").strip()
            if new_time:
                event["time"] = new_time
            new_venue = input("New Venue: ").strip()
            if new_venue:
                event["venue"] = new_venue
            new_resources = input("New Resources: ").strip()
            if new_resources:
                event["resources"] = new_resources
            new_status = input("New Status: ").strip()
            if new_status:
                event["status"] = new_status
            saveData(data)
            print("Updated")
            return
    print("Event not found")

def deleteEvent():
    data = loadData()
    event_id = input("Enter ID: ").strip()
    for i in range(len(data["events"])):
        if str(data["events"][i]["event_id"]) == str(event_id):
            del data["events"][i]
            saveData(data)
            print("Deleted")
            return
    print("Event not found")

def registerAttendee():
    data = loadData()
    viewEvents()
    event_id = input("Enter Event ID for registration: ").strip()
    selected_event = None
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            selected_event = event
            break
    if not selected_event:
        print("Event Not Found")
        return

    reg_id = input("Registration ID: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()

    if "attendees" not in selected_event:
        selected_event["attendees"] = []

    for a in selected_event["attendees"]:
        if a["email"] == email:
            print("Already Registered")
            return

    ticket_id = "TKT" + str(data["ticket_counter"])
    data["ticket_counter"] += 1

    new_attendee = Attendee(reg_id, name, email, phone, ticket_id)
    selected_event["attendees"].append(new_attendee.to_dict())
    saveData(data)
    print("Registration Successful")
    print("Ticket:", ticket_id)

def viewAttendees():
    data = loadData()
    viewEvents()
    event_id = input("Enter Event ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            attendees = event.get("attendees", [])
            if not attendees:
                print("No Registrations")
                return
            print("\n--- Attendees ---")
            for a in attendees:
                print("Name:", a["name"], "| Ticket:", a["ticket_id"], "| Status:", a["status"])
            return
    print("Event Not Found")

def markAttendance():
    data = loadData()
    viewEvents()
    event_id = input("Enter Event ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            ticket_id = input("Ticket ID: ").strip()
            for a in event.get("attendees", []):
                if a["ticket_id"] == ticket_id:
                    a["status"] = "Checked In"
                    saveData(data)
                    print("Attendance Updated")
                    return
            print("Invalid Ticket")
            return
    print("Event Not Found")

def addVendor():
    data = loadData()
    vendor_id = input("Vendor ID: ").strip()
    for v in data["vendors"]:
        if str(v["vendor_id"]) == str(vendor_id):
            print("Vendor ID exists")
            return
    name = input("Vendor Name: ").strip()
    service = input("Service: ").strip()

    new_vendor = Vendor(vendor_id, name, service)
    data["vendors"].append(new_vendor.to_dict())
    saveData(data)
    print("Vendor Added")

def viewVendors():
    data = loadData()
    if not data["vendors"]:
        print("No Vendors")
        return
    print("\n--- Vendors ---")
    for v in data["vendors"]:
        print("ID:", v["vendor_id"], "| Name:", v["name"], "| Service:", v["service"])

def assignVendor():
    data = loadData()
    viewEvents()
    event_id = input("Enter Event ID: ").strip()
    selected_event = None
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            selected_event = event
            break
    if not selected_event:
        print("Event Not Found")
        return

    viewVendors()
    vendor_id = input("Enter Vendor ID: ").strip()
    selected_vendor = None
    for v in data["vendors"]:
        if str(v["vendor_id"]) == str(vendor_id):
            selected_vendor = v
            break
    if not selected_vendor:
        print("Vendor Not Found")
        return

    if "vendors" not in selected_event:
        selected_event["vendors"] = []

    for v in selected_event["vendors"]:
        if str(v["vendor_id"]) == str(vendor_id):
            print("Vendor Already Assigned")
            return

    selected_event["vendors"].append(selected_vendor)
    saveData(data)
    print("Vendor Assigned")

def generateReport():
    data = loadData()
    print("\n=== EVENT REPORT ===")
    if not data["events"]:
        print("No Events Available")
        return
    for e in data["events"]:
        print("\nEvent Name:", e["event_name"])
        attendees = e.get("attendees", [])
        print("Registrations:", len(attendees))
        checked_in = sum(1 for a in attendees if a["status"] == "Checked In")
        print("Checked In:", checked_in)
        vendors = e.get("vendors", [])
        print("Assigned Vendors:")
        if not vendors:
            print(" - None")
        else:
            for v in vendors:
                print(" -", v["name"], f"({v['service']})")

def main():
    while True:
        print("\n=== EventSphere ===")
        print("1. Create Event")
        print("2. View Events")
        print("3. Search Event")
        print("4. Update Event")
        print("5. Delete Event")
        print("6. Register Attendee")
        print("7. View Attendees")
        print("8. Mark Attendance")
        print("9. Add Vendor")
        print("10. View Vendors")
        print("11. Assign Vendor")
        print("12. Generate Report")
        print("13. Exit")

        choice = input("Choice: ").strip()

        if choice == "1":
            createEvent()
        elif choice == "2":
            viewEvents()
        elif choice == "3":
            searchEvent()
        elif choice == "4":
            updateEvent()
        elif choice == "5":
            deleteEvent()
        elif choice == "6":
            registerAttendee()
        elif choice == "7":
            viewAttendees()
        elif choice == "8":
            markAttendance()
        elif choice == "9":
            addVendor()
        elif choice == "10":
            viewVendors()
        elif choice == "11":
            assignVendor()
        elif choice == "12":
            generateReport()
        elif choice == "13":
            print("Exiting program.")
            break
        else:
            print("Wrong choice")

if __name__ == "__main__":
    main()
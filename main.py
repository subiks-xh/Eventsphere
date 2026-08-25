import json
import os
from event import Event, Attendee, Vendor

FILE_NAME = "data.json"

def loadData():
    if not os.path.exists(FILE_NAME):
        return {"events": [], "vendors": [], "ticket_counter": 1001, "notifications": []}
    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)
            if isinstance(data, list):
                return {"events": data, "vendors": [], "ticket_counter": 1001, "notifications": []}
            if "notifications" not in data:
                data["notifications"] = []
            return data
    except:
        return {"events": [], "vendors": [], "ticket_counter": 1001, "notifications": []}

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
    capacity = input("Enter Capacity: ").strip()
    try:
        capacity = int(capacity)
    except:
        capacity = 0
    status = "Planning"

    new_event = Event(event_id, event_name, date, time, venue, resources, status, capacity=capacity)
    data["events"].append(new_event.to_dict())
    saveData(data)
    print("Event created")

def viewEvents():
    data = loadData()
    if not data["events"]:
        print("No events")
        return
    for event in data["events"]:
        print("ID:", event['event_id'], "| Name:", event['event_name'], "| Capacity:", event.get("capacity", "N/A"))
        print("Date:", event['date'], "| Venue:", event['venue'])
        print("Status:", event['status'])
        print("---")

def searchEvent():
    data = loadData()
    event_id = input("Enter ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            print("ID:", event["event_id"])
            print("Name:", event["event_name"])
            print("Date:", event["date"])
            print("Time:", event["time"])
            print("Venue:", event["venue"])
            print("Resources:", event["resources"])
            print("Status:", event["status"])
            return
    print("Event not found")

def updateEvent():
    data = loadData()
    event_id = input("Enter ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            new_name = input("New Name (enter to skip): ").strip()
            if new_name:
                event["event_name"] = new_name
            new_date = input("New Date (enter to skip): ").strip()
            if new_date:
                event["date"] = new_date
            new_time = input("New Time (enter to skip): ").strip()
            if new_time:
                event["time"] = new_time
            new_venue = input("New Venue (enter to skip): ").strip()
            if new_venue:
                old_venue = event.get("venue", "")
                event["venue"] = new_venue
                if old_venue and new_venue != old_venue:
                    notification = "Event venue for " + event["event_name"] + " changed to " + new_venue + "."
                    data["notifications"].append(notification)
            new_resources = input("New Resources (enter to skip): ").strip()
            if new_resources:
                event["resources"] = new_resources
            new_status = input("New Status (enter to skip): ").strip()
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
    if "waitlist" not in selected_event:
        selected_event["waitlist"] = []

    for a in selected_event["attendees"]:
        if a["email"] == email:
            print("Already Registered")
            return

    for w in selected_event["waitlist"]:
        if w["email"] == email:
            print("Already on Waitlist")
            return

    capacity = selected_event.get("capacity", 0)
    current_count = len(selected_event["attendees"])

    if capacity > 0 and current_count >= capacity:
        print("Event is full. Capacity:", capacity)
        choice = input("Add to waitlist? (yes/no): ").strip().lower()
        if choice == "yes":
            waitlist_entry = {"reg_id": reg_id, "name": name, "email": email, "phone": phone}
            selected_event["waitlist"].append(waitlist_entry)
            saveData(data)
            print("Added to waitlist")
        else:
            print("Registration cancelled")
        return

    ticket_id = "TKT" + str(data["ticket_counter"])
    data["ticket_counter"] += 1

    new_attendee = Attendee(reg_id, name, email, phone, ticket_id)
    selected_event["attendees"].append(new_attendee.to_dict())

    notification = "Registration successful for " + selected_event["event_name"] + ". Ticket: " + ticket_id
    data["notifications"].append(notification)

    saveData(data)
    print("Registration Successful")
    print("Ticket:", ticket_id)
    print("Notification Created")

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
    import datetime
    data = loadData()
    viewEvents()
    event_id = input("Enter Event ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            ticket_id = input("Ticket ID: ").strip()
            for a in event.get("attendees", []):
                if a["ticket_id"] == ticket_id:
                    if a["status"] == "Checked In":
                        print("Already Checked In")
                        return
                    a["status"] = "Checked In"
                    a["checkin_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    a["certificate"] = "Eligible"
                    saveData(data)
                    print("Attendance Updated")
                    print("Check-in Time:", a["checkin_time"])
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
        print("Date:", e.get("date", ""))
        print("Venue:", e.get("venue", ""))
        capacity = e.get("capacity", 0)
        print("Capacity:", capacity)
        attendees = e.get("attendees", [])
        total_reg = len(attendees)
        print("Registrations:", total_reg)
        checked_in = sum(1 for a in attendees if a.get("status") == "Checked In")
        print("Checked In:", checked_in)
        waitlisted = len(e.get("waitlist", []))
        print("Waitlisted:", waitlisted)
        if capacity > 0:
            percentage = int((checked_in / capacity) * 100)
            print("Attendance:", str(percentage) + "%")
        else:
            print("Attendance: N/A")
        cert_eligible = sum(1 for a in attendees if a.get("certificate") == "Eligible")
        print("Certificate Eligible:", cert_eligible)
        vendors = e.get("vendors", [])
        print("Assigned Vendors:")
        if not vendors:
            print(" - None")
        else:
            for v in vendors:
                print(" -", v["name"], "(" + v["service"] + ")")
        print("---")

def cancelRegistration():
    data = loadData()
    event_id = input("Enter Event ID: ").strip()
    selected_event = None
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            selected_event = event
            break
    if not selected_event:
        print("Event Not Found")
        return
    ticket_id = input("Enter Ticket ID: ").strip()
    attendees = selected_event.get("attendees", [])
    found = None
    for a in attendees:
        if a["ticket_id"] == ticket_id:
            found = a
            break
    if not found:
        print("Registration not found")
        return
    attendees.remove(found)
    print("Registration Cancelled for", found["name"])
    waitlist = selected_event.get("waitlist", [])
    if waitlist:
        next_person = waitlist.pop(0)
        new_ticket = "TKT" + str(data["ticket_counter"])
        data["ticket_counter"] += 1
        promoted = Attendee(next_person["reg_id"], next_person["name"], next_person["email"], next_person["phone"], new_ticket)
        selected_event["attendees"].append(promoted.to_dict())
        notification = "Your registration for " + selected_event["event_name"] + " has been confirmed from the waitlist. Ticket: " + new_ticket
        data["notifications"].append(notification)
        print(next_person["name"], "promoted from waitlist")
        print("New Ticket:", new_ticket)
        print("Notification Created")
    saveData(data)

def viewNotifications():
    data = loadData()
    notifications = data.get("notifications", [])
    if not notifications:
        print("No Notifications")
        return
    print("\n--- Notifications ---")
    for n in notifications:
        print("-", n)

def viewWaitlist():
    data = loadData()
    event_id = input("Enter Event ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            waitlist = event.get("waitlist", [])
            if not waitlist:
                print("Waitlist is empty")
                return
            print("\n--- Waitlist ---")
            for i in range(len(waitlist)):
                w = waitlist[i]
                print(str(i + 1) + ".", w["name"], "| Email:", w["email"], "| Phone:", w["phone"])
            return
    print("Event Not Found")

def viewCertificateStatus():
    data = loadData()
    event_id = input("Enter Event ID: ").strip()
    for event in data["events"]:
        if str(event["event_id"]) == str(event_id):
            attendees = event.get("attendees", [])
            if not attendees:
                print("No Attendees")
                return
            print("\n--- Certificate Status ---")
            for a in attendees:
                print("Name:", a["name"])
                print("Ticket:", a["ticket_id"])
                print("Attendance:", a.get("status", "Registered"))
                print("Certificate:", a.get("certificate", "Not Eligible"))
                print("---")
            return
    print("Event Not Found")

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
        print("13. View Notifications")
        print("14. View Waitlist")
        print("15. Cancel Registration")
        print("16. View Certificate Status")
        print("17. Exit")

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
            viewNotifications()
        elif choice == "14":
            viewWaitlist()
        elif choice == "15":
            cancelRegistration()
        elif choice == "16":
            viewCertificateStatus()
        elif choice == "17":
            print("Exiting program.")
            break
        else:
            print("Wrong choice")

if __name__ == "__main__":
    main()
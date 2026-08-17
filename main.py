import json
import os
from event import Event

FILE_NAME = "data.json"

def loadEvents():
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME,"r") as file:
            return json.load(file)
    except:
        return []

def saveEvents(events):
    with open(FILE_NAME,"w") as file:
        json.dump(events,file,indent=4)

def createEvent():
    events=loadEvents()
    event_id=input("Enter Event ID: ").strip()
    if not event_id:
        print("ID empty")
        return
    for event in events:
        if event["event_id"]==event_id:
            print("ID exists")
            return
    event_name=input("Enter Name: ").strip()
    if not event_name:
        print("Name empty")
        return
    date=input("Enter Date: ").strip()
    time=input("Enter Time: ").strip()
    venue=input("Enter Venue: ").strip()
    resources=input("Enter Resources: ").strip()
    status="Planning"
    new_event=Event(event_id,event_name,date,time,venue,resources,status)
    events.append(new_event.to_dict())
    saveEvents(events)
    print("Event created")

def viewEvents():
    events=loadEvents()
    if not events:
        print("No events")
        return
    for event in events:
        print("ID:",event['event_id'])
        print("Name:",event['event_name'])
        print("Date:",event['date'])
        print("Time:",event['time'])
        print("Venue:",event['venue'])
        print("Resources:",event['resources'])
        print("Status:",event['status'])
        print("---")

def searchEvent():
    events=loadEvents()
    event_id=input("Enter ID: ").strip()
    for event in events:
        if event["event_id"]==event_id:
            print("ID:",event['event_id'])
            print("Name:",event['event_name'])
            print("Date:",event['date'])
            print("Time:",event['time'])
            print("Venue:",event['venue'])
            print("Resources:",event['resources'])
            print("Status:",event['status'])
            return
    print("Event not found")

def updateEvent():
    events=loadEvents()
    event_id=input("Enter ID: ").strip()
    for event in events:
        if event["event_id"]==event_id:
            new_name=input("New Name: ").strip()
            if new_name:
                event["event_name"]=new_name
            new_date=input("New Date: ").strip()
            if new_date:
                event["date"]=new_date
            new_time=input("New Time: ").strip()
            if new_time:
                event["time"]=new_time
            new_venue=input("New Venue: ").strip()
            if new_venue:
                event["venue"]=new_venue
            new_resources=input("New Resources: ").strip()
            if new_resources:
                event["resources"]=new_resources
            new_status=input("New Status: ").strip()
            if new_status:
                event["status"]=new_status
            saveEvents(events)
            print("Updated")
            return
    print("Event not found")

def deleteEvent():
    events=loadEvents()
    event_id=input("Enter ID: ").strip()
    for i in range(len(events)):
        if events[i]["event_id"]==event_id:
            del events[i]
            saveEvents(events)
            print("Deleted")
            return
    print("Event not found")

def main():
    while True:
        print("\n1.Create\n2.View\n3.Search\n4.Update\n5.Delete\n6.Exit")
        choice=input("Choice: ").strip()
        if choice=="1":
            createEvent()
        elif choice=="2":
            viewEvents()
        elif choice=="3":
            searchEvent()
        elif choice=="4":
            updateEvent()
        elif choice=="5":
            deleteEvent()
        elif choice=="6":
            print("Bye")
            break
        else:
            print("Wrong choice")

if __name__=="__main__":
    main()
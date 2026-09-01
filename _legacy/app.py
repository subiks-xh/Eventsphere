from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import datetime
from main import loadData, saveData
from event import Event, Attendee, Vendor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventsphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'eventsphere_secret_key'  # Needed for flash messages

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route('/')
def home():
    data = loadData()
    events = data.get('events', [])
    total_events = len(events)
    total_registrations = sum(len(e.get('attendees', [])) for e in events)
    total_checked_in = sum(1 for e in events for a in e.get('attendees', []) if a.get('status') == 'Checked In')
    
    return render_template('index.html', 
                           events=events,
                           total_events=total_events,
                           total_registrations=total_registrations,
                           total_checked_in=total_checked_in)

@app.route('/events')
def events_list():
    data = loadData()
    return render_template('events.html', events=data.get('events', []))

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        data = loadData()
        event_id = request.form.get('event_id').strip()
        
        for event in data['events']:
            if str(event['event_id']) == str(event_id):
                flash("Event ID already exists.")
                return redirect(url_for('create_event'))
                
        event_name = request.form.get('event_name').strip()
        date = request.form.get('date').strip()
        time = request.form.get('time').strip()
        venue = request.form.get('venue').strip()
        resources = request.form.get('resources').strip()
        try:
            capacity = int(request.form.get('capacity').strip())
        except ValueError:
            capacity = 0
            
        new_event = Event(event_id, event_name, date, time, venue, resources, "Planning", capacity=capacity)
        data['events'].append(new_event.to_dict())
        saveData(data)
        flash("Event created successfully!")
        return redirect(url_for('events_list'))
        
    return render_template('create_event.html')

@app.route('/event/<event_id>')
def event_details(event_id):
    data = loadData()
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            return render_template('event_details.html', event=event)
    flash("Event not found.")
    return redirect(url_for('events_list'))

@app.route('/register/<event_id>', methods=['GET', 'POST'])
def register(event_id):
    data = loadData()
    selected_event = None
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            selected_event = event
            break
            
    if not selected_event:
        flash("Event not found.")
        return redirect(url_for('events_list'))
        
    if request.method == 'POST':
        reg_id = request.form.get('reg_id').strip()
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        phone = request.form.get('phone').strip()
        
        if 'attendees' not in selected_event:
            selected_event['attendees'] = []
        if 'waitlist' not in selected_event:
            selected_event['waitlist'] = []
            
        for a in selected_event['attendees']:
            if a['email'] == email:
                flash("Email already registered.")
                return redirect(url_for('register', event_id=event_id))
                
        for w in selected_event['waitlist']:
            if w['email'] == email:
                flash("Email already on waitlist.")
                return redirect(url_for('register', event_id=event_id))
                
        capacity = selected_event.get('capacity', 0)
        current_count = len(selected_event['attendees'])
        
        join_waitlist = request.form.get('join_waitlist') == 'yes'
        
        if capacity > 0 and current_count >= capacity:
            if join_waitlist:
                selected_event['waitlist'].append({'reg_id': reg_id, 'name': name, 'email': email, 'phone': phone})
                saveData(data)
                flash(f"Event is full. You have been added to the waitlist.")
                return redirect(url_for('event_details', event_id=event_id))
            else:
                return render_template('register.html', event=selected_event, is_full=True)
                
        ticket_id = "TKT" + str(data['ticket_counter'])
        data['ticket_counter'] += 1
        
        new_attendee = Attendee(reg_id, name, email, phone, ticket_id)
        selected_event['attendees'].append(new_attendee.to_dict())
        
        if 'notifications' not in data:
            data['notifications'] = []
        data['notifications'].append(f"Registration successful for {selected_event['event_name']}. Ticket: {ticket_id}")
        
        saveData(data)
        flash(f"Registration Successful! Ticket ID: {ticket_id}")
        return redirect(url_for('event_details', event_id=event_id))
        
    return render_template('register.html', event=selected_event, is_full=False)

@app.route('/attendees/<event_id>')
def attendees(event_id):
    data = loadData()
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            return render_template('attendees.html', event=event)
    flash("Event not found.")
    return redirect(url_for('events_list'))

@app.route('/attendance/<event_id>', methods=['GET', 'POST'])
def attendance(event_id):
    data = loadData()
    selected_event = None
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            selected_event = event
            break
            
    if not selected_event:
        flash("Event not found.")
        return redirect(url_for('events_list'))
        
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id').strip()
        for a in selected_event.get('attendees', []):
            if str(a.get('ticket_id')) == str(ticket_id):
                if a.get('status') == 'Checked In':
                    flash("Already Checked In.")
                    return redirect(url_for('attendance', event_id=event_id))
                
                a['status'] = 'Checked In'
                a['checkin_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                a['certificate'] = 'Eligible'
                saveData(data)
                flash(f"Attendance Updated. Check-in Time: {a['checkin_time']}")
                return redirect(url_for('attendance', event_id=event_id))
                
        flash("Invalid Ticket ID.")
        return redirect(url_for('attendance', event_id=event_id))
        
    return render_template('attendance.html', event=selected_event)

@app.route('/waitlist/<event_id>')
def waitlist(event_id):
    data = loadData()
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            return render_template('waitlist.html', event=event)
    flash("Event not found.")
    return redirect(url_for('events_list'))

@app.route('/cancel_registration/<event_id>/<ticket_id>', methods=['POST'])
def cancel_registration(event_id, ticket_id):
    data = loadData()
    selected_event = None
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            selected_event = event
            break
            
    if selected_event:
        attendees_list = selected_event.get('attendees', [])
        found_attendee = None
        for a in attendees_list:
            if str(a.get('ticket_id')) == str(ticket_id):
                found_attendee = a
                break
                
        if found_attendee:
            attendees_list.remove(found_attendee)
            flash(f"Registration cancelled for {found_attendee.get('name')}.")
            
            waitlist_list = selected_event.get('waitlist', [])
            if waitlist_list:
                next_person = waitlist_list.pop(0)
                new_ticket = "TKT" + str(data['ticket_counter'])
                data['ticket_counter'] += 1
                promoted = Attendee(next_person['reg_id'], next_person['name'], next_person['email'], next_person['phone'], new_ticket)
                selected_event['attendees'].append(promoted.to_dict())
                
                if 'notifications' not in data:
                    data['notifications'] = []
                data['notifications'].append(f"Your registration for {selected_event['event_name']} has been confirmed from the waitlist. Ticket: {new_ticket}")
                flash(f"{next_person['name']} promoted from waitlist with ticket {new_ticket}.")
                
            saveData(data)
            
    return redirect(url_for('attendees', event_id=event_id))

@app.route('/notifications')
def notifications():
    data = loadData()
    return render_template('notifications.html', notifications=data.get('notifications', []))

@app.route('/vendors', methods=['GET', 'POST'])
def vendors():
    data = loadData()
    if request.method == 'POST':
        vendor_id = request.form.get('vendor_id').strip()
        for v in data.get('vendors', []):
            if str(v.get('vendor_id')) == str(vendor_id):
                flash("Vendor ID already exists.")
                return redirect(url_for('vendors'))
                
        name = request.form.get('name').strip()
        service = request.form.get('service').strip()
        new_vendor = Vendor(vendor_id, name, service)
        data.setdefault('vendors', []).append(new_vendor.to_dict())
        saveData(data)
        flash("Vendor added successfully.")
        return redirect(url_for('vendors'))
        
    return render_template('vendors.html', vendors=data.get('vendors', []))

@app.route('/assign_vendor/<event_id>', methods=['GET', 'POST'])
def assign_vendor(event_id):
    data = loadData()
    selected_event = None
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            selected_event = event
            break
            
    if not selected_event:
        flash("Event not found.")
        return redirect(url_for('events_list'))
        
    if request.method == 'POST':
        vendor_id = request.form.get('vendor_id')
        selected_vendor = None
        for v in data.get('vendors', []):
            if str(v.get('vendor_id')) == str(vendor_id):
                selected_vendor = v
                break
                
        if not selected_vendor:
            flash("Vendor not found.")
            return redirect(url_for('assign_vendor', event_id=event_id))
            
        if 'vendors' not in selected_event:
            selected_event['vendors'] = []
            
        for v in selected_event['vendors']:
            if str(v.get('vendor_id')) == str(vendor_id):
                flash("Vendor already assigned to this event.")
                return redirect(url_for('assign_vendor', event_id=event_id))
                
        selected_event['vendors'].append(selected_vendor)
        saveData(data)
        flash("Vendor assigned successfully.")
        return redirect(url_for('event_details', event_id=event_id))
        
    return render_template('assign_vendor.html', event=selected_event, vendors=data.get('vendors', []))

@app.route('/certificate_status/<event_id>')
def certificate_status(event_id):
    data = loadData()
    for event in data['events']:
        if str(event['event_id']) == str(event_id):
            return render_template('certificate_status.html', event=event)
    flash("Event not found.")
    return redirect(url_for('events_list'))

@app.route('/report')
def report():
    data = loadData()
    return render_template('report.html', events=data.get('events', []))

if __name__ == '__main__':
    app.run(debug=True)

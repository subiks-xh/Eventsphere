# EventSphere - QA Walkthrough & Defect Log

This document tracks the end-to-end interactive QA session for EventSphere across all roles and milestones (M1–M4 + Signature Features).

## Session Details
- **Environment**: Local Development
- **Database**: Freshly seeded
- **Status**: IN PROGRESS

## Defect Log
*(Any defects found during the interactive session will be logged here with their fix status)*

| Defect | Section/Step | Status | Fix Details |
|--------|--------------|--------|-------------|
| `UndefinedError: kpis is undefined` | Section 0 / Navbar | **FIXED** | `main.py` was directly rendering dashboard templates without passing data. Changed to `redirect(url_for('role.dashboard'))` to route through proper controller logic. |
| `TypeError: cannot unpack non-iterable bool object` | Section 2 / Step 1 (Create Event) | **FIXED** | `venue.has_conflict()` returns a boolean, but `events.py` tried to unpack it as a tuple. Refactored `events.py` to use `get_conflicting_events()` separately if a conflict is found. |
| `400 Bad Request on Publish` | Section 2 / Step 3 (Publish) | **FIXED** | The Publish, Cancel, and Register buttons on the Event Details page used `POST` forms but lacked a `csrf_token()`. Added hidden CSRF inputs to all 5 forms in `detail.html`. |
| `403 Forbidden on Register` | Phase 2 / Register | **FIXED** | The `before_request` hook in `events.py` blocked all POST requests for non-Organizers/Admins, completely preventing Attendees from registering. Whitelisted `events.register` and `events.cancel_registration` in the hook. |
| `Missing Vendor/Resource UI` | Phase 3 / Organizer View | **FIXED** | The Organizer UI on the Event Details page lacked buttons to navigate to Vendor and Resource management. Added `Manage Vendors` and `Manage Resources` buttons to the Registration Info sidebar in `detail.html`. |
| `400 Bad Request on Assign` | Phase 3 / Vendor Assign | **FIXED** | Similar to the Publish button, the form in `vendors.html` for assigning a vendor lacked a `csrf_token()`. I added the tokens to the assignment and removal forms. Also proactively added the `update_status` form to the Vendor Dashboard so the vendor can accept the assignment. |
| `NameError: EventVendor is not defined` | Phase 3 / Vendor Login | **FIXED** | When logging in as the Vendor, the Vendor Dashboard raised an exception because `app/models/vendor.py` referenced `EventVendor` in the `assigned_events` property without importing it. Imported the missing model. |

---

## Section 0: Unauthenticated (Public Browsing)
*Focus: Homepage, Event Discovery, Event Details, Public routing*

1. **View Homepage**
   - **Action**: Navigate to `http://127.0.0.1:5000/`. Scroll through the page.
   - **Expected Result**: The homepage should load successfully. You should see a hero banner, a "Featured Events" section displaying a grid of published events with dates and categories, and navigation links at the top (Events, Login, Register).

2. **Browse All Events**
   - **Action**: Click the `Events` link in the top navigation bar.
   - **Expected Result**: A paginated list or grid of all upcoming published events should appear.

3. **Filter Events (If applicable)**
   - **Action**: Use the category dropdown or search bar to filter by "Conference" or any visible category, then submit.
   - **Expected Result**: The events grid should update to show only events matching the filter.

4. **View Event Details**
   - **Action**: Click on the title or "View Details" button of any event in the list.
   - **Expected Result**: You are redirected to the event detail page (`/events/<id>`). It should show the event name, date, time, venue, description, organizer info, and a "Register" button. Since you are unauthenticated, clicking the Register button or a warning nearby should prompt you to log in.

---

## Section 1: Attendee
*(To be detailed during the session)*

## Section 2: Organizer (Your Account: Krishna)
*Focus: Event Creation, Conflict Detection, Budgets, Analytics, Reporting*

Since you are logged in as an **Organizer**, let's test your dashboard and event management capabilities. Please follow these exact steps and let me know the result of each (Pass / Fail / Errors).

1. **Create an Event (Testing Conflict Detection)**
   - **Action**: On your dashboard, click the `Create Event` button (or go to `Organizer > Create Event`).
   - Fill in the following details:
     - **Name**: `Krishna's Tech Summit`
     - **Category**: `Conference`
     - **Description**: `Testing the conflict detector.`
     - **Date**: Choose tomorrow's date.
     - **Start Time**: `09:00` (AM)
     - **End Time**: `17:00` (5:00 PM)
     - **Venue**: Select the first venue in the dropdown (remember which one you picked!).
     - **Capacity**: `100`
     - **Registration Deadline**: Choose today's date.
   - Click **Create Event**.
   - **Expected Result**: The event should be created successfully, and you should be redirected to the event details or dashboard. Note: If the seeder already booked this venue for tomorrow, you might see a conflict error—this means conflict detection works! If it creates successfully, that's fine too.

2. **Test Deliberate Conflict Detection**
   - **Action**: Click `Create Event` again. Try to create *another* event with the exact same Date, Start Time, End Time, and Venue as the one you just created.
   - **Expected Result**: The system MUST block you and display an error message saying there is a scheduling conflict at that venue.

3. **Publish the Event**
   - **Action**: Go to `Organizer > My Events`. Click on `Krishna's Tech Summit`. Find the option to change the status to `PUBLISHED` (or click a "Publish" button if available).
   - **Expected Result**: The event status updates to Published, making it visible to the public.

4. **Set Up a Budget**
   - **Action**: On the event management page for `Krishna's Tech Summit`, navigate to the `Budget` tab.
   - **Action**: Add a new budget item.
     - **Category**: `Catering`
     - **Amount**: `500`
     - **Description**: `Lunch for attendees`
   - **Expected Result**: The budget item should be added and the total budget utilization chart should update.

5. **View Analytics & Export Report**
   - **Action**: From the Organizer dropdown, go to your Analytics or Statistics page.
   - **Expected Result**: You should see charts/KPIs.
   - **Action**: Click the `Export PDF` or `Export CSV` button.
   - **Expected Result**: A file should download successfully containing your event data.

Please run through these 5 steps and let me know what happens!

## Section 3: Vendor
*(To be detailed during the session)*

## Section 4: Admin
*(To be detailed during the session)*

## Section 5: Cross-cutting & Advanced Features
*(To be detailed during the session)*

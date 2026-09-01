# EventSphere - Usability QA Checklist

Use this checklist to manually verify the core workflows of EventSphere prior to a production release.

## 1. Authentication & Roles
- [ ] New user can register successfully.
- [ ] User can log in.
- [ ] User with `Admin` role can access the `/admin` dashboard.
- [ ] User without `Admin` role is denied access to `/admin` (receives 403 Forbidden).
- [ ] User can log out.

## 2. Event Creation & Management
- [ ] Organizer can create a new event.
- [ ] Forecasted attendance appears correctly when Category and Capacity are filled.
- [ ] Organizer can view the event on their dashboard.
- [ ] Organizer can edit event details.
- [ ] Unauthorized users cannot edit an event they do not own.

## 3. Budget & Approvals
- [ ] Organizer can view the budget dashboard for their event.
- [ ] Organizer can update the total allocated budget.
- [ ] Submitting an expense < ₹50,000 auto-approves.
- [ ] Submitting an expense >= ₹50,000 creates a pending `ApprovalRequest`.
- [ ] Organizer/Admin can approve or reject the `ApprovalRequest` from the inbox.
- [ ] Organizer can download the Budget CSV.

## 4. Ticketing & Check-in
- [ ] Attendee can register for an upcoming event.
- [ ] Attendee receives a Ticket ID.
- [ ] Organizer can check-in an attendee using their Ticket ID.
- [ ] Checking in the same attendee twice yields an error message.

## 5. API layer
- [ ] `GET /api/v1/events` returns a paginated list of events.
- [ ] `POST /api/v1/events` creates an event with proper auth.
- [ ] `GET /api/v1/events/forecast` returns a JSON object with the expected attendance forecast.

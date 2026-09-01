# EventSphere - REST API (v1)

EventSphere provides a `/api/v1` prefix for REST endpoints, typically used by interactive frontend widgets. All endpoints require authentication via `Flask-Login` cookies (`@login_required`) unless stated otherwise.

## Endpoints

### 1. `GET /api/v1/events`
Lists paginated events.
- **Auth required**: No.
- **Parameters**: `page`, `per_page`.
- **Response**: JSON array of events and metadata.

### 2. `GET /api/v1/events/<id>`
Retrieves details for a specific event.
- **Auth required**: No.
- **Response**: JSON representation of the event.

### 3. `POST /api/v1/events`
Creates a new event.
- **Auth required**: Yes (`Organizer` or `Admin`).
- **Body**: JSON containing `name`, `date`, `category`, `capacity`, etc.
- **Response**: `201 Created` with event ID.

### 4. `PUT /api/v1/events/<id>`
Updates an existing event.
- **Auth required**: Yes (must be the Organizer of the event, or an Admin).
- **Body**: JSON with updated fields.
- **Response**: `200 OK` or `403 Forbidden`.

### 5. `DELETE /api/v1/events/<id>`
Deletes an event.
- **Auth required**: Yes (must be the Organizer of the event, or an Admin).
- **Response**: `200 OK`.

### 6. `GET /api/v1/events/forecast`
Forecasts expected attendance for event planning.
- **Auth required**: Yes (`Organizer` or `Admin`).
- **Parameters**: `category` (string), `capacity` (int).
- **Response**: JSON `{ "forecast": 75, "capacity": 100, "category": "conference" }`.

### 7. `GET /api/v1/events/<id>/budget`
Retrieves budget metrics for an event.
- **Auth required**: Yes (must be the Organizer of the event, or an Admin).
- **Response**: JSON containing `total_amount`, `approved_expenses`, `remaining`, `utilization_percentage`.

### 8. `GET /api/v1/notifications/unread_count`
Gets the number of unread notifications for the current user.
- **Auth required**: Yes.
- **Response**: JSON `{ "unread_count": 5 }`.

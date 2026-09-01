import json

def test_get_events_unauthenticated(client):
    """Test getting public events without login."""
    response = client.get('/api/v1/events')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'events' in data
    assert 'meta' in data

def test_create_event_unauthenticated(client):
    """Test creating an event without login fails."""
    response = client.post('/api/v1/events', json={
        'name': 'Test Event',
        'date': '2025-01-01'
    })
    # Should redirect to login (302) or return 401 depending on Flask-Login setup for API
    assert response.status_code in [302, 401]

def test_api_forecast(client, init_database):
    """Test the forecasting endpoint."""
    with client:
        # Login as admin
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'adminpass'
        })
        
        response = client.get('/api/v1/events/forecast?category=conference&capacity=100')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['forecast'] == 75 # 75% fallback when no history
        assert data['capacity'] == 100
        assert data['category'] == 'conference'

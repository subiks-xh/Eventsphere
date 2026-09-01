def test_login_page_renders(client):
    """Test that login page renders correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client, init_database):
    """Test successful login."""
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'adminpass'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Logout' in response.data

def test_login_failure(client, init_database):
    """Test login with incorrect password."""
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username' in response.data

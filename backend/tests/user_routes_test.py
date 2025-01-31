import requests

BASE_URL = "http://localhost:5000/users"

# Test login
def test_login():
    print("\nTesting /login endpoint...")
    payload = {"piToken": "User1"}  # Replace 'mock_token' with a valid token
    response = requests.post(f"{BASE_URL}/login", json=payload)

    if response.status_code == 200:
        print("Login successful!")
        print("Response:", response.json())
        print("Response Cookies:", response.cookies)
        return response.cookies
    else:
        print("Login failed. Status Code:", response.status_code)
        print("Error Response:", response.text)
        return None

# Test get profile
def test_get_profile(cookies):
    print("\nTesting /profile (GET) endpoint...")
    headers = {"Authorization": "Bearer mock_token"}
    print("Cookies", cookies)
    response = requests.get(f"{BASE_URL}/profile", cookies=cookies, headers=headers)

    if response.status_code == 200:
        print("Profile data:", response.json())
    else:
        print("Failed to get profile. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test update profile
def test_update_profile(cookies):
    print("\nTesting /profile (PUT) endpoint...")
    payload = {"name": "Updated Name", "email": "updated1@example.com"}
    headers = {"Authorization": "Bearer mock_token"}
    response = requests.put(f"{BASE_URL}/profile", json=payload, cookies=cookies, headers=headers)

    if response.status_code == 200:
        print("Profile updated:", response.json())
    else:
        print("Failed to update profile. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test logout
def test_logout(cookies):
    print("\nTesting /logout endpoint...")
    headers = {"Authorization": "Bearer mock_token"}
    response = requests.post(f"{BASE_URL}/logout", cookies=cookies, headers=headers)

    if response.status_code == 200:
        print("Logout successful:", response.json())
    else:
        print("Failed to logout. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test validate token
def test_validate_token():
    print("\nTesting /validate-token endpoint...")
    payload = {"pi_token": "Bearer mock_token"}  # Replace 'mock_token' with a valid token
    response = requests.post(f"{BASE_URL}/validate-token", json=payload)

    if response.status_code == 200:
        print("Token validation successful:", response.json())
    else:
        print("Failed to validate token. Status Code:", response.status_code)
        print("Error Response:", response.text)

if __name__ == "__main__":
    # Step 1: Test login and get session cookies
    cookies = test_login()
    if not cookies:
        print("Login failed. Aborting further tests.")
        exit(1)

    # Step 2: Test other endpoints
    test_get_profile(cookies)
    test_update_profile(cookies)
    test_logout(cookies)

    # Step 3: Test validate token (doesn't require session cookies)
    test_validate_token()

import requests

BASE_URL = "http://localhost:5000"

# Test login to get session cookies
def test_login():
    print("\nTesting /login endpoint...")
    payload = {"piToken": "User1"}  # Replace 'User1' with valid piToken
    response = requests.post(f"{BASE_URL}/users/login", json=payload)

    if response.status_code == 200:
        print("Login successful!")
        print("Response Cookies:", response.cookies)
        return response.cookies
    else:
        print("Login failed. Status Code:", response.status_code)
        print("Error Response:", response.text)
        return None


# Test Create Notification
def test_create_notification(cookies):
    print("\nTesting /notification/create (POST) endpoint...")
    notification_data = {
        "message": "Test notification message",
        "type": "info",
        "status": "unread",
        "link": "http://example.com",
        "relatedEntityId": 123,
        "category": "general",
        "isActionable": True,
        "expiresAt": "2025-02-20T00:00:00Z",
        "actorUserId": "b4597edb-f707-476c-bde9-"
    }
    response = requests.post(f"{BASE_URL}/notification/create", json=notification_data, cookies=cookies)

    if response.status_code == 201:
        print("Notification created successfully:", response.json())
    else:
        print("Failed to create notification. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Notifications by User
def test_get_notifications_by_user(cookies):
    print("\nTesting /notification/list (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/notification/list", cookies=cookies)

    if response.status_code == 200:
        print("Notifications by user:", response.json())
    else:
        print("Failed to fetch notifications for user. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Update Notification Status
def test_update_notification_status(cookies, notification_id, new_status):
    print(f"\nTesting /notification/update (PUT) endpoint for Notification {notification_id}...")
    response = requests.put(
        f"{BASE_URL}/notification/update", 
        json={"notificationId": notification_id, "status": new_status}, 
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"Notification status updated for {notification_id}: {response.json()}")
    else:
        print(f"Failed to update status for notification {notification_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Delete Notification
def test_delete_notification(cookies, notification_id):
    print(f"\nTesting /notification/delete (DELETE) endpoint for Notification {notification_id}...")
    response = requests.delete(
        f"{BASE_URL}/notification/delete", 
        json={"notificationId": notification_id}, 
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"Notification deleted for {notification_id}: {response.json()}")
    else:
        print(f"Failed to delete notification {notification_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


if __name__ == "__main__":
    # Step 1: Login and get session cookies
    cookies = test_login()
    if not cookies:
        print("Login failed. Aborting further tests.")
        exit(1)

    # Step 2: Test notification endpoints
    test_create_notification(cookies)
    test_get_notifications_by_user(cookies)

    # Example notification status update
    notification_id = "notification_id_example"
    test_update_notification_status(cookies, notification_id, "read")

    # Example notification deletion
    test_delete_notification(cookies, notification_id)

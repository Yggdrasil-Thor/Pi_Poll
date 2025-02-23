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


# Test Create Payment
def test_create_payment(cookies):
    print("\nTesting /payment (POST) endpoint...")
    payment_data = {
        "pollId": 12345,
        "amount": 100.0,
        "paymentType": "creation",  # Can be 'update', 'voting', etc.
        "transactionId": "txn_123456789"
    }
    response = requests.post(f"{BASE_URL}/payment/create", json=payment_data, cookies=cookies)

    if response.status_code == 201:
        print("Payment created successfully:", response.json())
    else:
        print("Failed to create payment. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Payments by User
def test_get_payments_by_user(cookies):
    print("\nTesting /payment/user (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/payment/user", cookies=cookies)

    if response.status_code == 200:
        print("Payments by user:", response.json())
    else:
        print("Failed to fetch payments for user. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Payments for Poll
def test_get_payments_for_poll(cookies, poll_id):
    print(f"\nTesting /payment/poll/{poll_id} (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/payment/poll/{poll_id}", cookies=cookies)

    if response.status_code == 200:
        print(f"Payments for Poll {poll_id}:", response.json())
    else:
        print(f"Failed to fetch payments for poll {poll_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Total Payment for Poll
def test_get_total_payment_for_poll(cookies, poll_id):
    print(f"\nTesting /payment/poll/{poll_id}/total (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/payment/poll/{poll_id}/total", cookies=cookies)

    if response.status_code == 200:
        print(f"Total payments for Poll {poll_id}: {response.json()}")
    else:
        print(f"Failed to calculate total payment for poll {poll_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Update Payment Status
def test_update_payment_status(cookies, payment_id, new_status):
    print(f"\nTesting /payment/update/{payment_id} (PUT) endpoint...")
    response = requests.put(
        f"{BASE_URL}/payment/update/{payment_id}", 
        json={"status": new_status}, 
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"Payment status updated for {payment_id}: {response.json()}")
    else:
        print(f"Failed to update status for payment {payment_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Check Payment Required
def test_check_payment_required(cookies, poll_id, action_type):
    print(f"\nTesting /payment/check (GET) endpoint for Poll {poll_id} with action_type {action_type}...")
    response = requests.get(
        f"{BASE_URL}/payment/check",
        params={"poll_id": poll_id, "action_type": action_type},
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"Payment required check for Poll {poll_id}: {response.json()}")
    else:
        print(f"Failed to check payment requirement. Status Code:", response.status_code)
        print("Error Response:", response.text)


if __name__ == "__main__":
    # Step 1: Login and get session cookies
    cookies = test_login()
    if not cookies:
        print("Login failed. Aborting further tests.")
        exit(1)

    # Step 2: Test payment endpoints
    test_create_payment(cookies)
    test_get_payments_by_user(cookies)

    poll_id = 12345
    test_get_payments_for_poll(cookies, poll_id)
    test_get_total_payment_for_poll(cookies, poll_id)

    # Example payment status update
    payment_id = "67a18a9f2085ed65f81f005b"
    test_update_payment_status(cookies, payment_id, "completed")

    # Check if payment is required for a specific poll action
    #test_check_payment_required(cookies, poll_id, "creation")

import requests

BASE_URL = "http://localhost:5000"

# Test login to get session cookies
def test_login():
    print("\nTesting /login endpoint...")
    payload = {"piToken": "User1"}  # Replace 'User1' with valid piToken
    response = requests.post(f"{BASE_URL}/users/login", json=payload)

    if response.status_code == 200:
        print("Login successful!")
        return response.cookies
    else:
        print("Login failed. Status Code:", response.status_code)
        print("Error Response:", response.text)
        return None


# Test Create Poll
def test_create_poll(cookies):
    print("\nTesting /poll/create endpoint...")
    poll_data = {
        "title": "Best Programming Language?",
        "options": ["Python", "JavaScript", "Java", "C++"],
        "description":"desc1",
        "expiresAt": "2025-12-31T23:59:59Z",
        "topics": ["programming"],
        "createdBy":"UserId",
        "requiresPaymentForCreation":"true",
        "paymentAmountForCreation":10,
        "paymentId":"67a18a9f2085ed65f81f005b",
        "requiredVotes":3

    }
    response = requests.post(f"{BASE_URL}/poll/create", json=poll_data, cookies=cookies)

    if response.status_code == 201:
        print("Poll created successfully:", response.json())
        return response.json().get("data", {}).get("pollId")
    else:
        print("Failed to create poll. Status Code:", response.status_code)
        print("Error Response:", response.text)
        return None


# Test Extend Poll Votes
def test_extend_poll_votes(cookies, poll_id):
    print(f"\nTesting /poll/extendVotes/{poll_id} endpoint...")
    extend_data = {
        "additionalVotes": 5,
        "requires_payment_for_update": True,
        "payment_amount_for_update": 10,
        "paymentId": "txn_123"
    }
    response = requests.post(f"{BASE_URL}/poll/extendVotes/{poll_id}", json=extend_data, cookies=cookies)

    if response.status_code == 200:
        print("Poll votes extended successfully:", response.json())
    else:
        print("Failed to extend poll votes. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Update Poll
def test_update_poll(cookies, poll_id):
    print(f"\nTesting /poll/update/{poll_id} endpoint...")
    update_data = {
        "title": "Updated Poll Title"
    }
    response = requests.put(f"{BASE_URL}/poll/update/{poll_id}", json=update_data, cookies=cookies)

    if response.status_code == 200:
        print("Poll updated successfully:", response.json())
    else:
        print("Failed to update poll. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Add Vote
def test_add_vote(cookies, poll_id, option_index):
    print(f"\nTesting /poll/vote/{poll_id} endpoint...")
    vote_data = {"optionId": option_index}
    response = requests.post(f"{BASE_URL}/poll/vote/{poll_id}", json=vote_data, cookies=cookies)

    if response.status_code == 200:
        print("Vote added successfully:", response.json())
    else:
        print("Failed to add vote. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Poll by ID
def test_get_poll(cookies, poll_id):
    print(f"\nTesting /poll/{poll_id} endpoint...")
    response = requests.get(f"{BASE_URL}/poll/{poll_id}", cookies=cookies)

    if response.status_code == 200:
        print("Poll details:", response.json())
    else:
        print("Failed to fetch poll. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get User's Polls
def test_get_user_polls(cookies, user_id):
    print(f"\nTesting users/{user_id}/polls endpoint...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/polls", cookies=cookies)

    if response.status_code == 200:
        print("User polls:", response.json())
    else:
        print("Failed to fetch user's polls. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Delete Poll
def test_delete_poll(cookies, poll_id):
    print(f"\nTesting /poll/delete/{poll_id} endpoint...")
    response = requests.delete(f"{BASE_URL}/poll/delete/{poll_id}", cookies=cookies)

    if response.status_code == 200:
        print("Poll deleted successfully:", response.json())
    else:
        print("Failed to delete poll. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Active Polls
def test_get_active_polls(cookies):
    print("\nTesting /poll/active endpoint...")
    response = requests.get(f"{BASE_URL}/poll/active", cookies=cookies)

    if response.status_code == 200:
        print("Active polls:", response.json())
    else:
        print("Failed to fetch active polls. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Polls by Topic
def test_get_polls_by_topic(cookies, topic):
    print(f"\nTesting /poll/topic/{topic} endpoint...")
    response = requests.get(f"{BASE_URL}/poll/topic/{topic}", cookies=cookies)

    if response.status_code == 200:
        print(f"Polls under topic '{topic}':", response.json())
    else:
        print(f"Failed to fetch polls for topic '{topic}'. Status Code:", response.status_code)
        print("Error Response:", response.text)


if __name__ == "__main__":
    # Step 1: Login and get session cookies
    cookies = test_login()
    if not cookies:
        print("Login failed. Aborting further tests.")
        exit(1)

    # Step 2: Test creating a poll
    poll_id = test_create_poll(cookies)
    if not poll_id:
        print("Poll creation failed. Aborting further tests.")
        exit(1)

    # Step 3: Test other poll-related endpoints
    test_update_poll(cookies, poll_id)
    test_add_vote(cookies, poll_id, option_index=0)
    test_get_poll(cookies, poll_id)
    test_extend_poll_votes(cookies, poll_id)
    test_get_active_polls(cookies)
    test_get_user_polls(cookies,"9eee8705-2f16-49fe-9a72-")
    test_get_polls_by_topic(cookies, "programming")
    test_delete_poll(cookies, poll_id)

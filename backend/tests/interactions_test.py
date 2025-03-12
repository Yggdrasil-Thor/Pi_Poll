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

# Test Log Interaction (view, click, vote, comment)
def test_log_interaction(cookies, action):
    print(f"\nTesting /interaction/log/{action} endpoint...")
    interaction_data = {
        "pollId": "67cbeb5e7c5bbf3d9f98f52f",
        "actionType": action
    }
    response = requests.post(f"{BASE_URL}/interaction/log/{action}", json=interaction_data, cookies=cookies)

    if response.status_code == 201:
        print(f"Interaction '{action}' logged successfully:", response.json())
    else:
        print(f"Failed to log '{action}' interaction. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test Get User Interactions
def test_get_user_interactions(cookies, user_id):
    print(f"\nTesting /interaction/user/{user_id} endpoint...")
    response = requests.get(f"{BASE_URL}/interaction/user/{user_id}", cookies=cookies)

    if response.status_code == 200:
        print("User interactions:", response.json())
    else:
        print("Failed to fetch user interactions. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test Get Poll Interactions
def test_get_poll_interactions(cookies, poll_id):
    print(f"\nTesting /interaction/poll/{poll_id} endpoint...")
    response = requests.get(f"{BASE_URL}/interaction/poll/{poll_id}", cookies=cookies)

    if response.status_code == 200:
        print(f"Poll interactions for {poll_id}:", response.json())
    else:
        print("Failed to fetch poll interactions. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test Get Interactions by Type (e.g., vote, comment)
def test_get_interactions_by_type(cookies, action_type):
    print(f"\nTesting /interaction/type/{action_type} endpoint...")
    response = requests.get(f"{BASE_URL}/interaction/type/{action_type}", cookies=cookies)

    if response.status_code == 200:
        print(f"Interactions of type '{action_type}':", response.json())
    else:
        print(f"Failed to fetch interactions by type '{action_type}'. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test Poll Preference (like, dislike, etc.)
def test_poll_preference(cookies, action):
    print(f"\nTesting /interaction/poll/{action} endpoint...")
    interaction_data = {
        "pollId": "67cbeb5e7c5bbf3d9f98f52f"
    }
    response = requests.post(f"{BASE_URL}/interaction/poll/{action}", json=interaction_data, cookies=cookies)

    if response.status_code == 200:
        print(f"Poll preference action '{action}' processed successfully:", response.json())
    else:
        print(f"Failed to process '{action}' poll preference. Status Code:", response.status_code)
        print("Error Response:", response.text)

if __name__ == "__main__":
    # Step 1: Login and get session cookies
    cookies = test_login()
    if not cookies:
        print("Login failed. Aborting further tests.")
        exit(1)

    """# Step 2: Test interaction-related endpoints
    actions = ["view", "click", "vote", "comment"]
    for action in actions:
        test_log_interaction(cookies, action)"""

    # Step 3: Test fetching interactions
    test_get_user_interactions(cookies, "6c915b0b-ba98-474b-afb4-")
    test_get_poll_interactions(cookies, "67cbeb5e7c5bbf3d9f98f52f")
    test_get_interactions_by_type(cookies, "vote")
    
    # Step 4: Test poll preference actions (like, dislike, etc.)
    poll_preference_actions = ["view", "click","like", "unlike", "dislike", "undislike"]
    for action in poll_preference_actions:
        test_poll_preference(cookies, action)

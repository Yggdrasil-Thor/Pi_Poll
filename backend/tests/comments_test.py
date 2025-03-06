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


# Test Create Comment
def test_create_comment(cookies):
    print("\nTesting /comments/create (POST) endpoint...")
    comment_data = {
        "pollId": "67c7db339b4856288f0f7536",
        "text": "This is a test comment",
        "parentId": None  # For top-level comments
    }
    response = requests.post(f"{BASE_URL}/comments/create", json=comment_data, cookies=cookies)

    if response.status_code == 201:
        print("Comment created successfully:", response.json())
        return response.json().get("data")  # Returning comment ID
    else:
        print("Failed to create comment. Status Code:", response.status_code)
        print("Error Response:", response.text)
        return None


# Test Get Comment by ID
def test_get_comment_by_id(cookies, comment_id):
    print(f"\nTesting /comments/{comment_id} (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/comments/{comment_id}", cookies=cookies)

    if response.status_code == 200:
        print("Comment details:", response.json())
    else:
        print("Failed to fetch comment. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Comments by Poll
def test_get_comments_by_poll(cookies, poll_id):
    print(f"\nTesting /comments/poll/{poll_id} (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/comments/poll/{poll_id}", cookies=cookies)

    if response.status_code == 200:
        print("Comments for poll:", response.json())
    else:
        print("Failed to fetch comments for poll. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Get Comments by User
def test_get_comments_by_user(cookies,user_id):
    print(f"\nTesting /users/comments/{user_id} (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/users/comments/{user_id}", cookies=cookies)

    if response.status_code == 200:
        print("Comments by user:", response.json())
    else:
        print("Failed to fetch comments for user. Status Code:", response.status_code)
        print("Error Response:", response.text)

# Test Get Comments by User
def test_get_replies(cookies,parent_id):
    print(f"\nTesting /comments/replies/{parent_id} (GET) endpoint...")
    response = requests.get(f"{BASE_URL}/comments/replies/{parent_id}", cookies=cookies)

    if response.status_code == 200:
        print("Replies to parent:", response.json())
    else:
        print("Failed to get replies. Status Code:", response.status_code)
        print("Error Response:", response.text)



# Test Update Comment Sentiment
def test_update_comment_sentiment(cookies, comment_id):
    print(f"\nTesting /comments/update_sentiment (PUT) endpoint for Comment {comment_id}...")
    response = requests.put(
        f"{BASE_URL}/comments/update_sentiment/{comment_id}", 
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"Comment sentiment updated for {comment_id}: {response.json()}")
    else:
        print(f"Failed to update sentiment for comment {comment_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


# Test Delete Comment
def test_delete_comment(cookies, comment_id):
    print(f"\nTesting /comments/delete (DELETE) endpoint for Comment {comment_id}...")
    response = requests.delete(
        f"{BASE_URL}/comments/delete/{comment_id}", 
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"Comment deleted for {comment_id}: {response.json()}")
    else:
        print(f"Failed to delete comment {comment_id}. Status Code:", response.status_code)
        print("Error Response:", response.text)


if __name__ == "__main__":
    # Step 1: Login and get session cookies
    cookies = test_login()
    if not cookies:
        print("Login failed. Aborting further tests.")
        exit(1)

    # Step 2: Test comment endpoints
    comment_id = test_create_comment(cookies)
    parent_id = comment_id
    if comment_id:
        test_get_comment_by_id(cookies, comment_id)
        test_get_comments_by_poll(cookies, "67c7db339b4856288f0f7536")
        test_get_comments_by_user(cookies,"deb0c5a4-6caa-4133-8d10-")
        test_get_replies(cookies,parent_id)
        test_update_comment_sentiment(cookies, comment_id)
        test_delete_comment(cookies, comment_id)

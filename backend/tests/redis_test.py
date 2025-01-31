from utils.redis_session import create_session, get_session, delete_session, is_session_valid, redis_health_check

# Test Redis health
if redis_health_check():
    print("Redis is running and reachable.")
else:
    print("Redis is not running or unreachable.")
    exit(1)

# Test session creation
user_id = "123"
token = "test_token"
print(f"Creating session for user_id: {user_id} with token: {token}")
create_session(user_id, token)

# Test session retrieval
print(f"Retrieving session for user_id: {user_id}")
retrieved_token = get_session(user_id)
print(f"Retrieved token: {retrieved_token}")
assert retrieved_token == token, f"Expected {token}, got {retrieved_token}"

# Test session validity
print(f"Checking session validity for user_id: {user_id}")
is_valid = is_session_valid(user_id)
print(f"Session valid: {is_valid}")
assert is_valid, "Session should be valid"

# Test session deletion
print(f"Deleting session for user_id: {user_id}")
delete_session(user_id)

# Verify session deletion
print(f"Checking session validity after deletion for user_id: {user_id}")
is_valid_after_deletion = is_session_valid(user_id)
print(f"Session valid after deletion: {is_valid_after_deletion}")
assert not is_valid_after_deletion, "Session should be invalid after deletion"

print("All tests passed!")

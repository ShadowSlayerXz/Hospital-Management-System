from database.user_dao import create_user, get_user_by_email
from services.auth_services import login_user, register_user

# Testing user creation
print("Creating user...")
result = create_user("KT", "kt@test.com", "1234", "patient")
print("Create result:", result)

# Testing fetching user
print("\nFetching user...")
user = get_user_by_email("hitesh@test.com")
print("Fetched user:", user)

# Testing User registration
print("\nRegistering user...")
register_user("Hitesh", "hitesh@test.com", "1234", "patient")

# Testing User login
print("\nLogging in user...")
login_user("hitesh@test.com", "1234")

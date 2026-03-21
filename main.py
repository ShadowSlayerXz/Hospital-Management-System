from database.user_dao import create_user, get_user_by_email

# Test user creation
print("Creating user...")
result = create_user("Hitesh", "hitesh@test.com", "1234", "patient")
print("Create result:", result)

# Test fetching user
print("\nFetching user...")
user = get_user_by_email("hitesh@test.com")
print("Fetched user:", user)

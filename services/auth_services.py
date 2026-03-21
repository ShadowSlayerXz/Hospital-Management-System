from database.user_dao import create_user, get_user_by_email


# user registration
def register_user(name, email, password, role):
    existing_user = get_user_by_email(email)

    if existing_user:
        return False

    result = create_user(name, email, password, role)

    if result:
        print("User registered successfully.")
        return True
    else:
        print("Failed to register user.")
        return False


# user login
def login_user(email, password):
    user = get_user_by_email(email)

    if not user:
        print("User not found.")
        return False

    if user[3] != password:
        print("Incorrect password.")
        return False

    print("Login successful.")
    return True

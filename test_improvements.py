#!/usr/bin/env python3
"""
Test script to verify the improved user management code
"""
import asyncio
import uuid
from app.domains.user.models import UserCreate, UserUpdate, UserOut
from app.domains.user.service import (
    create_user,
    fetch_user,
    update_user_service,
    delete_user,
    get_all_users,
)


async def test_user_operations():
    """Test basic user CRUD operations"""
    print("Testing user operations...")

    # Test 1: Create user
    print("\n1. Creating user...")
    user_data = UserCreate(name="John Doe", password="securepassword123")
    user_id = await create_user(user_data)

    if user_id:
        print(f"✅ User created with ID: {user_id}")
    else:
        print("❌ Failed to create user")
        return

    # Test 2: Fetch user
    print("\n2. Fetching user...")
    user = await fetch_user(user_id)
    if user:
        print(f"✅ User fetched: {user.name}")
    else:
        print("❌ Failed to fetch user")

    # Test 3: Update user
    print("\n3. Updating user...")
    update_data = UserUpdate(name="John Smith")
    success = await update_user_service(user_id, update_data)
    if success:
        print("✅ User updated successfully")

        # Verify update
        updated_user = await fetch_user(user_id)
        if updated_user and updated_user.name == "John Smith":
            print(f"✅ Update verified: {updated_user.name}")
        else:
            print("❌ Update verification failed")
    else:
        print("❌ Failed to update user")

    # Test 4: Get all users
    print("\n4. Getting all users...")
    all_users = await get_all_users()
    print(f"✅ Found {len(all_users)} users")

    # Test 5: Delete user
    print("\n5. Deleting user...")
    deleted = await delete_user(user_id)
    if deleted:
        print("✅ User deleted successfully")

        # Verify deletion
        deleted_user = await fetch_user(user_id)
        if deleted_user is None:
            print("✅ Deletion verified")
        else:
            print("❌ Deletion verification failed")
    else:
        print("❌ Failed to delete user")


async def test_error_handling():
    """Test error handling scenarios"""
    print("\n" + "=" * 50)
    print("Testing error handling...")

    # Test 1: Fetch non-existent user
    print("\n1. Fetching non-existent user...")
    fake_id = uuid.uuid4()
    user = await fetch_user(fake_id)
    if user is None:
        print("✅ Correctly returned None for non-existent user")
    else:
        print("❌ Should have returned None")

    # Test 2: Update non-existent user
    print("\n2. Updating non-existent user...")
    update_data = UserUpdate(name="Test Name")
    success = await update_user_service(fake_id, update_data)
    if not success:
        print("✅ Correctly failed to update non-existent user")
    else:
        print("❌ Should have failed to update")

    # Test 3: Delete non-existent user
    print("\n3. Deleting non-existent user...")
    deleted = await delete_user(fake_id)
    if not deleted:
        print("✅ Correctly failed to delete non-existent user")
    else:
        print("❌ Should have failed to delete")


async def main():
    """Main test function"""
    print("🚀 Starting user management tests...")

    try:
        await test_user_operations()
        await test_error_handling()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""Test multi-user functionality."""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"


async def test_multi_user():
    """Test multi-user API endpoints."""
    async with aiohttp.ClientSession() as session:
        print("=== Testing Multi-User API ===\n")
        
        # Test 1: Health check
        print("1. Testing health check...")
        async with session.get(f"{BASE_URL}/health") as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(data, indent=2)}\n")
        
        # Test 2: Register user 1
        print("2. Registering user 1...")
        user1_data = {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "SecurePass123!"
        }
        async with session.post(
            f"{BASE_URL}/auth/register",
            json=user1_data
        ) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                user1 = await resp.json()
                print(f"   User created: {user1['username']}")
                print(f"   API Key: {user1['api_key'][:20]}...")
                print(f"   Token: {user1['token'][:20]}...\n")
                user1_token = user1['token']
                user1_api_key = user1['api_key']
            else:
                error = await resp.text()
                print(f"   Error: {error}\n")
                return
        
        # Test 3: Register user 2
        print("3. Registering user 2...")
        user2_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "AnotherPass456!"
        }
        async with session.post(
            f"{BASE_URL}/auth/register",
            json=user2_data
        ) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                user2 = await resp.json()
                print(f"   User created: {user2['username']}")
                print(f"   API Key: {user2['api_key'][:20]}...")
                print(f"   Token: {user2['token'][:20]}...\n")
                user2_token = user2['token']
            else:
                error = await resp.text()
                print(f"   Error: {error}\n")
                # Continue even if user 2 fails
                user2_token = None
        
        # Test 4: Login as user 1
        print("4. Testing login...")
        async with session.post(
            f"{BASE_URL}/auth/login",
            json={"username": "testuser1", "password": "SecurePass123!"}
        ) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                login_data = await resp.json()
                print(f"   Logged in as: {login_data['username']}\n")
            else:
                error = await resp.text()
                print(f"   Error: {error}\n")
        
        # Test 5: Get profile (with JWT token)
        print("5. Getting user profile (JWT auth)...")
        headers = {"Authorization": f"Bearer {user1_token}"}
        async with session.get(
            f"{BASE_URL}/user/profile",
            headers=headers
        ) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                profile = await resp.json()
                print(f"   Profile: {json.dumps(profile, indent=2)}\n")
            else:
                error = await resp.text()
                print(f"   Error: {error}\n")
        
        # Test 6: Simulate call for user 1 (with API key)
        print("6. Simulating call for user 1 (API key auth)...")
        headers = {"X-API-Key": user1_api_key}
        call_data = {
            "call_id": "test_001",
            "caller_number": "+1234567890",
            "called_number": "+0987654321"
        }
        async with session.post(
            f"{BASE_URL}/call/incoming",
            json=call_data,
            headers=headers
        ) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                result = await resp.json()
                print(f"   Call result: {json.dumps(result, indent=2)}\n")
            else:
                error = await resp.text()
                print(f"   Error: {error}\n")
        
        # Test 7: Get call history for user 1
        print("7. Getting call history for user 1...")
        headers = {"Authorization": f"Bearer {user1_token}"}
        async with session.get(
            f"{BASE_URL}/user/calls",
            headers=headers
        ) as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                history = await resp.json()
                print(f"   Total calls: {history['total_calls']}")
                if history['calls']:
                    print(f"   Latest call: {json.dumps(history['calls'][0], indent=2)}\n")
                else:
                    print(f"   No calls yet\n")
            else:
                error = await resp.text()
                print(f"   Error: {error}\n")
        
        # Test 8: Try accessing without auth (should fail)
        print("8. Testing unauthorized access...")
        async with session.get(f"{BASE_URL}/user/profile") as resp:
            print(f"   Status: {resp.status} (expected 401)")
            if resp.status == 401:
                print(f"   ✓ Properly rejected unauthorized request\n")
            else:
                print(f"   ✗ Security issue: should require authentication\n")
        
        print("=== Tests Complete ===")


if __name__ == "__main__":
    asyncio.run(test_multi_user())

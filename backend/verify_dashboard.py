#!/usr/bin/env python3
"""
Quick test to verify dashboard data sources
"""
import requests

def test_dashboard_data():
    # Login
    login_response = requests.post(
        'http://localhost:8001/api/auth/login',
        json={'email': 'debuguser2@example.com', 'password': 'testpass123'},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print("🧪 Testing dashboard data sources...")
    
    # Test clipboard stats
    r1 = requests.get('http://localhost:8001/api/clipboard/stats', headers=headers)
    if r1.status_code == 200:
        data = r1.json()
        print(f"✅ Clipboard: {data['sync_count']} syncs, {data['total_items']} items")
    else:
        print(f"❌ Clipboard stats failed: {r1.status_code}")
    
    # Test audit stats  
    r2 = requests.get('http://localhost:8001/api/audit/stats', headers=headers)
    if r2.status_code == 200:
        data = r2.json()
        print(f"✅ Audit: {data['total_events']} events, {data['success_rate']}% success")
    else:
        print(f"❌ Audit stats failed: {r2.status_code}")
    
    # Test devices list (fallback)
    r3 = requests.get('http://localhost:8001/api/devices/', headers=headers)
    if r3.status_code == 200:
        devices = r3.json()
        online = sum(1 for d in devices if d.get('is_online', False))
        print(f"✅ Devices: {len(devices)} total, {online} online")
    else:
        print(f"❌ Devices endpoint failed: {r3.status_code}")
        
    print("\n🎉 Dashboard should now show real-time data!")
    print("The dashboard will auto-refresh every 5 seconds.")

if __name__ == "__main__":
    test_dashboard_data()

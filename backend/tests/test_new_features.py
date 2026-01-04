"""
Integration Test Script for New Features

Run this script to verify all new features work correctly.
Usage: docker-compose exec api python tests/test_new_features.py
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_result(test_name: str, success: bool, response=None):
    """Print test result with colors."""
    if success:
        print(f"✅ {test_name}")
    else:
        print(f"❌ {test_name}")
        if response:
            print(f"   Response: {response}")


def test_health():
    """Test health endpoint."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        success = r.status_code == 200 and r.json().get("status") == "ok"
        print_result("Health Check", success, r.json() if not success else None)
        return success
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False


def test_lineup_api():
    """Test Lineup API CRUD operations."""
    test_match_id = "test-integration-001"
    
    # 1. Create lineup
    try:
        payload = {
            "match_id": test_match_id,
            "mappings": [
                {"track_id": 1, "player_name": "Messi", "jersey_number": 10, "team": "home"},
                {"track_id": 2, "player_name": "Pedri", "jersey_number": 8, "team": "home"},
                {"track_id": 11, "player_name": "Vinicius", "jersey_number": 7, "team": "away"}
            ]
        }
        r = requests.post(
            f"{BASE_URL}/api/v1/lineups",
            json=payload,
            timeout=10
        )
        create_success = r.status_code == 200 and r.json().get("mapped_tracks") == 3
        print_result("Lineup API - Create", create_success, r.json() if not create_success else None)
    except Exception as e:
        print_result("Lineup API - Create", False, str(e))
        return False
    
    # 2. Get lineup
    try:
        r = requests.get(f"{BASE_URL}/api/v1/lineups/{test_match_id}", timeout=5)
        get_success = r.status_code == 200 and len(r.json().get("mappings", [])) == 3
        print_result("Lineup API - Get", get_success, r.json() if not get_success else None)
    except Exception as e:
        print_result("Lineup API - Get", False, str(e))
        return False
    
    # 3. Get specific player
    try:
        r = requests.get(f"{BASE_URL}/api/v1/lineups/{test_match_id}/player/1", timeout=5)
        player_success = r.status_code == 200 and r.json().get("player_name") == "Messi"
        print_result("Lineup API - Get Player", player_success, r.json() if not player_success else None)
    except Exception as e:
        print_result("Lineup API - Get Player", False, str(e))
        return False
    
    # 4. Delete lineup
    try:
        r = requests.delete(f"{BASE_URL}/api/v1/lineups/{test_match_id}", timeout=5)
        delete_success = r.status_code == 200
        print_result("Lineup API - Delete", delete_success, r.json() if not delete_success else None)
    except Exception as e:
        print_result("Lineup API - Delete", False, str(e))
        return False
    
    return create_success and get_success and player_success and delete_success


def test_index_api():
    """Test RAG Indexing API."""
    test_match_id = "test-integration-002"
    
    # 1. Index with custom data
    try:
        payload = {
            "match_events": [
                {"type": "goal", "player": "Messi", "team": "Barcelona", "minute": 23},
                {"type": "shot", "player": "Pedri", "team": "Barcelona", "minute": 45}
            ],
            "match_metrics": {
                "home_ppda": 8.5,
                "away_ppda": 12.3,
                "total_distance": 115.5
            },
            "match_summary": "Barcelona won 2-0 with strong pressing."
        }
        r = requests.post(
            f"{BASE_URL}/api/v1/index/{test_match_id}",
            json=payload,
            timeout=10
        )
        index_success = r.status_code == 200 and r.json().get("status") in ["success", "no_documents"]
        print_result("Index API - Index Match", index_success, r.json() if not index_success else None)
    except Exception as e:
        print_result("Index API - Index Match", False, str(e))
        return False
    
    # 2. Get stats
    try:
        r = requests.get(f"{BASE_URL}/api/v1/index/stats", timeout=5)
        stats_success = r.status_code == 200 and "status" in r.json()
        print_result("Index API - Get Stats", stats_success, r.json() if not stats_success else None)
    except Exception as e:
        print_result("Index API - Get Stats", False, str(e))
        return False
    
    # 3. Delete index
    try:
        r = requests.delete(f"{BASE_URL}/api/v1/index/{test_match_id}", timeout=5)
        delete_success = r.status_code == 200
        print_result("Index API - Delete", delete_success, r.json() if not delete_success else None)
    except Exception as e:
        print_result("Index API - Delete", False, str(e))
        return False
    
    return index_success and stats_success and delete_success


def test_video_endpoint():
    """Test video processing endpoint accepts new parameters."""
    try:
        # Just test that the endpoint accepts the new parameters
        # (won't actually process since no video file)
        payload = {
            "video_path": "/data/nonexistent.mp4",
            "output_path": "/output",
            "metadata": {
                "home_team": "Barcelona",
                "away_team": "Real Madrid",
                "date": "2026-01-03",
                "competition": "La Liga"
            },
            "sync_offset_seconds": 0.0,
            "mode": "full_match"
        }
        r = requests.post(
            f"{BASE_URL}/api/v1/process-video",
            json=payload,
            timeout=10
        )
        # Should return 200 (job started) or error about file not found
        # Just check it doesn't return 422 (validation error)
        success = r.status_code != 422
        print_result("Video API - New Parameters", success, 
                    r.json() if r.status_code == 422 else None)
        return success
    except Exception as e:
        print_result("Video API - New Parameters", False, str(e))
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 50)
    print("🧪 Running Integration Tests for New Features")
    print("=" * 50 + "\n")
    
    results = []
    
    # Health check first
    results.append(("Health", test_health()))
    
    # Lineup API
    results.append(("Lineup API", test_lineup_api()))
    
    # Index API
    results.append(("Index API", test_index_api()))
    
    # Video API
    results.append(("Video API", test_video_endpoint()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    print("=" * 50 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

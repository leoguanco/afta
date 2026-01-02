import sys
import os

# Ensure src module is in path
sys.path.append(os.getcwd())

from src.infrastructure.storage.minio_adapter import MinIOAdapter

if __name__ == "__main__":
    match_id = sys.argv[1] if len(sys.argv) > 1 else '2-boca'
    
    print(f"Initializing MinIO Adapter for match: {match_id}...")
    try:
        adapter = MinIOAdapter()
        bucket = adapter.bucket
        key = f"tracking/{match_id}.parquet"
        
        print(f"Attempting to delete object: {bucket}/{key}")
        
        # Check if exists first (optional, but good for feedback)
        try:
            adapter.client.stat_object(bucket, key)
            exists = True
        except:
            exists = False
            
        if exists:
            adapter.client.remove_object(bucket, key)
            print(f"✅ Successfully deleted {key}")
        else:
            print(f"⚠️ Object {key} does not exist (already clean).")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)

# Implementation Plan - Tracking Persistence Completion

## Goal Description

Harden the `MinIOAdapter` and `vision_tasks.py` to ensure robust, error-tolerant storage of large player trajectory files. This moves the implementation from "functioning prototype" to "production-ready" by handling network failures and ensuring data integrity.

## User Review Required

> [!NOTE]
> We are adding explicit retry logic to the Celery task. The default is 5 seconds countdown.

## Proposed Changes

### Infrastructure Layer

#### [MODIFY] [minio_adapter.py](file:///d:/Workspace/afta/backend/src/infrastructure/storage/minio_adapter.py)

- Update `save_parquet` to explicitly set `content_type="application/octet-stream"`.
- Add a check `self.client.bucket_exists` inside `save_parquet` (or ensure it's cached) to prevent "Bucket not found" errors on fresh deploys.

#### [MODIFY] [vision_tasks.py](file:///d:/Workspace/afta/backend/src/infrastructure/worker/tasks/vision_tasks.py)

- Wrap the upload section in a specific `try/except S3Error` block.
- In the `except` block, log a specific warning and re-raise to trigger the Celery `retry` mechanism.
- Verify the `max_retries` parameter in `@celery_app.task` decorator is appropriate (currently 2).

## Verification Plan

### Automated Tests

- **Integration Test**: `tests/infrastructure/storage/test_minio_adapter_integration.py` (New or update existing)
  - **Test Retry**: Mock `minio_client.put_object` to fail once then succeed. Verify `vision_tasks` handles this (though testing Celery retry mechanism directly is tricky, we can test the function logic).
  - **Test File Integrity**: Save a dataframe, download it immediately, and assert `pd.testing.assert_frame_equal`.

### Manual Verification

- Run a local MinIO instance.
- Turn off MinIO container (`docker stop afta-minio-1`).
- Trigger `process_video_task`.
- Turn on MinIO container.
- Verify task eventually succeeds.

# Model Splitting TODO

## Overview
Splitting the monolithic `app/models.py` into separate files under `app/models/` for better organization, fixing typos, and updating dependent imports.

## Steps

- [x] Create `app/models/` directory
- [x] Create `app/models/__init__.py` with re-exports for backward compatibility
- [x] Create `app/models/staff.py` with Staff-related models and Embedding
- [x] Create `app/models/attendance.py` with Attendance-related models and Status
- [x] Create `app/models/admin.py` with Administrator models (fix typos)
- [x] Update imports in dependent route files:
  - `app/route/embedding.py`
  - `app/route/status.py`
  - `app/route/admin.py`
  - `app/route/attendance.py`
  - `app/route/staff.py`
- [x] Delete original `app/models.py`
- [x] Verify the app runs without import errors (e.g., execute `python app/main.py`)
- [ ] Test key routes to ensure models function correctly (e.g., staff creation, attendance logging)

## Notes
- Fix typos: "Admistrator" → "Administrator", "AttendanceCreat" → "AttendanceCreate".
- Ensure relationships (e.g., back_populates) remain intact.
- No changes to database schema; just reorganization.

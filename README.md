# Spy Cat Agency Backend

This is the backend for the Spy Cat Agency built with FastAPI and SQLite.

## Setup
1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy requests pydantic
   ```

2. **Run the application**:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`.

## Database
- Uses SQLite database (`spy.db`), which is created automatically.
- Stores cats, missions, and targets.

## API Endpoints
The backend provides the following endpoints:
- **Cats**:
  - `POST /cats`: Create a new cat
  - `GET /cats`: List all cats.
  - `GET /cats/{cat_id}`: Get a cat by ID.
  - `PUT /cats/{cat_id}`: Update a cat's salary.
  - `DELETE /cats/{cat_id}`: Delete a cat.
- **Missions**:
  - `POST /missions`: Create a new mission.
  - `GET /missions`: List all missions.
  - `GET /missions/{mission_id}`: Get a specific mission by ID.
  - `DELETE /missions/{mission_id}`: Delete a mission.
  - `PATCH /missions/{mission_id}/assign`: Assign a cat to a mission.
- **Targets**:
  - `PATCH /missions/{mission_id}/targets/{target_id}/notes`: Update notes.
  - `PATCH /missions/{mission_id}/targets/{target_id}/complete`: Mark a target as complete.
All endpoints are documented in the Postman collection in this repo.

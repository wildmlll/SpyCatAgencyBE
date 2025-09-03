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
All endpoints are documented in the Postman collection in this repo or [HERE](https://example.com](https://maxhanych-9474331.postman.co/workspace/Maksym's-Workspace~b8cef587-3b59-4434-82fc-3db7b5707de1/collection/48142531-7e346a24-a1c3-4e51-8d14-418afc3b0465?action=share&source=copy-link&creator=48142531). 

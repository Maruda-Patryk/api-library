# Library API

A simple Django application exposing an API for managing a library's book collection.

## Getting Started

1. Build the image and start the container:
   ```bash
   docker-compose up --build
   ```
2. The application will be available at `http://localhost:8000/`.
3. API endpoints are available under the `/api/` prefix (e.g., `/api/books/`).

## API Documentation

- **Swagger UI** — Interactive documentation is exposed at `http://localhost:8000/api/docs/`.
- **OpenAPI schema** — A raw schema is available at `http://localhost:8000/api/schema/`.
- **Postman collection** — Import `Library_API.postman_collection.json` (root directory) into Postman to explore the API with sample requests.

## Development Workflow

- **Pre-commit hooks** — Install the hooks locally to keep the codebase consistent:
  ```bash
  pip install pre-commit
  pre-commit install
  ```
  You can run them on demand with:
  ```bash
  pre-commit run --all-files
  ```

## Running Tests

Execute the Django test suite inside the Docker environment:

```bash
docker compose -f docker-compose.yml run --rm -T web python manage.py test --settings=library_project.settings
```

## Test Users

For local testing, the database seeds multiple library users via a data migration. After applying migrations, the following library card numbers will be available in the system:

- `123456`
- `654321`
- `111111`

Additionally, an administrator account (with `is_staff` and `is_superuser` privileges) is created for accessing the Django admin panel (http://localhost:8000/admin/):

- Library card number: `222222`
- Password: `pass1234`

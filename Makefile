run:
	uvicorn workout_api.main:app --reload
run-docker:
	docker compose up --build
run-migrations:
	alembic upgrade head
test:
	python -m pytest -q

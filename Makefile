install-deps:
	pip3 install -r requirements.txt

up: install-deps
	docker-compose down --remove-orphans
	docker volume rm iqvia-assignment_raw_data || true
	docker volume rm iqvia-assignment_refined_data || true
	docker compose up -d --build

down:
	docker-compose down --remove-orphans
	docker volume rm iqvia-assignment_raw_data || true
	docker volume rm iqvia-assignment_refined_data || true

test:
	docker-compose down
	docker volume rm iqvia-assignment_raw_data || true
	docker volume rm iqvia-assignment_refined_data || true
	docker-compose up -d --build
	sleep 30
	pytest -v tests/test_etl.py


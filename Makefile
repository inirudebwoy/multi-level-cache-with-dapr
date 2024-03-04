run:
	poetry run uvicorn main:app --reload

dapr-run:
	dapr run --app-id main-app --resources-path ./resources/ --app-port 8000 -- make run
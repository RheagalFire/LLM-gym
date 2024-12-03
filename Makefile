.PHONY: local
local:
	uvicorn gym_reader.api.api:app --proxy-headers --host 127.0.0.1 --port 8001 --log-level debug --reload --timeout-keep-alive 65

indexing:
	python -m gym_reader.services.indexing_service

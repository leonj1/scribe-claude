.PHONY: start stop restart help

help:
	@echo "Available targets:"
	@echo "  start   - Start all services using docker-compose"
	@echo "  stop    - Stop all services using docker-compose"
	@echo "  restart - Restart all services (stop then start)"

start:
	@echo "Starting services..."
	docker compose up -d
	@echo "Services started successfully!"

stop:
	@echo "Stopping services..."
	docker compose down
	@docker ps -a | grep transcription | awk '{print $$1}' | xargs -r docker rm -f 2>/dev/null || true
	@echo "Services stopped successfully!"

restart: stop start
	@echo "Services restarted successfully!"

.PHONY: up down logs status report report-clean dump clean

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f producer extractor graph_builder summary

status:
	curl -s http://localhost:8000/ | python3 -m json.tool || echo "API not reachable. Is Docker running?"

report:
	$(MAKE) -C latex-report

report-clean:
	$(MAKE) -C latex-report clean

dump:
	python3 server/cskg_dump.py

clean: report-clean
	rm -f cskg_full_dump.ttl
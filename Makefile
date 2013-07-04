all: server

server:
	cd python && ./server.py

deploy-staging:
	ssh sc-staging@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		git pull && \
		cd text && \
		git pull && \
		cd .. \
		pip install -r requirements.txt && \
		sudo supervisorctl restart sc-staging'

deploy-production:
	ssh sc-production@vps.suttacentral.net \
		'cd $$HOME/suttacentral && \
		git pull && \
		cd text && \
		git pull'

clean:
	rm -rf \
		__pycache__ \
		python/__pycache__ \
		log/*.log \
		tmp/dbr.cache

clean-db:
	rm -f db/sc.sqlite

clean-all: clean clean-db

fetch-db-export:
	cd tmp && curl -O http://suttacentral.net/db-exports/sc-latest.sql.gz
	echo 'The database is now available in tmp/sc-latest.sql.gz'

regenerate-db-export:
	ssh sc-production@vps.suttacentral.net '$$HOME/create-db-export'

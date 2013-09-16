all: server

server:
	cd python && ./server.py

deploy-staging:
	ssh sc-staging@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		touch tmp/maintenance && \
		sudo supervisorctl stop sc-staging && \
		git pull && \
		cd text && \
		git pull && \
		cd .. && \
		pip install -q -r requirements.txt && \
		make clean-all && \
		make reset-db && \
		make build-assets && \
		make build-dict && \
		make build-search-indexes && \
		rm -f tmp/maintenance && \
		sudo supervisorctl start sc-staging && \
		sudo service apache2 reload'

deploy-production:
	ssh sc-production@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		touch tmp/maintenance && \
		sudo supervisorctl stop sc-production && \
		git pull && \
		cd text && \
		git pull && \
		cd .. && \
		pip install -q -r requirements.txt && \
		make build-assets && \
		make build-dict && \
		make build-search-indexes && \
		rm -f tmp/maintenance && \
		sudo supervisorctl start sc-production && \
		sudo service apache2 reload'

quick-deploy-production:
	ssh sc-production@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		touch tmp/maintenance && \
		sudo supervisorctl stop sc-production && \
		git pull && \
		cd text && \
		git pull && \
		cd .. && \
		pip install -q -r requirements.txt && \
		make build-assets && \
		rm -f tmp/maintenance && \
		sudo supervisorctl start sc-production && \
		sudo service apache2 reload'

clean:
	rm -rf \
		__pycache__ \
		python/__pycache__ \
		log/*.log \
		tmp/*

clean-assets:
	rm -rf \
		static/css/compiled/*.css \
		static/js/compiled/*.js

clean-db:
	rm -f db/*.sqlite db/*.sqlite.tmp*
clean-exports:
	rm -f static/exports/*
clean-old-exports:
	find static/exports -type f -mtime +7 -exec rm {} \;

clean-all: clean clean-assets clean-db clean-exports

build-assets:
	cd python && python -c 'import assets;assets.build()'

build-dict:
	cd python && python build_dict_db.py

build-search-indexes:
	cd python && python -c 'import textsearch; textsearch.build()'

create-dev-offline-export:
	utility/export/offline.py --force localhost:8800
create-dev-db-export:
	utility/export/db.py --force

create-production-offline-export:
	utility/export/offline.py --quiet --wait 0.05 suttacentral.net
create-production-db-export:
	utility/export/db.py --quiet

create-db-user:
	python/dbutil.py create-db-user
setup-db-auth:
	python/dbutil.py setup-db-auth
fetch-db-export:
	python/dbutil.py fetch-db-export
create-db:
	python/dbutil.py create-db
load-db:
	python/dbutil.py load-db
drop-db:
	python/dbutil.py drop-db
reset-db:
	python/dbutil.py reset-db

create-newrelic-ini:
	utility/create_newrelic_ini.py

test: test-local

test-local:
	python -m unittest discover -s tests -p '*_test.py'
test-staging:
	URL='http://staging.suttacentral.net/' python -m unittest discover -s tests -p '*_test.py'
test-production:
	URL='http://suttacentral.net/' python -m unittest discover -s tests -p '*_test.py'

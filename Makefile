all: server

server:
	invoke server

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
		sudo supervisorctl start sc-staging && \
		sudo service apache2 reload && \
		rm -f tmp/maintenance && \
		make build-dict && \
		make build-search-indexes'

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
		sudo supervisorctl start sc-production && \
		sudo service apache2 reload && \
		rm -f tmp/maintenance && \
		make build-dict && \
		make build-search-indexes'

quickest-deploy-production:
	ssh sc-production@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		git pull && \
		cd text && \
		git pull && \
		cd .. && \
		pip install -q -r requirements.txt && \
		make build-assets && \
		sudo supervisorctl restart sc-production'

deploy-texts-production:
	ssh sc-production@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		cd text && \
		git pull && \
		cd .. &&\
		make build-search-indexes'
		
clean:
	invoke clean
clean-assets:
	invoke assets.clean
clean-all-assets:
	invoke assets.clean --aggressive
clean-db:
	invoke db.clean
clean-exports:
	rm -f static/exports/*
clean-old-exports:
	find static/exports -type f -mtime +7 -exec rm {} \;

clean-all: clean clean-assets clean-db clean-exports

build-assets: compile-assets

compile-assets:
	invoke assets.compile

build-dict:
	cd src && python build_dict_db.py

build-search-indexes:
	cd src && python -c 'import textsearch; textsearch.build()'

sync-production-fonts:
	rsync -avz sc-production@vps.suttacentral.net:/home/sc-production/suttacentral/static/fonts/nonfree/ static/fonts/nonfree/

create-dev-offline-export:
	utility/export/offline.py --force localhost:8800
create-dev-db-export:
	utility/export/db.py --force

create-production-offline-export:
	utility/export/offline.py --quiet --wait 0.05 suttacentral.net
create-production-db-export:
	utility/export/db.py --quiet

create-db-user:
	invoke db.setup
setup-db-auth:
	invoke db.setup
fetch-db-export:
	invoke db.dump.download
create-db:
	invoke db.create
load-db:
	invoke db.dump.import
drop-db:
	invoke db.drop
reset-db:
	invoke db.reset

create-newrelic-ini:
	invoke newrelic.update_ini

test:
	invoke test
test-local:
	invoke test
test-staging:
	invoke test --url='http://staging.suttacentral.net/'
test-production:
	invoke test --url='http://suttacentral.net/'

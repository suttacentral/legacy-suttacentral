all: server

server:
	cd src && ./server.py

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
	rm -rf \
		__pycache__ \
		src/__pycache__ \
		log/*.log \
		tmp/*
clean-assets:
	rm -rf \
		static/css/compiled/*.css \
		static/js/compiled/*.js \
		tmp/webassets*
clean-outdated-assets:
	cd src && python -c 'import assets; assets.clean_outdated()'
clean-db:
	rm -f db/*.sqlite db/*.sqlite.tmp*
clean-exports:
	rm -f static/exports/*
clean-old-exports:
	find static/exports -type f -mtime +7 -exec rm {} \;

clean-all: clean clean-assets clean-db clean-exports

build-assets:
	cd src && python -c 'import assets;assets.build()'

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
	utility/dbutil.py create-db-user
setup-db-auth:
	utility/dbutil.py setup-db-auth
fetch-db-export:
	utility/dbutil.py fetch-db-export
create-db:
	utility/dbutil.py create-db
load-db:
	utility/dbutil.py load-db
drop-db:
	utility/dbutil.py drop-db
reset-db:
	utility/dbutil.py reset-db

create-newrelic-ini:
	utility/create_newrelic_ini.py

test: test-local

test-local:
	python -m unittest discover -s tests -p '*_test.py'
test-staging:
	URL='http://staging.suttacentral.net/' python -m unittest discover -s tests -p '*_test.py'
test-production:
	URL='http://suttacentral.net/' python -m unittest discover -s tests -p '*_test.py'

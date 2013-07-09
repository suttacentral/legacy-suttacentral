all: server

server:
	cd python && ./server.py

deploy-staging:
	ssh sc-staging@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		sudo supervisorctl stop sc-staging && \
		touch tmp/maintenance && \
		git pull && \
		cd text && \
		git pull && \
		cd .. && \
		pip install -r requirements.txt && \
		rm -f tmp/maintenance && \
		sudo supervisorctl start sc-staging'

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
		tmp/*

clean-assets:
	rm -rf \
		static/css/compiled/*.css \
		static/js/compiled/*.js

clean-db:
	rm -f db/sc.sqlite

clean-all: clean clean-assets clean-db

build-assets:
	cd python && python -c 'import assets;assets.build()'

regenerate-db-export:
	ssh sc-production@vps.suttacentral.net '$$HOME/create-db-export'

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

test: test-local

test-local:
	python tests/sc_test.py
test-staging:
	URL='http://staging.suttacentral.net/' python tests/sc_test.py
test-production:
	URL='http://suttacentral.net/' python tests/sc_test.py

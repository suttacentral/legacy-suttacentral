all: server

server:
	invoke server

deploy-staging:
	invoke deploy.staging.full
deploy-production:
	invoke deploy.production.full
quickest-deploy-production:
	invoke deploy.production.quick
deploy-texts-production:
	invoke deploy.production.text

clean:
	invoke clean
clean-assets:
	invoke assets.clean --older
clean-all-assets:
	invoke assets.clean
clean-db:
	invoke db.clean
	invoke dictionary.clean
	invoke search.clean
clean-exports:
	invoke exports.db.clean
	invoke exports.offline.clean
clean-old-exports:
	invoke exports.db.clean --older
	invoke exports.offline.clean --older
clean-all:
	invoke clean --aggressive

build-assets:
	invoke assets.compile
compile-assets:
	invoke assets.compile
build-dict:
	invoke dictionary.build
build-search-indexes:
	invoke search.index

sync-production-fonts:
	invoke fonts.download_nonfree

create-dev-offline-export:
	invoke exports.offline.create_dev
create-dev-db-export:
	invoke exports.db.create_dev

create-production-offline-export:
	invoke exports.offline.create_production
create-production-db-export:
	invoke exports.db.create_production

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

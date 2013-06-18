all:

deploy-staging:
	ssh sc-staging@vps.suttacentral.net \
		'source $$HOME/.virtualenvs/suttacentral/bin/activate && \
		cd $$HOME/suttacentral && \
		git pull && \
		pip install -r requirements.txt && \
		sudo supervisorctl restart sc-staging'

deploy-production:
	ssh sc-production@vps.suttacentral.net \
		cd $$HOME/suttacentral && \
		git pull && \
		cd text && \
		git pull

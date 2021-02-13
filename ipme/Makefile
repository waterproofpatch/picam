.PHONY: test

all: deploy

deploy: 
	git push heroku master

droptables:
	heroku pg:reset DATABASE_URL --confirm ipme-proxy

test:
	python -m pytest -xs test

clean:
	rm -rf tags src/__pycache__ src/test.db

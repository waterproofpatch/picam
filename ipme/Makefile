.PHONY: test

all: deploy

deploy: 
	git push heroku master

droptables:
	heroku pg:reset DATABASE_URL --confirm ipme-proxy

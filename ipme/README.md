# IP Proxy

## Deploy

```bash
git commit -am "a message"
git push heroku master
firefox https://ipme-proxy.herokuapp.com/
```

## Logs

```bash
heroku logs --tail
```

## Drop Database

```bash
heroku pg:reset DATABASE_URL
```

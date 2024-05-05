# Memecry

A meme website built with [relax-py](https://github.com/crpier/relax-py)

## Running

- Clone the repository
- `poetry install`
- `cp example.env .env`
- edit `.env` to your liking (only the args in the first paragraph are required)
- `dotenv run python memecry/main.py`

## Deployment

The deployment was configured with [dokku](https://dokku.com/) in mind, but it should work with other platforms.

The only thing to bear in mind when using `dokku` is that the default size for uploads is too small, so you need to increase it.
Can do it with this [plugin](https://github.com/Zeilenwerk/dokku-nginx-max-upload-size))

You can also scale the app to have more workers, with no issue, with something like

```sh
dokku ps:scale memecry web=5
```

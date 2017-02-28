= Scrapper for SEO Monitor

Scrapy was used as primary framework

After installing requirements you can run spider by command:

`scrapy crawl [spider-name]`

== Settings
Most of settings are in `scrapper/settings.py`

=== To use MongoDb as your store you need to:
* set env variables: `MONGODB_HOST, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION` (see more in `settings.py`)
* uncomment `scrapper.pipelines.MongoDBPipeline` in `settings.py`

=== To save screenshots you need to:
* run Splash service (i.e. using Docker: http://splash.readthedocs.io/en/stable/install.html#os-x-docker)
* set SPLASH_URL env variable
* uncomment `scrapper.pipelines.ScreenshotPipeline` in `settings.py`

=== To use Pusher you need to:
* set env variable `PUSHER_ENABLED` to `True`
* set env variables: `PUSHER_ENABLED, PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET`

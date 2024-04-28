# Setup instructions specifically for setting up The Grand Hunt

## Set up the environment

The easiest way to begin is by copying a previous year's folder in `/var/www`. For example, to copy the 2024 folder to 2025, first `cd /var/www`, then run `cp -a 2024 2025`.

`cd` into the new directory.

Remove any content specific to the past year's game. This can be done with `git reset --hard` for most files. Also make sure to reset the database by deleting `db.sqlite3`.

## Move to the new year

In `/gph/settings/prod.py`, update `ALLOWED_HOSTS` to include the new year's subdomain, if relevant.

In `/puzzles/hunt_config.py`, update any relevant information such as the start and end date.

At this stage you can begin populating any other static content such as the homepage.

## Get the server running

### Django

Run `./manage.py runserver` to initialize settings. You can immediately press control-C to exit the running server once console messages have stopped. 

The previous command likely displayed a warning about database migrations. Run `./manage.py migrate` to update the database.

### Gunicorn

Begin setting up the Gunicorn gateway by creating the service file. Execute `sudo nano /etc/systemd/system/gph{year}.service`, replacing `{year}` with the year's hunt being created. This will open the nano text editor.

Paste the following block into that editor
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/{year}
ExecStart=/usr/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/{year}/gph.sock gph.wsgi:application

[Install]
WantedBy=multi-user.target
```
Ensure that you replace both usages of the placeholder `{year}` with the year you're setting up.

Then, save and close the nano editor. Use control-s to save and control-x to exit.

Enable this service with the following commands:
```bash
sudo systemctl start gph{year}
sudo systemctl enable gph{year}
```

Ensure you once again replace `{year}` with the year your are setting up. Then, check the status of the service with
```bash
sudo systemctl status gph{year}
```
You should see "Active: active (running)"

### Nginx
Create a new Nginx site with `sudo nano /etc/nginx/sites-available/{year}`

Paste the following block, and replace `{year}` with the year
```
server {
    listen 80;
    server_name {year}.grandhuntdigital.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/{year};
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/{year}/gph.sock;
    }
}
```

Enable the site by running `sudo ln -s /etc/nginx/sites-available/{year} /etc/nginx/sites-enabled`

Confirm the configuration is valid with the command `sudo nginx -t`

Finally, restart nginx with `sudo systemctl restart nginx`

The site should now be available. You can check in your browser by going to `{year}.grandhuntdigital.com`.

## SSL encryption with Certbot

One final step is to add SSL encryption so we support HTTPS and security that comes along with it. 

Due to limitations with LetsEncrypt, our automated SSL provider, the wildcard subdomain DNS record we use isn't good enough for this step. So while you can access the site (without SSL) at this point, we need to add another DNS record explicitly setting up this game.

Go into the admin interface of our domain registrar (NameSilo at the time of writing) and find the DNS records for the grandhuntdigital.com domain and add a new entry. Unless you've recently made some infrastructure changes, it'll probably be the same as the entry for the past year.
| Hostname | Type | Value | TTL |
|---|---|---|---|
| `{year}` | A | 144.24.46.133 | 7200 |

Save this and wait for it to propogate. It may take some time to propogate (up to two hours) so if the following step fails, retry in a bit.

Run `sudo certbot --nginx -d {year}.grandhuntdigital.com` and fill in the requested fields.


# Commands for later

## Launching a hunt

When launching a hunt, you'll want to make the main `grandhuntdigital.com` domain point to the new hunt's socket. Edit the Nginx config file for the main site with `sudo nano /etc/nginx/sites-available/main-site` and change both instances of the previous year to the current year. Specifically, the entry with `root /var/www/{previous-year}` and `proxy_pass http://unix:/var/www/{previous-year}/gph.sock;` need to be updated to the current year..

Finally, confirm the new Nginx configuration is valid using `sudo nginx -t` and restart Nginx with `sudo systemctl restart nginx`.

## Troubleshooting
If you make changes to the Gunicorn files (`/etc/systemd/system/gph{year}.service`), you will need to reboot Gunicorn.
```bash
sudo systemctl daemon-reload
sudo systemctl restart gph{year}
```

When you make changes to pages, you may also need to run `sudo systemctl restart gph{year}`

If you need to restart Nginx, you can use `sudo systemctl restart nginx`


# Running the Site Locally
During development, you can also run a local instance of the puzzle hunt site

### Setup
1. Clone this repo, e.g. `git clone https://github.com/spiffycoffee/grandhunt-2024.git`
2. (Optional, but recommended) Create a virtualenv to isolate the project's dependencies from your system Python
```
python -m venv venv
```
then activate the virtualenv
```
source venv/bin/activate
```
3. Install the project dependencies, `pip install -r requirements.txt`
4. Establish a salt value to make Django happy, since this is local the value doesn't really matter
`export SECRET_KEY=*mash the keyboard*`
5. Now everything is installed and ready to run. For the initial run, perform the Django migrations to setup the DB, and create an admin user for yourself
```
python manage.py migrate
python manage.py createsuperuser
```

### Run Locally
If you've rebooted / closed your terminal since last time, activate the virtualenv again: `source venv/bin/activate`

6. Start the Django server, `python manage.py runserver`
7. Access the hunt site via your browser at `localhost:8000`

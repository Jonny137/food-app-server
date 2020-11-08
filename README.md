# Food App Server
Backend server for a recipe website.

<img src="https://cdn3.iconfinder.com/data/icons/logos-and-brands-adobe/512/267_Python-512.png"
     alt="Markdown Node icon"
     height="30px"
/>&nbsp;&nbsp;&nbsp;
<img src="https://cdn.onlinewebfonts.com/svg/img_437027.png"
     alt="Markdown Node icon"
     height="30px"
/>&nbsp;&nbsp;
<img src="https://wiki.postgresql.org/images/a/a4/PostgreSQL_logo.3colors.svg"
     alt="Markdown Node icon"
     height="30px"
/>&nbsp;&nbsp;&nbsp;
<img src="https://www.docker.com/sites/default/files/d8/2019-07/horizontal-logo-monochromatic-white.png"
     alt="Markdown Node icon"
     height="30px"
/>

## Usage

The app requires an `.env` file with the following variables:
```
DB_URI=postgresql://<username>:<password>@<database_url>:<port>/<database_name>
DB_TEST_URI=postgresql://<username>:<password>@database_url:<port>/<test_database_name>
HUNTER_KEY=<secret key provided by Hunter.io>
CLEARBIT_KEY=<secret key provided by Clearbit>
SECRET_KEY=<flask_secret_key>
```
Links for [Hunter.io](https://hunter.io/) and [Clearbit](https://clearbit.com/).

### Without Docker
It is advised to work in a virtual environment. Create one using the following command:
```
python3 -m venv venv
```

Activating **venv**:
- Windows OS: `./venv/Scripts/activate`
- Unix/Mac OS: `source venv/bin/activate`

Install the required packages into the newly created venv:
```
pip install -r requirements.txt
```

Run the following commands to setup the tables in your database:
```
flask db migrate
flask db upgrade
```

To start the server run:
```
flask run
```

### Using Docker
There are two separate Docker containers, one for hosting the Postgres database and the other one for Flask service.
The app now also requires a `.postgresenv` file with the following variables:
```
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<database_name>
```
This will ensure that the Docker hosted database credentials are secure.
To build and run Docker containers use the following command:
```
docker-compose up --build --remove-orphans
```
## Test
To run tests:
```
python tests.py
```

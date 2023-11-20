# My City

Project work for the course "Databases and Web Programming".

## Description

My City allows people to easily know what's going on in their city, inform about things that are not as they should be, and vote in various polls.

Users are required to register with the following information:
- username (unique),
- password,
- birthday (optional),
- gender (optional),
- zip code (optional).

All users can:
- sign in and sign out,
- view news, notices, and polls,
- create notices about things that need improvement,
- support notices created by other users,
- vote in polls with a thumb up or down,
- see anonymized poll analytics about respondents,
- give feedback,
- edit their profile (except username),
- view notices they have created.

Only admins can:
- create news and polls,
- read user feedback,
- disable user accounts.

## Installation

1. Clone the repository.

2. Go to its root folder.

3. Create a virtual environment with:

    `python3 -m venv venv`

4. Activate the virtual environment with:

    `source venv/bin/activate`

5. Install required dependencies with:

    `pip install -r ./requirements.txt`

6. Add a .env file with `DATABASE_URL` and `SECRET_KEY`:

    ```
    DATABASE_URL=<your_local_database_address>
    SECRET_KEY=<a_random_string_to_enable_app_sessions_properly>
    ```

    The `DATABASE_URL` depends on your system and PostgreSQL setup.

    The `SECRET_KEY` can be generated with, for example:

    ```
    $ python3
    >>> import secrets
    >>> secrets.token_hex(16)
    ```

7. Set your database to use the required schema with: 
    `psql database_name < schema.sql`

8. Run the app with:

    `flask run`

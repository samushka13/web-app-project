# My City (Oma kaupunki)

Project work for the course "Databases and Web Programming".

## Description

My City allows people to easily know what's going on in their city, inform about things that are not as they should be, and vote in various polls. The website language is Finnish.

Users are required to register with the following information:
- username (unique),
- password,
- date of birth (optional),
- gender (optional),
- zip code (optional),
- admin status (optional).

All users can:
- sign in and sign out,
- view news, notices, polls, and feedback,
- see view counts of news and notices,
- create notices,
- support notices created by others,
- see support counts of notices,
- see status history of notices,
- vote in polls (for or against),
- see poll vote counts,
- see anonymized poll voter distributions,
- give feedback,
- edit their profile (except username),
- change their password,
- delete their account.

Only admins can:
- create news and polls,
- edit statuses of news, notices, polls, and feedback,
- view archived news, notices, polls, and feedback,
- see who has changed statuses of news, notices, polls, and feedback,
- disable user accounts.

## Installation

The project can only be run locally. Therefore, you need to ensure that your system environment meets the basic requirements. For example, working Python and PostgreSQL installations are required (tested on v3.9 and v14.10, respectively). Instructions for installing these on your system can be easily found on the web.

After your environment is all set, the project can be run with the following instructions:

1. Clone the repository.

2. Go to its root folder.

3. Create a virtual environment with:

    `python3 -m venv venv`

4. Activate the virtual environment with:

    `source venv/bin/activate`

5. Install required dependencies with:

    `pip install -r ./requirements.txt`

6. Add a `.env` file that includes:

    ```
    DATABASE_URL=<your_local_database_address>
    SECRET_KEY=<random_string_to_enable_sessions_properly>
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

8. Run the project with:

    `flask run`

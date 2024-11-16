import argparse

from django.core.management.utils import get_random_secret_key


def generate_content(mode: str):
    """
    Generate the content of the .env file
    mode is either 'DEV' or 'PROD'
    """
    secret_key = get_random_secret_key()
    if mode == "DEV":
        return [
            f"SECRET_KEY='{secret_key}'",
            "DEBUG=True",
            "ALLOWED_HOSTS='127.0.0.1'",
            "DATABASE_URL='sqlite:///./db.sqlite3'",
            "EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'",
            f"MODE='{mode}'",
        ]


def main():
    """
    Generate a .env file in the current directory
    """
    parser = argparse.ArgumentParser(description='Generate a .env file in the current directory.')
    parser.add_argument(
        'mode', choices=['DEV', 'PROD'], help='The mode to generate the .env file in.', default='DEV'
    )

    content = generate_content(mode=parser.parse_args().mode)
    with open('.env', 'w') as f:
        for line in content:
            f.write(f"{line}\n")


if __name__ == '__main__':
    main()

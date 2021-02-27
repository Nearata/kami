from argon2 import PasswordHasher
from click import command as click_command
from click import option as click_option

from kami.database import db, Users


@click_command()
@click_option("-u", "--username", prompt="New admin username", type=str, required=True)
@click_option("-p", "--password", prompt="New admin password", type=str, required=True, hide_input=True, confirmation_prompt=True)
def main(username: str, password: str) -> None:
    db.connect()

    user = Users.get_or_none(username=username)

    if not user:
        ph = PasswordHasher()
        hashed = ph.hash(password)

        Users.create(
            username=username,
            password=hashed,
            is_admin=True
        )
        print("User created.")
    else:
        print("User already exists.")

    db.close()


if __name__ == "__main__":
    main()

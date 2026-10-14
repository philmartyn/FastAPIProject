"""Password hashing and session helpers.

We use the `bcrypt` library directly (passlib is unmaintained and breaks with
recent bcrypt releases).

TODO (you):

  - hash_password(password: str) -> str
      bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

  - verify_password(password: str, hashed: str) -> bool
      bcrypt.checkpw(password.encode(), hashed.encode())

  - log_in(request, user_id)  -> store the id in the signed session:
      request.session["user_id"] = user_id

  - log_out(request)          -> request.session.clear()

Docs: https://pypi.org/project/bcrypt/
"""


def hash_password(password: str) -> str:
    """Return a bcrypt hash of `password`."""
    # TODO
    raise NotImplementedError


def verify_password(password: str, hashed: str) -> bool:
    """Return True if `password` matches the stored `hashed` value."""
    # TODO
    raise NotImplementedError

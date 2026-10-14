"""Business logic shared by the HTML routes and the JSON API.

Keeping queries here (instead of inside route functions) means the HTMX
endpoints in `app/routers/notes.py` and the JSON endpoints in
`app/routers/api.py` do the exact same thing -- a nice design point to show off.

TODO (you) -- implement, all scoped to a given user so nobody can touch another
user's notes:

  - list_notes(db, user)                    -> list[Note] (pinned first)
  - get_note(db, user, note_id)             -> Note | None
  - create_note(db, user, title, body)      -> Note
  - update_note(db, user, note_id, **fields)-> Note | None
  - delete_note(db, user, note_id)          -> bool
  - toggle_pin(db, user, note_id)           -> Note | None
"""

# TODO: imports...

"""SuttaCentral server environment.

Usage: cherryd -i sc.server

Note: This module is not intended to be imported from another module or
program.
"""

from sc import app, scimm

app.setup()
app.mount()
scimm.start_updater()

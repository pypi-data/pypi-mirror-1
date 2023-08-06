from flamboyantsshd import handlers

handler = handlers.IPTables
#handler = handlers.DebugHandler

class Tolerance:
    base_penalty = 0
    password_failure = 5
    invalid_user = 3

class Penalties:
    password_failure = 1
    invalid_user = 1

from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase("db.sqlite")


def getdb():
    return db

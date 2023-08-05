from five.intid.keyreference import IConnection

def add_object_to_connection(ob, event):
    connection = IConnection(self, None)
    if None is not connection:
        connection.add(ob)

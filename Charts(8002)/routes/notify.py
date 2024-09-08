from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)

async def notify_clients(name,connected_clients):
    message = json.dumps({
        "response": 'data',
        "name":name
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

async def gridChange_notifiy(connected_clients):
    message = json.dumps({
        "response": 'grid',
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

async def widget_notifiy(connected_clients):
    message = json.dumps({
        "response": 'widget',
    }, cls=JSONEncoder)

    for client in connected_clients:
        await client.send_text(message)

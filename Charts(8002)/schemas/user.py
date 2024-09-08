def EmailcallEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "Date": str(item["Date"]),
        "data": list(item["data"]),
    }


def EmailcallsEntity(entity) -> list:
    return [EmailcallEntity(item) for item in entity]

def WidgetsEntry(item) -> dict:
    widget_entry = {
        "id": str(item["_id"]),
        "title": str(item["title"]),
        "chartType": str(item["chartType"]),
        "sources": item["sources"],
        "keywords": item["keywords"],
        "email": str(item["email"]),
        "grid": dict(item["grid"]),
        "status": str(item["status"]),
    }

    widget_entry["xAxis"] = str(item.get("xAxis", ""))
    widget_entry["yAxis"] = str(item.get("yAxis", ""))
    widget_entry["topics"] = item.get("topics", [])

    return widget_entry


def WidgetEntry(entity) -> list:
    return [WidgetsEntry(item) for item in entity]

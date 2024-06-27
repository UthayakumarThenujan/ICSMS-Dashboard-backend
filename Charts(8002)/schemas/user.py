from fastapi import HTTPException


def callEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "Sentiment": dict(item["Sentiment"]),
        "Date": str(item["Date"]),
        "ID": list(item["ID"]),
        "Word": list(item["Word"]),
        "Categories": dict(item["Categories"]),
    }


def callsEntity(entity) -> list:
    return [callEntity(item) for item in entity]

def EmailcallEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "Date": str(item["Date"]),
        "data": list(item["data"]),
        # "ID": list(item["ID"]),
        # "Word": list(item["Word"]),
        # "Categories": dict(item["Categories"]),
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
        # widget_entry["yAxis"] = str(item.get("yAxis", ""))

    return widget_entry


def WidgetEntry(entity) -> list:
    return [WidgetsEntry(item) for item in entity]

def bartChartEntry(item) -> dict:
    return {
        "Date": str(item["Date"]),
        "Categories": dict(item["Categories"]),
    }

def bartChartsEntry(entity) -> list:
    return [bartChartEntry(item) for item in entity]
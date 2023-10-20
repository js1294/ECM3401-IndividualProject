"""
Program to get live AIS data from AISStream.io and convert into a CSV file after a period of time.
Author: Jack Shaw
"""
import asyncio
import time
import csv
import traceback
from datetime import datetime, timezone

import websockets
import orjson

async def connect_ais_stream(api_key: str, bounding_box: list, message_type: str, timeout: int):
    """
    Connects to AISStream.io websocket, creating a list of the data collected.
    """
    messages = []
    start = time.time()
    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
            sub_message = {"APIKey": api_key, # API key to allow authorisation.
                           "BoundingBoxes": [bounding_box], # Coordinates that restrict the data to be collected.
                           "FilterMessageTypes": [message_type]} # Filters what message types should be shown.

            sub_message_json = orjson.dumps(sub_message)
            await websocket.send(sub_message_json)
            async for message_json in websocket:
                # When the time has been reached the data collected should be converted into a CSV file.
                if (time.time() - start) >= timeout:
                    convert_to_csv(messages, message_type)
                    return
                message = orjson.loads(message_json)
                # Ignore any messages that are invalid.
                if str(message["Message"][message_type]["Valid"]) != "True":
                    continue

                if message_type == "AddressedSafetyMessage" or \
                   message_type == "SafetyBroadcastMessage":
                    print()

                messages.append(message_formatter(message, message_type))
                print((time.time() - start))
    # The websocket connect could be closed since the API key is not valid or because of loss of connection.
    # If loss of connection occurs convert any data found into a CSV file.
    except websockets.exceptions.ConnectionClosedError:
        if len(messages) > 1:
            convert_to_csv(messages, message_type)
        elif len(messages) == 1 and messages[-1]["error"] == "Api Key Is Not Valid":
            print("Error - Api Key Is Not Valid. Please check the Api Key and try again.")
    except Exception:
        print(traceback.format_exc())

def message_formatter(message: dict, message_type: str) -> dict:
    """
    Formats the data depending on the message type entered.
    """
    formatted_message = {}
    ais_message = message["Message"][message_type]
    if message_type == "PositionReport":
        formatted_message = {"UserID": ais_message["UserID"],
                             "NavigationalStatus": ais_message["NavigationalStatus"],
                             "RateOfTurn": ais_message["RateOfTurn"],
                             "Sog": ais_message["Sog"],
                             "PositionAccuracy": ais_message["PositionAccuracy"],
                             "Longitude": ais_message["Longitude"],
                             "Latitude": ais_message["Latitude"],
                             "Cog": ais_message["Cog"],
                             "TrueHeading": ais_message["TrueHeading"],
                             "Source": 0,
                             "Timestamp": ais_message["Timestamp"],
                             "UTCTime": datetime.now(timezone.utc)}
    elif message_type == "ExtendedClassBPositionReport":
        formatted_message = {"UserID": ais_message["UserID"],
                             "NavigationalStatus": 16,
                             "RateOfTurn": 128,
                             "Sog": ais_message["Sog"],
                             "PositionAccuracy": ais_message["PositionAccuracy"],
                             "Longitude": ais_message["Longitude"],
                             "Latitude": ais_message["Latitude"],
                             "Cog": ais_message["Cog"],
                             "TrueHeading": ais_message["TrueHeading"],
                             "Source": 1,
                             "Timestamp": ais_message["Timestamp"],
                             "UTCTime": datetime.now(timezone.utc)}
    elif message_type == "LongRangeAisBroadcastMessage":
        formatted_message = {"UserID": ais_message["UserID"],
                             "NavigationalStatus": ais_message["NavigationalStatus"],
                             "RateOfTurn": 128,
                             "Sog": ais_message["Sog"],
                             "PositionAccuracy": ais_message["PositionAccuracy"],
                             "Longitude": ais_message["Longitude"],
                             "Latitude": ais_message["Latitude"],
                             "Cog": ais_message["Cog"],
                             "TrueHeading": 511,
                             "Source": 2,
                             "Timestamp": 60,
                             "UTCTime": datetime.now(timezone.utc)}
    elif message_type == "ShipStaticData":
        formatted_message = {"UserID": ais_message["UserID"],
                             "ImoNumber": ais_message["ImoNumber"],
                             "Name": ais_message["Name"],
                             "CallSign": ais_message["CallSign"],
                             "Type": ais_message["Type"],
                             "Draught": ais_message["MaximumStaticDraught"],
                             "DimensionA": ais_message["Dimension"]["A"],
                             "DimensionB": ais_message["Dimension"]["B"],
                             "DimensionC": ais_message["Dimension"]["C"],
                             "DimensionD": ais_message["Dimension"]["D"],
                             "EtaMonth": ais_message["Eta"]["Month"],
                             "EtaDay": ais_message["Eta"]["Day"],
                             "EtaHour": ais_message["Eta"]["Hour"],
                             "EtaMinute": ais_message["Eta"]["Minute"],
                             "Destination": ais_message["Destination"],
                             "FixType": ais_message["FixType"],
                             "UTCTime": datetime.now(timezone.utc)}
    elif message_type == "StaticDataReport":
        formatted_message = {"UserID": ais_message["UserID"],
                             "ImoNumber": 0,
                             "Name": ais_message["ReportA"]["Name"],
                             "CallSign": ais_message["ReportB"]["CallSign"],
                             "Type": ais_message["ReportB"]["ShipType"],
                             "Draught": 0,
                             "DimensionA": ais_message["ReportB"]["Dimension"]["A"],
                             "DimensionB": ais_message["ReportB"]["Dimension"]["B"],
                             "DimensionC": ais_message["ReportB"]["Dimension"]["C"],
                             "DimensionD": ais_message["ReportB"]["Dimension"]["D"],
                             "EtaMonth": 0,
                             "EtaDay": 0,
                             "EtaHour": 24,
                             "EtaMinute": 60,
                             "Destination": "@@@@@@@@@@@@@@@@@@@@",
                             "FixType": ais_message["ReportB"]["FixType"],
                             "UTCTime": datetime.now(timezone.utc)}
    elif message_type == "AidsToNavigationReport":
        formatted_message = {"UserID": ais_message["UserID"],
                             "Name": ais_message["Name"],
                             "NameExtension": ais_message["NameExtension"],
                             "Type": ais_message["Type"],
                             "PositionAccuracy": ais_message["PositionAccuracy"],
                             "OffPosition": ais_message["OffPosition"],
                             "VirtualAtoN": ais_message["VirtualAtoN"],
                             "Longitude": ais_message["Longitude"],
                             "Latitude": ais_message["Latitude"],
                             "DimensionA": ais_message["Dimension"]["A"],
                             "DimensionB": ais_message["Dimension"]["B"],
                             "DimensionC": ais_message["Dimension"]["C"],
                             "DimensionD": ais_message["Dimension"]["D"],
                             "UTCTime": datetime.now(timezone.utc)}
    elif message_type == "BaseStationReport":
        formatted_message = {"UserID": ais_message["UserID"],
                             "Name": "Station",
                             "NameExtension": "",
                             "Type": 34,
                             "PositionAccuracy": ais_message["PositionAccuracy"],
                             "OffPosition": "FALSE",
                             "VirtualAtoN": "FALSE",
                             "Longitude": ais_message["Longitude"],
                             "Latitude": ais_message["Latitude"],
                             "DimensionA": 0,
                             "DimensionB": 0,
                             "DimensionC": 0,
                             "DimensionD": 0,
                             "UTCTime": datetime.now(timezone.utc)}
    return formatted_message

def convert_to_csv(messages: list, message_type: str):
    """
    Converts the collected formatted messages into a CSV file.
    """
    field_names = []
    file_name = ""
    if (message_type == "PositionReport" or message_type == "LongRangeAisBroadcastMessage"
        or message_type == "ExtendedClassBPositionReport"):
        field_names = ["UserID", "NavigationalStatus", "RateOfTurn",
                       "Sog", "PositionAccuracy", "Longitude","Latitude",
                       "Cog", "TrueHeading", "Source", "Timestamp", "UTCTime"]
        file_name = "PositionReport"
    elif message_type == "ShipStaticData" or message_type == "StaticDataReport":
        field_names = ["UserID", "ImoNumber", "Name", "CallSign", "Type", "Draught",
                       "DimensionA", "DimensionB", "DimensionC", "DimensionD", "EtaMonth",
                       "EtaDay", "EtaHour", "EtaMinute", "Destination", "FixType", "UTCTime"]
        file_name = "ShipStaticData"
    elif message_type == "AidsToNavigationReport" or message_type == "BaseStationReport":
        field_names = ["UserID", "Name", "NameExtension", "Type", "PositionAccuracy",
                       "OffPosition", "VirtualAtoN", "Longitude", "Latitude",
                       "DimensionA", "DimensionB", "DimensionC", "DimensionD", "UTCTime"]
        file_name = "AidsToNavigationReport"

    with open(f"CSV/{file_name}.csv", "a", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names, lineterminator='\n')
        writer.writerows(messages)

def get_api_keys() -> list:
    """
    Gets the API keys from the API keys configuration file.
    This is done to ensure the API keys are not released.
    """
    api_keys = []
    with open("API keys", "r") as api_file:
        for api_key in api_file.readlines():
            api_keys.append(api_key.replace("\n",""))
    return api_keys

async def main():
    """
    Main function used to create each task to collect data in parallel.
    """

    api_keys = get_api_keys()

    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(connect_ais_stream( api_keys[0],
                                      [[51.18, -2.25],[53.415, -8.39]],
                                      "PositionReport",
                                           6000))

        task_group.create_task(connect_ais_stream(api_keys[1],
                                      [[53.415, -2.25],[55.65, -8.39]],
                                      "PositionReport",
                                           6000))

        task_group.create_task(connect_ais_stream(api_keys[2],
                                     [[51.18, -2.25],[55.65, -8.39]],
                                     "ExtendedClassBPositionReport",
                                          6000))

        task_group.create_task(connect_ais_stream(api_keys[3],
                                     [[51.18, -2.25],[55.65, -8.39]],
                                     "LongRangeAisBroadcastMessage",
                                          6000))

        task_group.create_task(connect_ais_stream(api_keys[4],
                                     [[50, 0],[60, -10]],
                                     "ShipStaticData",
                                          8000))

        task_group.create_task(connect_ais_stream(api_keys[5],
                                     [[50, 0],[60, -10]],
                                     "StaticDataReport",
                                          8000))

        task_group.create_task(connect_ais_stream(api_keys[6],
                                     [[50, 0],[60, -10]],
                                     "AidsToNavigationReport",
                                          8000))

        task_group.create_task(connect_ais_stream(api_keys[7],
                                     [[50, 0],[60, -10]],
                                     "BaseStationReport",
                                          8000))

        task_group.create_task(connect_ais_stream(api_keys[6],
                                     [[50, 0],[60, -10]],
                                     "SafetyBroadcastMessage",
                                          8000))

        task_group.create_task(connect_ais_stream(api_keys[7],
                                     [[50, 0],[60, -10]],
                                     "AddressedSafetyMessage",
                                          8000))

if __name__ == "__main__":
    asyncio.run(main())

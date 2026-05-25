from app.services.storage_service import StorageService
from app.services.schema_service import SchemaService


class TrackerService:

    @staticmethod
    def create_tracker(tracker_name: str, schema: dict):

        existing = StorageService.read_tracker(tracker_name)

        if existing:
            return {
                "success": False,
                "message": "Tracker already exists"
            }

        tracker_data = {
            "tracker_name": tracker_name,
            "schema": schema,
            "data": []
        }

        StorageService.write_tracker(tracker_name, tracker_data)

        return {
            "success": True,
            "message": f"Tracker '{tracker_name}' created"
        }
    

    @staticmethod
    def list_trackers():

        from app.config import DATA_DIR

        trackers = [
            file.stem
            for file in DATA_DIR.glob("*.json")
        ]

        return {
            "success": True,
            "data": trackers
        }


    @staticmethod
    def add_data(tracker_name: str, data: dict):

        tracker = StorageService.read_tracker(tracker_name)

        if not tracker:
            return {
                "success": False,
                "message": "Tracker not found"
            }

        schema = tracker["schema"]

        valid, message = SchemaService.validate_data(schema, data)

        if not valid:
            return {
                "success": False,
                "message": message
            }

        existing_data = tracker["data"]

        data["id"] = len(existing_data) + 1

        existing_data.append(data)

        tracker["data"] = existing_data

        StorageService.write_tracker(tracker_name, tracker)

        return {
            "success": True,
            "message": "Data added successfully",
            "data": data
        }
    

    @staticmethod
    def fetch_data(tracker_name: str):

        tracker = StorageService.read_tracker(tracker_name)

        if not tracker:
            return {
                "success": False,
                "message": "Tracker not found"
            }

        return {
            "success": True,
            "data": tracker["data"]
        }
    

    @staticmethod
    def delete_data(tracker_name: str, record_id: int):

        tracker = StorageService.read_tracker(tracker_name)

        if not tracker:
            return {
                "success": False,
                "message": "Tracker not found"
            }

        tracker["data"] = [
            item
            for item in tracker["data"]
            if item["id"] != record_id
        ]

        StorageService.write_tracker(tracker_name, tracker)

        return {
            "success": True,
            "message": "Data deleted successfully"
        }
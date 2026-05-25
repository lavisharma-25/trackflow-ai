from app.services.tracker_service import TrackerService


class Router:

    @staticmethod
    def execute(command: dict):

        intent = command.get("intent")

        if intent == "CREATE_TRACKER":
            return TrackerService.create_tracker(
                tracker_name=command["tracker"],
                schema=command["data"]
            )

        elif intent == "LIST_TRACKERS":
            return TrackerService.list_trackers()

        elif intent == "ADD_DATA":
            return TrackerService.add_data(
                tracker_name=command["tracker"],
                data=command["data"]
            )

        elif intent == "FETCH_DATA":
            return TrackerService.fetch_data(
                tracker_name=command["tracker"]
            )

        elif intent == "DELETE_DATA":
            return TrackerService.delete_data(
                tracker_name=command["tracker"],
                record_id=command["data"]["id"]
            )

        return {
            "success": False,
            "message": "Unknown intent"
        }
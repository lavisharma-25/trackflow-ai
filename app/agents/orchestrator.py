from app.agents.intent_parser import IntentParser
from app.agents.router import Router


class AgentOrchestrator:

    @staticmethod
    def process(query: str):

        parsed_command = IntentParser.parse(query)

        response = Router.execute(parsed_command)

        return {
            "query": query,
            "parsed_command": parsed_command,
            "response": response
        }
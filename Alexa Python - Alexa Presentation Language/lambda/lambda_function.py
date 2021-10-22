import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.utils import get_supported_interfaces

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from logic import evaluate_choices
from random import choices

import json
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
from apl.apl_content import apl_main_template, create_url, _load_apl_document, get_apl_content

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['alexas_choice'] = choices(['rock', 'paper', 'scissors'])
        speak_output = "Welcome to the best game in the universe. Please select rock, paper, or scissors. "
        
        # APL config
        aptText = "Welcome to The Rock Paper Scissors Game"
        aplImage = create_url("Media/rps.jpeg")
        aplLogo = create_url("Media/logo.png")
        aplHome = apl_main_template(aplImage, aptText, aplLogo)
        
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    document=_load_apl_document("./apl/responsive.json"),
                    datasources = aplHome
                )
            )

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class answerIntentHandler(AbstractRequestHandler):
    """Handler for the answer Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("answerIntent")(handler_input)

    def handle(self, handler_input):
        # extract alexa's choice from session attributes 
        session_attributes = handler_input.attributes_manager.session_attributes
        alexas_choice = session_attributes['alexas_choice'][0]
        # get the user's choice
        users_choice = handler_input.request_envelope.request.intent.slots["rpschoice"].value
        # evaluate the choices based on the logic of the game
        winner, speak_output = evaluate_choices(alexas_choice, users_choice)
        # generate APL
        aplanswer = get_apl_content(winner)
        # do not end the session
        handler_input.response_builder.set_should_end_session(False)
        speak_output += " Play again.. "
        # reinitiate the game for the next game
        session_attributes['alexas_choice'] = choices(['rock', 'paper', 'scissors'])
        # APL handler
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    document=_load_apl_document("./apl/answer.json"),
                    datasources = aplanswer
                )
            )

        return handler_input.response_builder.speak(speak_output).response

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "This is the rock, paper, scissors game. Select one of these and see if you gonna beat me."
        
        # do not end the session
        handler_input.response_builder.set_should_end_session(False)

        return handler_input.response_builder.speak(speak_output).response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Thanks for your time. Goodbye!"

        return handler_input.response_builder.speak(speak_output).response

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can select rock, paper, or scissors, and see if you gonna beat me."
        reprompt = "I didn't catch that. You can select rock, paper, or scissors, and see if you gonna beat me."

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(answerIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
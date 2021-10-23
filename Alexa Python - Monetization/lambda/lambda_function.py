import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.utils import get_supported_interfaces

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor
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
        # i18n
        data = handler_input.attributes_manager.request_attributes["_"]
        
        session_attributes['alexas_choice'] = choices([data["ROCK"], data["PAPER"], data["SCISSORS"]])
        speak_output = data["WELCOME"]
        
        # APL config
        aplText = data["APLTEXT"]
        aplImage = create_url("Media/rps.jpeg")
        aplLogo = create_url("Media/logo.png")
        aplHome = apl_main_template(aplImage, aplText, aplLogo, data)
        
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
        
        # i18n
        data = handler_input.attributes_manager.request_attributes["_"]

        # evaluate the choices based on the logic of the game
        winner, speak_output = evaluate_choices(alexas_choice, users_choice, data)
        speak_output += data['PLAYAGAIN']
        
        # generate APL
        aplanswer = get_apl_content(winner, data)
        # do not end the session
        handler_input.response_builder.set_should_end_session(False)
        
        
        # reinitiate the game for the next game
        session_attributes['alexas_choice'] = choices([data["ROCK"], data["PAPER"], data["SCISSORS"]])
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
        
        # i18n
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data['HELP']
        
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
        
        # i18n
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data['STOP']

        return handler_input.response_builder.speak(speak_output).response

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        
        # i18n
        data = handler_input.attributes_manager.request_attributes["_"]
        speech = data['FALLBACK']
        reprompt = data['FALLBACKREP']

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
        
        # i18n
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data['TROUBLE']

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))

        # localized strings stored in language_strings.json
        with open("./language/language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        if locale[:2] in language_data:
            data = language_data[locale[:2]]
            # if a more specialized translation exists, then select it instead
            # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
            # then pick that instead
            if locale in language_data:
                data.update(language_data[locale])
        else:
            data = language_data[locale]
        handler_input.attributes_manager.request_attributes["_"] = data

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

sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
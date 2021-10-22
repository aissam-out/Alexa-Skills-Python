
def apl_main_template(background_url, text, logo):
    output = {
        "headlineTemplateData": {
            "type": "object",
            "objectId": "headlineSample",
            "properties": {
                "backgroundImage": {
                    "sources": [
                        {
                            "url": background_url,
                            "size": "large"
                        }
                    ]
                },
                "textContent": {
                    "primaryText": {
                        "type": "PlainText",
                        "text": text
                    },
                },
                "logoUrl": logo,
                "hintText": "Try, \"Alexa, What are the rules of this game?\"",
            }
        }
    }
    
    return output
    
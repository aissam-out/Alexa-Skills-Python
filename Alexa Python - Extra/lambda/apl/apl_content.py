import json
from ask_sdk_model import ui
from apl.utils import create_presigned_url

def apl_main_template(background_url, text, logo, data):
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
                "hintText": data['HINTTEXT'],
            }
        }
    }
    
    return output

def create_url(key):
    img_url_raw = str(ui.Image(large_image_url=create_presigned_url(key)))
    length = len(img_url_raw)
    return img_url_raw[21:length-28]

def _load_apl_document(file_path):
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

def get_apl_content(winner, data):
    aplLogo = create_url("Media/logo.png")
    if winner == "alexa":
        aptText = data["APLLOSER"]
        aplImage = create_url("Media/loser.jpeg")
    elif winner == "user":
        aptText = data["APLWINNER"]
        aplImage = create_url("Media/winner.jpeg")
    else:
        aptText = data["APLDRAW"]
        aplImage = create_url("Media/draw.jpeg")
    
    aplResult = apl_main_template(aplImage, aptText, aplLogo, data)
    
    return aplResult


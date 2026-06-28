from openai import OpenAI
import re
import base64

def id_classify_image(image_path, api_key):

    id_classes = [
        "ID",
        "Contract",
        "Other"
    ]

    # Correct client initialization
    client = OpenAI(api_key=api_key)

    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    


    # Image classification
    response = client.responses.create(
        model="gpt-5-mini",    # model with vision
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                    {
                        "type": "input_text",
                        "text": (
                            f"""Which of the following best matches the image?
                            1.ID: a light orange national identity card with a portrait photo and a QR code and a barcode, or light blue identity card with a portraitphoto and a signature.
                            2.Contract: a printed contract without any photo.
                            3.Other: a selfie of a person, a photo of a random object like a phone, or any other non-document image.
                            Return only the number of your choice. If unsure, return 3."""
                        )
                    },
                ]
            }
        ]
    )

    # Safely extract textual output
    model_reply = response.output_text.strip()
    if not model_reply:
        raise ValueError(f"No usable text in model response:\n{response}")

    # Extract first number from 1–3
    match = re.search(r"\b[1-4]\b", model_reply)
    if not match:
        raise ValueError(f"Unexpected output from model: {model_reply}")

    choice = int(match.group())

    return id_classes[choice - 1]

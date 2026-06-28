from openai import OpenAI
import re
import base64
import json

def gpt_classify_image(image_path, api_key, expected_values=None):

    checkItems = ["Approved", "CheckNotPassed", "Unreadable"]

    # Correct client initialization
    client = OpenAI(api_key=api_key)

    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Prepare a textual representation of expected values for the model
    metadata_text = ""
    if expected_values is not None:
        try:
            expected_json = json.dumps(expected_values, ensure_ascii=False)
        except Exception:
            expected_json = str(expected_values)
        metadata_text = f"\n\nexpected_values: {expected_json}\n\n"


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
                            f"""The image is a contract. In the table at the top of this image, there are five fields: FullName, FullAdress, Phone, StoveType, Date, StoveNumber, and ClientNumber.
                            {metadata_text}
                            Are the fields 'StoveNumber' and 'ClientNumber' respectevely filled with the same infos as you can find in the input vector named 'expected_values'?
                            In 'StoveNumber' check only the last four handwritten digits.
                            Is the 'Date' field filled with a date (any date is acceptable)?
                            At the bottom of the image there are two signature fields. 
                            Are dates and signatures or blue marks (blue marks are also accepted as signatures) present in those fields? 
                            Please answer with one of the following numbers only:
                            1. Yes, all fields are correctly filled
                            2. No, one or more fields are not correctly filled 
                            3. I can't read them
                            If you are unsure about something but it sounds reasonably correct, please answer '1'. Try to be as lenient as possible.
                            Only in case 'ClentNumber' is wrong, return the number and "Wrong".
                            """
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
    match = re.search(r"\b[1-3]\b", model_reply)
    if not match:
        raise ValueError(f"Unexpected output from model: {model_reply}")

    choice = int(match.group())

    return model_reply, choice, checkItems[choice - 1]
# response.output_text.strip()

"""
The image is a contract. In the table at the top of this image, there are five fields: FullName, FullAdress, Phone, StoveType, Date, StoveNumber, and ClientNumber.
{metadata_text}
Are the fields 'Date', 'StoveNumber' and 'ClientNumber' respectevely filled with the same infos as you can find in the input vector named 'expected_values'?
In 'StoveNumber' check only the last four handwritten digits.
In 'Date' check only that the handwritten digits correspond to day and month of the date in 'expected_values'.
At the bottom of the image there are two signature fields. 
Are dates and signatures or blue marks (blue marks are also accepted as signatures) present in those fields? 
Please answer with one of the following numbers only:
1. Yes, all fields are correctly filled
2. No, one or more fields are not correctly filled 
3. I can't read them
If you are unsure about something but it sounds reasonably correct, please answer '1'. Try to be as lenient as possible.
Only in case 'ClentNumber' is wrong, return the number and "Wrong".
"""
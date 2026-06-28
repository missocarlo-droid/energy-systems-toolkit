from openai import OpenAI
import re
import base64

def stove_classify_image(image_path, api_key):

    stove_classes = [
        "Three-stone fire cookstove",
        "Traditional charcoal stove",
        "Improved cookstove",
        "Other"
    ]

    # Correct client initialization
    client = OpenAI(api_key=api_key)

    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    


    # Image classification
    response = client.responses.create(
        model="gpt-5.1",    # model with vision
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
                            f"""Which of the following best matche the image?
                            1.three-stone fire: two or three stones on the ground. There may be a wood bonfire. It may include wood, ash, or a pot.
                            2.traditional charcoal stove: a simple metal or clay body, basic grate, rough/low-tech. It may include charcoal or ash.
                            3.improved cookstove (portable or fixed): a portable metal/clay stove with handles and/or engineered parts, OR a fixed/mud/brick built-in stove with a shaped combustion chamber. It is cleaner, more engineered or intentionally built than category 2.
                            4.other/unclear
                            Return only the number of your choice. If unsure, return 4."""
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

    return stove_classes[choice - 1]

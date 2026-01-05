import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._models.message import Message
from task._models.role import Role
from task._utils.bucket_client import DialBucketClient
from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT, DIAL_URL
from task._utils.model_client import DialModelClient


async def _put_image() -> Attachment:
    file_name = "dialx-banner.png"
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = "image/png"
    # TODO:
    client = DialBucketClient(
        api_key=API_KEY,
        base_url=DIAL_URL,
    )
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    byte_stream = BytesIO(image_bytes)
    async with client:
        upload_result = await client.put_file(
            name=file_name,
            mime_type=mime_type_png,
            content=byte_stream,
        )
    #  1. Create DialBucketClient

    #  2. Open image file
    #  3. Use BytesIO to load bytes of image
    #  4. Upload file with client
    #  5. Return Attachment object with title (file name), url and type (mime type)
    return Attachment(
        title=file_name,
        url=upload_result["url"],
        type=mime_type_png,
    )


async def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    client = DialModelClient(
        api_key=API_KEY,
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="claude-sonnet-4-5@20250929",
    )
    #  2. Upload image (use `_put_image` method )
    attachment = await _put_image()
    #  3. Print attachment to see result

    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])
    answer = client.get_completion(
        messages=[
            Message(
                role=Role.USER,
                content="What do you see on this picture?",
                custom_content=CustomContent(attachments=[attachment]),
            )
        ]
    )
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis


asyncio.run(start())

import os
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from prompts import SYSTEM_PROMPT
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai

class StoryContext(BaseModel):
    header: str
    theme: str
    background: str
    style: str
    plot: Optional[str] = None

class Character(BaseModel):
    name: str
    age: Optional[str] = None
    height: Optional[str] = None
    skin_tone: Optional[str] = None
    traits: Optional[str] = None

class Panel(BaseModel):
    description: str


def save_pdf(images):
    """
    Save a list of PIL.Image objects as a PDF and return a BytesIO buffer.
    Perfect for Streamlit download_button.
    """
    if not images:
        raise ValueError("No images provided to save as PDF.")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    for img in images:
        # Ensure image is in RGB
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Preserve aspect ratio
        aspect = img.width / img.height
        if aspect > width / height:
            draw_width = width
            draw_height = width / aspect
        else:
            draw_height = height
            draw_width = height * aspect

        # Center image
        x = (width - draw_width) / 2
        y = (height - draw_height) / 2

        # Draw image directly from memory
        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)
        c.drawImage(ImageReader(img_io), x, y, draw_width, draw_height)

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer



def generate_prompt(story_context: StoryContext, characters: List[Character], panel: Panel) -> str:
    """Aggregates inputs into a formatted prompt string."""

    # Build characters string
    characters_str = ""
    for char in characters:
        parts = [
            f"Name: {char.name}",
        ]
        if char.age:
            parts.append(f"Age: {char.age}")
        if char.height:
            parts.append(f"Height: {char.height}")
        if char.skin_tone:
            parts.append(f"Skin Tone: {char.skin_tone}")
        if char.traits:
            parts.append(f"Key traits: {char.traits}")

        characters_str += "- " + ", ".join(parts) + "\n"

    # Fill system prompt
    prompt = SYSTEM_PROMPT.format(
        story_header=story_context.header,
        theme=story_context.theme,
        background=story_context.background,
        plot=story_context.plot,
        style=story_context.style,
        characters_str=characters_str.strip(),
        panel_description=panel.description
    )

    return prompt


def generate_image(prompt: str, chat=None, image: Image.Image = None, new_session=False):
    """
    Generate or edit an image using Gemini image API.

    Args:
        prompt (str): The text instruction for generation/editing.
        chat: Existing chat object for iterative edits (default: None).
        image (PIL.Image.Image): Optional reference image for edits.
        new_session (bool): If True, starts a fresh chat session.

    Returns:
        images (list[PIL.Image.Image]): Generated images as PIL objects.
        chat: Updated chat object for reuse in further edits.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    # Start new chat if required
    if chat is None or new_session:
        chat = client.chats.create(model="gemini-2.5-flash-image-preview")

    # Build contents for message
    contents = [prompt]
    if image:
        contents.append(image)

    # Send to Gemini API
    response = chat.send_message(contents)

    # Extract images from response
    images = []
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            img_bytes = BytesIO(part.inline_data.data)
            image = Image.open(img_bytes)
            images.append(image)
    return images, chat


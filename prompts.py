SYSTEM_PROMPT = """
You are generating a multi-panel comic page. This means the image should be about 4-6 image panels.

[Story Header]: "{story_header}"

[Theme]: {theme}
[Background Setting]: {background}
[Comic Style]: {style}

[Characters]:
{characters_str}

[Panel Description]:
{panel_description}

[Plot]:
{plot}

Instructions:
- Draw in the chosen comic style.
- Ensure all recurring characters match their description across all panels.
- Keep proportions consistent between panels.
- Focus only on what happens in this specific panel.
- Maintain a comic layout look (panel framing, speech bubbles optional).

"""
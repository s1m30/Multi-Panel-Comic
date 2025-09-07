import streamlit as st
from chat import add_character
from PIL import Image
from utils import (
    StoryContext,
    Character,
    Panel,
    save_pdf,
    generate_prompt,
    generate_image,
)
import os


def main():
    st.set_page_config(page_title="Multi-Panel Comic Generator", layout="wide")
    st.title("📚 Multi-Panel Comic Generator")

    # Initialize session state
    if "comic_pages" not in st.session_state:
        st.session_state.comic_pages = []
    if "chat" not in st.session_state:
        st.session_state.chat = None  # will hold ongoing chat for edits

    # Sidebar for API key + file upload
    os.environ["GOOGLE_API_KEY"] = st.sidebar.text_input("Enter your Google API key:", type="password")
    st.sidebar.header("Upload Assets")
    uploaded_file = st.sidebar.file_uploader(
        "Upload reference image (optional)", type=["png", "jpg", "jpeg"]
    )

    # Tabs for input
    tabs = st.tabs(["Story Header", "Panel Description", "Characters", "Story Customization"])

    with tabs[0]:
        st.markdown("### 📝 Story Header\nProvide the main title or headline for your comic story.")
        story_header = st.text_input("Enter the comic header/title")

    with tabs[1]:
        st.markdown("### 🎬 Panel Description\nDescribe what should appear in this panel (characters, actions, emotions, etc.).")
        panel_description = st.text_area("Describe this panel")

    with tabs[2]:
        st.markdown("### 👥 Characters\nCustomize your characters’ appearance and traits.")
        st.subheader("Character Customization")
        if "characters" not in st.session_state:
            st.session_state.characters = []

        if st.button("➕ Add Character"):
            add_character()

        for idx, char in enumerate(st.session_state.characters):
            with st.expander(f"Character {idx+1}"):
                st.session_state.characters[idx]["name"] = st.text_input("Name", key=f"name_{idx}")
                st.session_state.characters[idx]["age"] = st.text_input("Age(optional)", key=f"age_{idx}")
                st.session_state.characters[idx]["height"] = st.text_input("Height(optional)", key=f"height_{idx}")
                st.session_state.characters[idx]["skin_tone"] = st.text_input("Skin Tone(optional)", key=f"skin_{idx}")

    with tabs[3]:
        st.markdown("### 🎨 Story Customization\nSet the theme, background, style, and plot of your comic.")
        theme = st.selectbox("Choose a theme", ["Adventure", "Sci-Fi", "Fantasy", "Slice of Life"])
        background = st.text_input("Background setting")
        style = st.selectbox("Comic drawing style", ["Manga", "Western", "Cartoon", "Minimalist"])
        plot = st.text_area("Story Plot (optional)", max_chars=500, help="Give more context about the overall story. Up to 500 characters.")
        
        
    with st.container(border=True):
        # --- Generate a new page ---
        st.subheader("⚡ Generate & Manage Comics")
        if st.button("🎨 Generate Comic Page"):
            story = StoryContext(
                header=story_header,
                theme=theme,
                background=background,
                style=style,
                plot=plot,
            )
            characters = [Character(**character) for character in st.session_state.characters]
            panel = Panel(description=panel_description)

            # Aggregate prompt
            prompt = generate_prompt(story, characters, panel)

            # Generate a new page (reset chat with new_session=True)
            images, st.session_state.chat = generate_image(prompt, new_session=True)

            if images:
                st.session_state.comic_pages.append(images[0])
                st.image(images[0], caption="Generated Comic Page")

        # --- Edit last page ---
        if st.session_state.comic_pages:
            # Show all pages
            st.subheader("📖 Your Generated Comic Pages")
            for idx, img in enumerate(st.session_state.comic_pages):
                st.image(img, caption=f"Comic Page {idx+1}", width=405)
                
            edit_instruction = st.text_input("✏️ Edit last page (optional)")
            if st.button("Apply Edit"):
                if edit_instruction.strip():
                    images, st.session_state.chat = generate_image(
                        edit_instruction, chat=st.session_state.chat
                    )
                    if images:
                        st.session_state.comic_pages[-1] = images[0]  # replace last page
                        st.success("✅ Last page updated with your edit!")

            # Download + next page options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬇️ Download PDF"):
                    pdf_buffer = save_pdf(st.session_state.comic_pages)
                    st.download_button(
                        "Download Comic PDF", pdf_buffer, file_name="comic.pdf", mime="application/pdf"
                    )

            with col2:
                if st.button("➕ Generate Next Page"):
                    st.success("You can now describe and generate the next page!")


if __name__ == "__main__":
    main()

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="BhashaMeme",
    page_icon="😂",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Asset Loading ---
ASSETS_DIR = "assets"

# For deploying on Hugging Face Spaces, a standard Linux font path is needed.
# We'll also provide a fallback for local development on Windows/macOS.
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not os.path.exists(FONT_PATH):
    # Fallback for local testing (Windows/Mac)
    st.warning(
        f"Could not find font at {FONT_PATH}. Trying a common system font 'Arial'. This may not work on all systems.")
    FONT_PATH = "arial.ttf"


# FIX: Changed to the older, more compatible st.cache decorator
@st.cache
def get_meme_templates():
    """Scans the assets directory for meme templates."""
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        return {}

    templates = {}
    for f_name in os.listdir(ASSETS_DIR):
        if f_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Format the name for the dropdown
            display_name = os.path.splitext(f_name)[0].replace("_", " ").replace("-", " ").title()
            templates[display_name] = os.path.join(ASSETS_DIR, f_name)
    return templates


def generate_meme(template_path, top_text, bottom_text, font_size=50):
    """Generates a meme by adding text to a template image."""
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        W, H = img.size

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except IOError:
            st.error(f"Font file not found at {FONT_PATH}. Please ensure it's available. Using default font.")
            font = ImageFont.load_default()

        def draw_text_with_outline(text, position, font, draw_obj):
            x, y = position
            # Draw outline
            draw_obj.text((x - 2, y - 2), text, font=font, fill='black')
            draw_obj.text((x + 2, y - 2), text, font=font, fill='black')
            draw_obj.text((x - 2, y + 2), text, font=font, fill='black')
            draw_obj.text((x + 2, y + 2), text, font=font, fill='black')
            # Draw text
            draw_obj.text((x, y), text, font=font, fill='white')

        if top_text:
            _, _, w, h = draw.textbbox((0, 0), top_text, font=font)
            x = (W - w) / 2
            y = 10
            draw_text_with_outline(top_text, (x, y), font, draw)

        if bottom_text:
            _, _, w, h = draw.textbbox((0, 0), bottom_text, font=font)
            x = (W - w) / 2
            y = H - h - 15
            draw_text_with_outline(bottom_text, (x, y), font, draw)

        # Convert image to bytes for download button
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return img, buffer

    except Exception as e:
        st.error(f"An error occurred during meme generation: {e}")
        return None, None


# --- UI Layout ---
st.title("😂 BhashaMeme: The Desi Meme Creator")
st.markdown("Create memes in your own language! Select a template, add your text, and download.")

meme_templates = get_meme_templates()

if not meme_templates:
    st.error("No meme templates found! Please add some images to the 'assets' folder.")
    st.info(
        "Create a folder named `assets` in your project directory and place your `.jpg` or `.png` meme templates inside it.")
else:
    selected_template_name = st.selectbox("1. Choose a Meme Template:", options=list(meme_templates.keys()))
    template_path = meme_templates[selected_template_name]

    st.image(template_path, caption="Selected Template", use_column_width=True)

    st.header("2. Add Your Text")
    top_text = st.text_input("Top Text (optional):")
    bottom_text = st.text_input("Bottom Text:", placeholder="Enter your funny caption here!")

    # FIX: Removed the 'use_container_width' argument which is not compatible with older Streamlit versions
    if st.button("🚀 Generate Meme"):
        if not bottom_text and not top_text:
            st.warning("Please add some text to generate a meme.")
        else:
            with st.spinner("Creating your masterpiece..."):
                final_meme, image_bytes = generate_meme(template_path, top_text, bottom_text)
                if final_meme:
                    st.success("Here is your meme!")
                    st.image(final_meme, use_column_width=True)

                    # FIX: Removed the 'use_container_width' argument
                    st.download_button(
                        label="📥 Download Meme",
                        data=image_bytes,
                        file_name="bhasha_meme.png",
                        mime="image/png"
                    )
                    # In a real app, you would add the logic to save the corpus data here
                    # e.g., save_to_corpus(selected_template_name, top_text, bottom_text)

st.markdown("---")
st.markdown("Made with ❤️ for the **viswam.ai** project.")


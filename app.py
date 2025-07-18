import streamlit as st
from PIL import Image, ImageDraw
import io, zipfile, base64, hashlib

def crop_image_into_zones(image, h_lines, v_lines, prefix="crop", suffix="", fmt="PNG"):
    width, height = image.size
    h_positions = sorted([0] + h_lines + [height])
    v_positions = sorted([0] + v_lines + [width])
    images = []
    for i in range(len(h_positions)-1):
        for j in range(len(v_positions)-1):
            box = (v_positions[j], h_positions[i], v_positions[j+1], h_positions[i+1])
            cropped = image.crop(box)
            name = f"{prefix}-{i+1}-{j+1}-{hashlib.md5(str(box).encode()).hexdigest()[:8]}{suffix}.{fmt.lower()}"
            images.append((name, cropped))
    return images

def generate_zip(images, fmt):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, img in images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=fmt)
            zip_file.writestr(filename, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def draw_image_with_lines(img, h_lines, v_lines):
    preview = img.copy()
    draw = ImageDraw.Draw(preview)
    for y in h_lines:
        draw.line([(0, y), (img.width, y)], fill="red", width=2)
    for x in v_lines:
        draw.line([(x, 0), (x, img.height)], fill="blue", width=2)
    return preview

def run_image_cropper_app():
    st.title("🖼️ Image Cropper with Horizontal/Vertical Guide Lines")

    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if not uploaded_file:
        return

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    st.markdown("### ✂️ Define Guide Lines")
    col1, col2 = st.columns(2)
    with col1:
        h_raw = st.text_input("Horizontal lines (px, comma separated)", value="100,300")
        h_lines = sorted({int(x) for x in h_raw.split(",") if x.strip().isdigit() and 0 < int(x.strip()) < image.height})
    with col2:
        v_raw = st.text_input("Vertical lines (px, comma separated)", value="200,400")
        v_lines = sorted({int(x) for x in v_raw.split(",") if x.strip().isdigit() and 0 < int(x.strip()) < image.width})

    preview_image = draw_image_with_lines(image, h_lines, v_lines)
    st.image(preview_image, caption="Crop Preview", use_column_width=True)

    st.markdown("### ⚙️ Export Options")
    fmt = st.selectbox("Image format", ["PNG", "JPEG"])
    prefix = st.text_input("Filename prefix", "crop")
    suffix = st.text_input("Filename suffix", "")
    export_zip = st.checkbox("Export as ZIP archive", value=True)

    if st.button("🚀 Crop and Download"):
        cropped_images = crop_image_into_zones(image, h_lines, v_lines, prefix, suffix, fmt)
        if export_zip:
            zip_data = generate_zip(cropped_images, fmt)
            st.download_button("📦 Download ZIP", data=zip_data, file_name="cropped_images.zip", mime="application/zip")
        else:
            for name, img in cropped_images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=fmt)
                st.download_button(f"⬇️ {name}", data=img_bytes.getvalue(), file_name=name, mime=f"image/{fmt.lower()}")

run_image_cropper_app()

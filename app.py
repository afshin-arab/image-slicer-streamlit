import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import base64, io

st.set_page_config(layout="wide")
st.title("🖼️ Streamlit Drag-and-Drop Image Cropper")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if not uploaded_file:
    st.stop()

image = Image.open(uploaded_file).convert("RGB")
buf = io.BytesIO()
image.save(buf, format="PNG")
img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
img_uri = f"data:image/png;base64,{img_b64}"

canvas_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  canvas {{ border: 1px solid #ccc; }}
</style>
</head>
<body>
<canvas id="canvas" width="{image.width}" height="{image.height}"></canvas>
<div><button onclick="exportLines()">📤 Export Crop Lines</button></div>
<script>
let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let img = new Image(); img.src = "{img_uri}";
let lines = [], dragging = null;
let h = [100, 300], v = [200, 400];

img.onload = () => draw();
canvas.onmousedown = e => dragging = detectLine(e);
canvas.onmouseup = () => dragging = null;
canvas.onmousemove = e => {{
  if (!dragging) return;
  let r = canvas.getBoundingClientRect();
  let x = e.clientX - r.left, y = e.clientY - r.top;
  if (dragging.d === 'h') dragging.p = Math.max(0, Math.min(canvas.height, y));
  else dragging.p = Math.max(0, Math.min(canvas.width, x));
  updateArrays(); draw();
}};
function draw() {{
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  lines = [];
  h.forEach(y => {{ lines.push({{d:'h',p:y}}); ctx.strokeStyle='red'; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }});
  v.forEach(x => {{ lines.push({{d:'v',p:x}}); ctx.strokeStyle='blue'; ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }});
}}
function detectLine(e) {{
  let r = canvas.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
  return lines.find(l => (l.d==='h' && Math.abs(l.p - y)<5) || (l.d==='v' && Math.abs(l.p - x)<5));
}}
function updateArrays() {{
  h = lines.filter(l => l.d === 'h').map(l => l.p);
  v = lines.filter(l => l.d === 'v').map(l => l.p);
}}
function exportLines() {{
  window.parent.postMessage({{ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: {{ horizontal: h.map(Math.round), vertical: v.map(Math.round) }} }}, "*");
}}
</script>
</body>
</html>
"""

canvas_height = min(3000, int(image.height) + 100)
result = components.html(canvas_html, height=canvas_height, scrolling=False)

if isinstance(result, dict) and "horizontal" in result:
    st.success("✅ Received crop line positions.")
    h_lines = sorted(set(result["horizontal"]))
    v_lines = sorted(set(result["vertical"]))
    st.write("Horizontal:", h_lines)
    st.write("Vertical:", v_lines)

    if st.button("✂️ Crop Image Now"):
        h_pos = sorted([0] + h_lines + [image.height])
        v_pos = sorted([0] + v_lines + [image.width])
        count = 0
        for i in range(len(h_pos)-1):
            for j in range(len(v_pos)-1):
                box = (v_pos[j], h_pos[i], v_pos[j+1], h_pos[i+1])
                cropped = image.crop(box)
                st.image(cropped, caption=f"Crop {i+1}-{j+1}", use_column_width=True)
                count += 1
        st.success(f"✨ Done! Cropped {count} images.")
else:
    st.info("🎯 Use the canvas to drag lines and export coordinates.")

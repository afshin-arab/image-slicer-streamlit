import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="wide")
st.title("🖼️ Drag-and-Drop Image Crop Lines")

st.markdown("""
This demo shows how to use a **custom HTML+JS component** inside Streamlit for dragging crop lines.
""")

custom_cropper_code = """
<!DOCTYPE html>
<html>
<head>
<style>
  canvas { border: 1px solid #ccc; }
  #controls { margin-top: 10px; }
</style>
</head>
<body>
<canvas id="canvas" width="800" height="600"></canvas>
<div id="controls">
  <button onclick="exportLines()">Export Line Positions</button>
</div>
<script>
let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let img = new Image();
img.src = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Example.jpg/800px-Example.jpg';  // Replace with uploaded image
let lines = [];
let draggingLine = null;
const TOLERANCE = 5;

// Initial line positions
let h_lines = [100, 300];
let v_lines = [200, 400];

img.onload = function () {
  draw();
};

canvas.addEventListener('mousedown', function(e) {
  let {x, y} = getMousePos(e);
  draggingLine = findLine(x, y);
});

canvas.addEventListener('mouseup', function(e) {
  draggingLine = null;
});

canvas.addEventListener('mousemove', function(e) {
  if (draggingLine) {
    let {x, y} = getMousePos(e);
    if (draggingLine.dir === 'h') {
      draggingLine.pos = Math.max(0, Math.min(canvas.height, y));
    } else {
      draggingLine.pos = Math.max(0, Math.min(canvas.width, x));
    }
    updateArrays();
    draw();
  }
});

function getMousePos(evt) {
  let rect = canvas.getBoundingClientRect();
  return {x: evt.clientX - rect.left, y: evt.clientY - rect.top};
}

function findLine(x, y) {
  for (let i = 0; i < lines.length; i++) {
    let l = lines[i];
    if (l.dir === 'h' && Math.abs(l.pos - y) < TOLERANCE) return l;
    if (l.dir === 'v' && Math.abs(l.pos - x) < TOLERANCE) return l;
  }
  return null;
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  lines = [];
  h_lines.forEach(y => {
    lines.push({dir: 'h', pos: y});
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.stroke();
  });
  v_lines.forEach(x => {
    lines.push({dir: 'v', pos: x});
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 2;
    ctx.stroke();
  });
}

function updateArrays() {
  h_lines = lines.filter(l => l.dir === 'h').map(l => l.pos);
  v_lines = lines.filter(l => l.dir === 'v').map(l => l.pos);
}

function exportLines() {
  const data = {
    horizontal: h_lines,
    vertical: v_lines
  };
  window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: data }, "*");
}
</script>
</body>
</html>
"""

# Embed in Streamlit
st.markdown("### 🔧 Canvas with Drag-and-Drop Lines")
response = html(custom_cropper_code, height=670, scrolling=False)

st.info("This is a static demo. To connect it fully, we’ll use `components.declare_component` and fetch coordinates.")

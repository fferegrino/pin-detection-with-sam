window.addEventListener('load', function() {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const img = document.getElementById('image');
  const boxes = [];  // Array to hold all boxes

  // img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

  let start = { x: 0, y: 0 };
  let isDrawing = false;

  canvas.addEventListener('mousedown', function(e) {
    start = { x: e.offsetX, y: e.offsetY };
    isDrawing = true;
  });

  canvas.addEventListener('mousemove', function(e) {
    if (isDrawing) {
      const currentX = e.offsetX;
      const currentY = e.offsetY;
      redrawCanvas();
      drawBox(start.x, start.y, currentX - start.x, currentY - start.y);
    }
  });

  canvas.addEventListener('mouseup', function(e) {
    if (isDrawing) {
      const endX = e.offsetX;
      const endY = e.offsetY;
      const box = { x: start.x, y: start.y, width: endX - start.x, height: endY - start.y };
      boxes.push(box);
      sendBoxData(box);
      redrawCanvas();
      isDrawing = false;
    }
  });

  function sendBoxData(box) {
    fetch('/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(box)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      document.getElementById('result')['src'] = data['data'];
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  }


  function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    boxes.forEach(box => {
      drawBox(box.x, box.y, box.width, box.height);
    });
  }

  function drawBox(x, y, width, height) {
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.strokeStyle = 'red';
    ctx.stroke();
  }
});

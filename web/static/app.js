window.addEventListener('load', function() {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const img = document.getElementById('image');
  const results = document.getElementById('results');
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

      x1 = Math.min(start.x, endX);
      y1 = Math.min(start.y, endY);
      x2 = Math.max(start.x, endX);
      y2 = Math.max(start.y, endY);

      const box = { x1, y1, x2, y2 };
      console.log(box);
      boxes.push(box);
      sendBoxData(box);
      redrawCanvas();
      isDrawing = false;
    }
  });

  function sendBoxData(box) {
    fetch('/cut', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(box)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data.results);
      // Clear the results div and add the new data
      results.innerHTML = '';

      for (let i = 0; i < data.results.length; i++) {
        
        const result = data.results[i];
        const t = createForm(result);
        results.appendChild(t);
      }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  }

  function createForm(result) {
    const card = document.createElement('div');
    card.classList.add('card');

    const form = document.createElement('form');
    form.action = '/select_cutout';
    form.method = 'POST';

    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'id';
    hiddenInput.value = result.id;

    const submitButton = document.createElement('button');
    submitButton.textContent = 'Select';
    submitButton.type = 'submit';

    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.name = 'name';
    nameInput.placeholder = 'Name';

    form.appendChild(nameInput);
    form.appendChild(hiddenInput);
    form.appendChild(submitButton);

    const image = document.createElement('img');
    image.src = result.image;

    const div = document.createElement('div');
    div.classList.add('image-container');

    div.appendChild(image);
    card.appendChild(div);

    card.appendChild(form);
    return card;
  }


  function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    boxes.forEach(box => {
      drawBox(box.x, box.y, box.width, box.height);
    });
  }

  function drawBox(x, y, width, height, fill = false) {
    ctx.beginPath();
    ctx.rect(x, y, width, height);
    ctx.strokeStyle = 'red';
    if (fill) {
      ctx.fillStyle = '#ff000033';
      ctx.fill();
    }
    ctx.stroke();
  }

  function drawPolygon(points) {
    ctx.beginPath();
    ctx.moveTo(points[0][0] * ratio, points[0][1] * ratio);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i][0] * ratio, points[i][1] * ratio);
    }
    ctx.fillStyle = '#ff0000FF';
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }


  for (let i = 0; i < existingCutouts.length; i++) {
    const cutout = existingCutouts[i];
    console.log(cutout);
    for (let i = 0; i < cutout.polygons.length; i++) {
      const points = cutout.polygons[i];
      drawPolygon(points);
    }
  }
});

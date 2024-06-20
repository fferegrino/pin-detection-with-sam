window.addEventListener('load', function() {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const img = document.getElementById('image');
  const results = document.getElementById('results');
  const contours = [];

  canvas.width = img.width;
  canvas.height = img.height;
  ctx.drawImage(img, 0, 0);

  let startingMousePosition = {
      x: 0,
      y: 0
  };
  let isDrawing = false;

  canvas.addEventListener('mousedown', function(e) {
      startingMousePosition = {
          x: e.offsetX,
          y: e.offsetY
      };
      isDrawing = true;
  });

  canvas.addEventListener('mousemove', function(e) {
      if (isDrawing) {
          const currentX = e.offsetX;
          const currentY = e.offsetY;
          redrawCanvas();
          drawBox(startingMousePosition.x, startingMousePosition.y, currentX - startingMousePosition.x, currentY - startingMousePosition.y);
      }
  });

  canvas.addEventListener('mouseup', function(e) {
      if (isDrawing) {
          const endX = e.offsetX;
          const endY = e.offsetY;

          x1 = Math.min(startingMousePosition.x, endX);
          y1 = Math.min(startingMousePosition.y, endY);
          x2 = Math.max(startingMousePosition.x, endX);
          y2 = Math.max(startingMousePosition.y, endY);

          const box = {
              x1,
              y1,
              x2,
              y2
          };
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

  const template = `
<div class="form-container">
    <div class="image-container">
        <img src="{{image}}">
    </div>
    <form action="/select_cutout" method="POST">
        <input type="text" name="name" placeholder="Name">
        <input type="hidden" name="id" value="{{id}}">
        <button type="submit">Select</button>
    </form>
</div>
`;

  function createForm(result) {

      const rendered = Mustache.render(template, {
          id: result.id,
          image: result.image
      });

      const div = document.createElement('div');
      div.innerHTML = rendered.trim();

      return div.firstChild;
  }

  function redrawCanvas() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      contours.forEach(points => {
          drawPolygon(points);
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
      ctx.moveTo(points[0] * ratio, points[1] * ratio);
      for (let i = 2; i < points.length; i += 2) {
        ctx.lineTo(points[i] * ratio, points[i + 1] * ratio);
      }
      ctx.fillStyle = '#ff0000FF';
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
  }

  for (let i = 0; i < existingCutouts.length; i++) {
      const cutout = existingCutouts[i];
      drawPolygon(cutout.polygon);
      contours.push(cutout.polygon);
  }
});
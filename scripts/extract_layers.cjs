const Jimp = require('jimp');
const path = require('path');

const basePath = path.join(__dirname, '../frontend/public/assets/vehicles/tank');
const srcImage = path.join(basePath, 'exploded.png');

async function processImage() {
  console.log('Loading source image...', srcImage);
  const image = await Jimp.read(srcImage);
  
  const width = image.bitmap.width;
  const height = image.bitmap.height;
  
  console.log(`Image dimensions: ${width}x${height}`);

  // First, convert background pixels to transparent
  // We assume the background is very dark (e.g. r < 30, g < 30, b < 30)
  image.scan(0, 0, width, height, function(x, y, idx) {
    const r = this.bitmap.data[idx + 0];
    const g = this.bitmap.data[idx + 1];
    const b = this.bitmap.data[idx + 2];
    
    // Background removal heuristic (dark pixels -> transparent)
    if (r < 25 && g < 30 && b < 40) {
      this.bitmap.data[idx + 3] = 0; // Set alpha to 0
    }
  });

  console.log('Background removed. Generating layers...');

  const layers = [
    { name: 'layer_turret.png', check: (x, y, w, h) => y < h * 0.40 },
    { name: 'layer_cannon.png', check: (x, y, w, h) => y >= h * 0.40 && y < h * 0.70 && x < w * 0.35 },
    { name: 'layer_treads.png', check: (x, y, w, h) => y >= h * 0.70 },
    { name: 'layer_chassis.png', check: (x, y, w, h) => y >= h * 0.40 && y < h * 0.70 && x >= w * 0.35 },
  ];

  for (const layer of layers) {
    const clone = image.clone();
    
    // Clear pixels outside the layer bounds
    clone.scan(0, 0, width, height, function(x, y, idx) {
      if (!layer.check(x, y, width, height)) {
        this.bitmap.data[idx + 3] = 0; // Transparent
      }
    });

    const outputPath = path.join(basePath, layer.name);
    await clone.writeAsync(outputPath);
    console.log(`Saved ${layer.name}`);
  }
  
  console.log('All layers extracted successfully.');
}

processImage().catch(console.error);

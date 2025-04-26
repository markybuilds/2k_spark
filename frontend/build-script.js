const fs = require('fs');
const path = require('path');

// Ensure the node_modules/.next/server directory exists
const serverDir = path.join(__dirname, 'node_modules', '.next', 'server');
if (!fs.existsSync(serverDir)) {
  fs.mkdirSync(serverDir, { recursive: true });
}

// Copy the lib directory to the node_modules directory
const libDir = path.join(__dirname, 'src', 'lib');
const nodeModulesLibDir = path.join(__dirname, 'node_modules', '@', 'lib');

if (!fs.existsSync(nodeModulesLibDir)) {
  fs.mkdirSync(nodeModulesLibDir, { recursive: true });
}

// Copy all files from lib to node_modules/@/lib
function copyDir(src, dest) {
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      if (!fs.existsSync(destPath)) {
        fs.mkdirSync(destPath, { recursive: true });
      }
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
      console.log(`Copied ${srcPath} to ${destPath}`);
    }
  }
}

try {
  copyDir(libDir, nodeModulesLibDir);
  console.log('Successfully copied lib directory to node_modules/@/lib');
} catch (error) {
  console.error('Error copying lib directory:', error);
}

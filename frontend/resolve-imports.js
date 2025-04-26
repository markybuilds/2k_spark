const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Find all TypeScript and TypeScript JSX files
const files = glob.sync('src/**/*.{ts,tsx}', { cwd: __dirname });

// Process each file
files.forEach(file => {
  const filePath = path.join(__dirname, file);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Replace @/lib imports with relative imports
  content = content.replace(
    /import\s+(.+?)\s+from\s+["']@\/lib\/utils["']/g, 
    'import $1 from "../../../lib/utils"'
  );
  
  content = content.replace(
    /import\s+(.+?)\s+from\s+["']@\/lib\/api\/client["']/g, 
    'import $1 from "../../../lib/api/client"'
  );
  
  // Write the modified content back to the file
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`Processed imports in ${file}`);
});

console.log('Import resolution completed successfully');

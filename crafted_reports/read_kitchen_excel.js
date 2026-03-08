const XLSX = require('xlsx');
const fs = require('fs');

const filePath = '/root/.openclaw/media/inbound/file_1---2868eeac-ecc0-4281-9159-dd65bd0c6ab4.xlsx';

// Read the workbook
const workbook = XLSX.readFile(filePath);

console.log('Sheets found:', workbook.SheetNames);
console.log();

// Process each sheet
workbook.SheetNames.forEach(sheetName => {
    console.log(`=== ${sheetName} ===`);
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    // Print all rows
    data.forEach((row, index) => {
        console.log(`Row ${index + 1}:`, row.join(' | '));
    });
    console.log();
});

// Also save structured data to a JSON file for Python to use
const allData = {};
workbook.SheetNames.forEach(sheetName => {
    const worksheet = workbook.Sheets[sheetName];
    allData[sheetName] = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
});

fs.writeFileSync('/tmp/kitchen_recipes.json', JSON.stringify(allData, null, 2));
console.log('Data saved to /tmp/kitchen_recipes.json');

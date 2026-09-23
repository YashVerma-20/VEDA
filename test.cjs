const fs = require('fs');
const text = fs.readFileSync('test_datasets/logistic_officer/lo_LOV_001_healthy.csv', 'utf8');
const lines = text.trim().split('\n');
const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
const records = lines.slice(1, 2).map(line => {
    const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
    const record = {};
    headers.forEach((h, i) => {
    const num = parseFloat(values[i]);
    record[h] = isNaN(num) ? values[i] : num;
    });
    return record;
});
console.log(records[0]);

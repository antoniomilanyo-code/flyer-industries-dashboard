// deploy-dashboard.js
// Run this to deploy the dashboard Edge Function

const fs = require('fs');
const https = require('https');

const PROJECT_REF = 'kidbbtdnhtncxtaqqgcp';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtpZGJidGRuaHRuY3h0YXFxZ2NwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjkyOTE4MywiZXhwIjoyMDg4NTA1MTgzfQ.HK2a_lvd6m0gSbE2pRkfVEzD0TAkYzpbujaxHs3SHK4';

const functionCode = fs.readFileSync('./supabase/functions/dashboard/index.ts', 'utf8');

const data = JSON.stringify({
  slug: 'dashboard',
  name: 'Flyer Industries Dashboard',
  source: Buffer.from(functionCode).toString('base64'),
  verify_jwt: false
});

const options = {
  hostname: 'api.supabase.com',
  port: 443,
  path: `/v1/projects/${PROJECT_REF}/functions`,
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${SERVICE_KEY}`,
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

console.log('Deploying Edge Function...');

const req = https.request(options, (res) => {
  let responseData = '';
  
  res.on('data', (chunk) => {
    responseData += chunk;
  });
  
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    console.log('Response:', responseData);
    
    if (res.statusCode === 201 || res.statusCode === 200) {
      console.log('\n✅ Deployment successful!');
      console.log('\n🌐 Your dashboard is at:');
      console.log(`https://${PROJECT_REF}.supabase.co/functions/v1/dashboard`);
    } else {
      console.log('\n❌ Deployment failed. Trying alternative method...');
    }
  });
});

req.on('error', (e) => {
  console.error('Error:', e.message);
});

req.write(data);
req.end();

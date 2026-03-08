// test-navigation.js
// Run this in browser console to test if navigation works

console.log('Testing navigation...');

// Check if elements exist
const views = document.querySelectorAll('.view');
const navBtns = document.querySelectorAll('.nav-btn');

console.log('Views found:', views.length);
console.log('Nav buttons found:', navBtns.length);

// Test navigation function
function testNavigate(viewName) {
  console.log('Testing navigate to:', viewName);
  
  // Hide all views
  document.querySelectorAll('.view').forEach(function(v) {
    v.classList.remove('active');
  });
  
  // Show target
  const target = document.getElementById('view-' + viewName);
  if (target) {
    target.classList.add('active');
    console.log('✓ Navigation to', viewName, 'successful');
    return true;
  } else {
    console.error('✗ View not found:', 'view-' + viewName);
    return false;
  }
}

// Run tests
console.log('\\nTesting navigation:');
testNavigate('crafted');
console.log('Current active view:', document.querySelector('.view.active')?.id);

console.log('\\nTo fix:');
console.log('1. If views exist but navigation fails, check console for JS errors');
console.log('2. Try adding event listeners manually');
console.log('3. Consider hosting on Supabase instead of GitHub Pages');

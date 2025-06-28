/**
 * Test script to verify clipboard page functionality
 * Run this in the browser console to test the clipboard page
 */

console.log('🧪 Testing ClipVault Clipboard Page...');

// Test 1: Check if frontend can reach backend
async function testBackendConnection() {
  try {
    const response = await fetch('http://localhost:8001/health');
    const data = await response.json();
    console.log('✅ Backend health check:', data);
    return true;
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    return false;
  }
}

// Test 2: Test clipboard API endpoint
async function testClipboardAPI() {
  try {
    const response = await fetch('http://localhost:8001/api/clipboard/');
    const data = await response.json();
    console.log('✅ Clipboard API response:', data);
    return data;
  } catch (error) {
    console.error('❌ Clipboard API failed:', error);
    return null;
  }
}

// Test 3: Test frontend clipboard hook
async function testFrontendClipboard() {
  try {
    // Check if useClipboard hook data is available
    const clipboardData = window.localStorage.getItem('clipvault_clipboard');
    console.log('📋 Frontend clipboard data:', clipboardData);
    return true;
  } catch (error) {
    console.error('❌ Frontend clipboard test failed:', error);
    return false;
  }
}

// Run all tests
async function runTests() {
  console.log('🚀 Starting clipboard page tests...');
  
  const backendOk = await testBackendConnection();
  const clipboardData = await testClipboardAPI();
  const frontendOk = await testFrontendClipboard();
  
  console.log('📊 Test Results:');
  console.log(`Backend: ${backendOk ? '✅' : '❌'}`);
  console.log(`Clipboard API: ${clipboardData ? '✅' : '❌'}`);
  console.log(`Frontend: ${frontendOk ? '✅' : '❌'}`);
  
  if (backendOk && clipboardData && frontendOk) {
    console.log('🎉 All tests passed! Clipboard page should work.');
  } else {
    console.log('⚠️ Some tests failed. Check the logs above.');
  }
}

// Auto-run tests
runTests();

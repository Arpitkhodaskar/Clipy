// Clear localStorage for ClipVault
console.log('🧹 Clearing ClipVault localStorage...');
localStorage.removeItem('access_token');
localStorage.removeItem('clipvault_user');
localStorage.removeItem('clipvault_domain_whitelist');
console.log('✅ localStorage cleared. Please refresh the page.');

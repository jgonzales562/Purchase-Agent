// Background service worker for Quick Add to Cart
// Handles storage for quantity preferences

// Store product quantity preferences per URL
let productSettings = {};

// Load from storage on startup
chrome.storage.local.get(['productSettings'], (result) => {
  if (result.productSettings) {
    productSettings = result.productSettings;
  }
});

// Listen for messages
chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.action === 'saveQuantity') {
    // Save quantity preference for a product URL
    const { url, quantity } = request;
    productSettings[url] = { quantity };
    chrome.storage.local.set({ productSettings });
    sendResponse({ success: true });
  } else if (request.action === 'getQuantity') {
    // Get saved quantity for a product URL
    const settings = productSettings[request.url] || { quantity: 1 };
    sendResponse(settings);
  }

  return true;
});

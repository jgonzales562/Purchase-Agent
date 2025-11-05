// Popup script - simple add-to-cart interface

document.addEventListener('DOMContentLoaded', () => {
  loadProductInfo();
});

function loadProductInfo() {
  // Get current tab to extract product info
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs || tabs.length === 0) {
      showError('No active tab found');
      return;
    }

    const currentTab = tabs[0];
    const url = currentTab.url;

    // Check if we're on a supported site
    const supportedSites = [
      'gamestop.com',
      'bestbuy.com',
      'target.com',
      'walmart.com',
      'pokemoncenter.com',
    ];
    const onSupportedSite = supportedSites.some((site) => url.includes(site));

    if (!onSupportedSite) {
      showError('This site is not supported yet');
      return;
    }

    // Load saved quantity for this URL
    chrome.runtime.sendMessage({ action: 'getQuantity', url }, (response) => {
      const savedQty = response?.quantity || 1;
      displayAddToCartUI(url, currentTab.title, savedQty);
    });
  });
}

function displayAddToCartUI(url, title, quantity) {
  const content = document.getElementById('content');

  content.innerHTML = `
    <div class="product-ui">
      <div class="product-title">
        <strong>${escapeHtml(title)}</strong>
      </div>
      
      <div class="quantity-control">
        <label class="quantity-label">
          Quantity:
          <input type="number" id="quantity" min="1" max="10" value="${quantity}" class="quantity-input" />
        </label>
      </div>
      
      <button id="addToCartBtn" class="add-cart-btn">
        🛒 Add to Cart
      </button>
    </div>
  `;

  // Attach event listeners
  const qtyInput = document.getElementById('quantity');
  qtyInput.addEventListener('change', (e) => {
    const qty = Math.max(1, Math.min(10, parseInt(e.target.value) || 1));
    qtyInput.value = qty;
    chrome.runtime.sendMessage({ action: 'saveQuantity', url, quantity: qty });
  });

  const addBtn = document.getElementById('addToCartBtn');
  addBtn.addEventListener('click', () => {
    const qty = parseInt(qtyInput.value) || 1;
    triggerAddToCart(qty, addBtn);
  });
}

function triggerAddToCart(quantity, button) {
  const RESET_DELAY_SUCCESS = 2500;
  const RESET_DELAY_ERROR = 2000;
  const originalText = button.textContent;
  const resetButton = (text, delay = RESET_DELAY_SUCCESS) => {
    button.textContent = text;
    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, delay);
  };

  button.textContent = '⏳ Adding...';
  button.disabled = true;

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs || tabs.length === 0) {
      resetButton('❌ Error', RESET_DELAY_ERROR);
      return;
    }

    chrome.tabs.sendMessage(
      tabs[0].id,
      { action: 'performAddToCart', quantity },
      (response) => {
        if (chrome.runtime.lastError) {
          resetButton('❌ Failed');
        } else if (response?.success) {
          resetButton('✅ Added!');
        } else {
          resetButton('❌ ' + (response?.error || 'Failed'));
        }
      }
    );
  });
}

function showError(message) {
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="empty-state">
      <p>${escapeHtml(message)}</p>
    </div>
  `;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

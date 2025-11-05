// Content script - handles add-to-cart functionality
(function () {
  'use strict';

  // Listen for add-to-cart requests
  chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
    if (request.action === 'performAddToCart') {
      const qty = Math.max(1, parseInt(request.quantity || 1, 10));
      performAddToCart(qty)
        .then((result) => {
          sendResponse(result);
        })
        .catch((err) => {
          sendResponse({ success: false, error: err?.message });
        });
      return true;
    }
  });

  // Perform add-to-cart with site-specific logic
  async function performAddToCart(quantity) {
    const hostname = location.hostname;

    if (hostname.includes('gamestop.com')) {
      return addToCartGameStop(quantity);
    }
    if (hostname.includes('bestbuy.com')) {
      return addToCartBestBuy(quantity);
    }
    if (hostname.includes('target.com')) {
      return addToCartTarget(quantity);
    }
    if (hostname.includes('walmart.com')) {
      return addToCartWalmart(quantity);
    }
    if (hostname.includes('pokemoncenter.com')) {
      return addToCartPokemonCenter(quantity);
    }

    return {
      success: false,
      error: 'Site not supported',
    };
  }

  // Constants
  const CLICK_DELAY_GAMESTOP = 400;
  const CLICK_DELAY_DEFAULT = 500;
  const ERROR_BUTTON_NOT_FOUND = 'Add to Cart button not found or disabled';

  // Utility: sleep
  function sleep(ms) {
    return new Promise((res) => setTimeout(res, ms));
  }

  // Helper: Standard error response
  function errorResponse(message) {
    return { success: false, error: message };
  }

  // Helper: Try-catch wrapper for add-to-cart functions
  async function tryAddToCart(fn) {
    try {
      return await fn();
    } catch (e) {
      return errorResponse(e?.message || 'Unknown error');
    }
  }

  // GameStop: set quantity and click add-to-cart
  async function addToCartGameStop(quantity) {
    return tryAddToCart(async () => {
      const qtyInput = document.querySelector(
        'input[name*="qty"], input[id*="qty"], input[name*="quantity"], input[type="number"]'
      );
      const qtySelect = document.querySelector(
        'select[name*="qty"], select[name*="quantity"]'
      );

      if (qtyInput) {
        qtyInput.value = String(quantity);
        qtyInput.dispatchEvent(new Event('input', { bubbles: true }));
        qtyInput.dispatchEvent(new Event('change', { bubbles: true }));
      } else if (qtySelect) {
        qtySelect.value = String(quantity);
        qtySelect.dispatchEvent(new Event('change', { bubbles: true }));
      }

      const candidates = Array.from(
        document.querySelectorAll('button, [role="button"], a.button')
      );
      const addBtn = candidates.find(
        (el) =>
          (el.innerText || '').toLowerCase().includes('add to cart') ||
          (el.getAttribute('aria-label') || '')
            .toLowerCase()
            .includes('add to cart')
      );

      if (!addBtn) {
        return errorResponse('Add to Cart button not found');
      }

      const times = qtyInput || qtySelect ? 1 : Math.max(1, quantity);
      for (let i = 0; i < times; i++) {
        addBtn.click();
        await sleep(CLICK_DELAY_GAMESTOP);
      }

      return { success: true };
    });
  }

  // Best Buy: click add-to-cart
  async function addToCartBestBuy(quantity) {
    return tryAddToCart(async () => {
      const addBtn = document.querySelector(
        'button[class*="add-to-cart"], button[class*="addToCart"]'
      );
      if (!addBtn || addBtn.disabled) {
        return errorResponse(ERROR_BUTTON_NOT_FOUND);
      }

      for (let i = 0; i < quantity; i++) {
        addBtn.click();
        await sleep(CLICK_DELAY_DEFAULT);
      }

      return { success: true };
    });
  }

  // Target: click add-to-cart
  async function addToCartTarget(quantity) {
    return tryAddToCart(async () => {
      const addBtn = document.querySelector('button[data-test*="addToCart"]');
      if (!addBtn || addBtn.disabled) {
        return errorResponse(ERROR_BUTTON_NOT_FOUND);
      }

      for (let i = 0; i < quantity; i++) {
        addBtn.click();
        await sleep(CLICK_DELAY_DEFAULT);
      }

      return { success: true };
    });
  }

  // Walmart: click add-to-cart
  async function addToCartWalmart(quantity) {
    return tryAddToCart(async () => {
      const addBtn = document.querySelector(
        'button[class*="add-to-cart"], button[data-automation-id*="add-to-cart"]'
      );
      if (!addBtn || addBtn.disabled) {
        return errorResponse(ERROR_BUTTON_NOT_FOUND);
      }

      for (let i = 0; i < quantity; i++) {
        addBtn.click();
        await sleep(CLICK_DELAY_DEFAULT);
      }

      return { success: true };
    });
  }

  // Pokemon Center: click add-to-cart
  async function addToCartPokemonCenter(quantity) {
    return tryAddToCart(async () => {
      const addBtn = document.querySelector('button[name="add"]');
      if (!addBtn || addBtn.disabled) {
        return errorResponse(ERROR_BUTTON_NOT_FOUND);
      }

      for (let i = 0; i < quantity; i++) {
        addBtn.click();
        await sleep(CLICK_DELAY_DEFAULT);
      }

      return { success: true };
    });
  }
})();

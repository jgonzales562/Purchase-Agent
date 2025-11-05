# Quick Add to Cart - Browser Extension

## What It Is

A simple Chrome browser extension that quickly adds products to your cart with one click. Set your desired quantity and add items instantly without manual clicking.

## Features

- 🛒 **One-click add to cart** - Quick purchase with custom quantities
- 🎯 **Multi-site support** - Works on GameStop, Best Buy, Target, Walmart, Pokémon Center
- � **Quantity control** - Choose quantity 1-10 before adding
- 💾 **Remembers preferences** - Saves your quantity per product
- ⚡ **Fast & simple** - No unnecessary features, just quick adding

## Installation

### For Chrome/Edge:

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select the `Purchase-Agent` folder
5. The extension icon will appear in your toolbar

## Usage

1. **Visit any product page** on a supported site
2. **Click the extension icon** in your toolbar
3. **Set your quantity** (1-10)
4. **Click "🛒 Add to Cart"** button
5. Done! The product is added to your cart

## How It Works

The extension detects when you're on a supported product page and enables a simple interface to:

- Select the quantity you want
- Automatically click the site's add-to-cart button with the right quantity
- Save your quantity preference for next time

No bots, no automation - just your browser doing the clicking for you!

## Supported Sites

- GameStop (gamestop.com)
- Best Buy (bestbuy.com)
- Target (target.com)
- Walmart (walmart.com)
- Pokémon Center (pokemoncenter.com)

## Files

- `manifest.json` - Extension configuration
- `popup.html` - Extension popup interface
- `popup.js` - Popup UI logic
- `content.js` - Site-specific add-to-cart logic
- `background.js` - Storage handler for preferences

## Privacy

This extension:

- ✅ Only runs on product pages of supported sites
- ✅ Stores quantity preferences locally on your device
- ✅ Does not collect or transmit any data
- ✅ Does not track your browsing
- ✅ Open source - inspect the code yourself!

## License

Free to use and modify.

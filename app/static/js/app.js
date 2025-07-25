// SaaS Shop JavaScript

// Shopping Cart Management
class ShoppingCart {
    constructor() {
        this.items = JSON.parse(localStorage.getItem('cart')) || [];
        this.updateCartUI();
    }

    addItem(productId, name, price, currency, image = null, quantity = 1) {
        const existingItem = this.items.find(item => item.productId === productId);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({
                productId: productId,
                name: name,
                price: price,
                currency: currency,
                image: image,
                quantity: quantity
            });
        }
        
        this.saveToStorage();
        this.updateCartUI();
        this.showAddedMessage(name);
    }

    removeItem(productId) {
        this.items = this.items.filter(item => item.productId !== productId);
        this.saveToStorage();
        this.updateCartUI();
    }

    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.productId === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = quantity;
                this.saveToStorage();
                this.updateCartUI();
            }
        }
    }

    getTotalAmount() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    getTotalItems() {
        return this.items.reduce((total, item) => total + item.quantity, 0);
    }

    saveToStorage() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    updateCartUI() {
        const cartCount = document.getElementById('cartCount');
        const cartItems = document.getElementById('cartItems');
        const cartTotal = document.getElementById('cartTotal');
        const totalAmount = document.getElementById('totalAmount');

        // Update cart count
        const totalItems = this.getTotalItems();
        if (cartCount) {
            cartCount.textContent = totalItems;
            cartCount.style.display = totalItems > 0 ? 'inline' : 'none';
        }

        // Update cart items
        if (cartItems) {
            if (this.items.length === 0) {
                cartItems.innerHTML = '<p class="text-muted">Кошик порожній</p>';
                if (cartTotal) cartTotal.classList.add('d-none');
            } else {
                cartItems.innerHTML = this.items.map(item => `
                    <div class="cart-item d-flex align-items-center">
                        ${item.image ? `<img src="/static/uploads/${item.image}" alt="${item.name}" class="me-2">` : ''}
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${item.name}</h6>
                            <small class="text-muted">${item.price} ${item.currency}</small>
                        </div>
                        <div class="d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-secondary" onclick="cart.updateQuantity(${item.productId}, ${item.quantity - 1})">-</button>
                            <span class="mx-2">${item.quantity}</span>
                            <button class="btn btn-sm btn-outline-secondary" onclick="cart.updateQuantity(${item.productId}, ${item.quantity + 1})">+</button>
                            <button class="btn btn-sm btn-outline-danger ms-2" onclick="cart.removeItem(${item.productId})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
                
                if (cartTotal) {
                    cartTotal.classList.remove('d-none');
                    if (totalAmount) {
                        // Get currency from first item (assuming all items have same currency)
                        const currency = this.items.length > 0 ? this.items[0].currency : 'EUR';
                        totalAmount.textContent = `${this.getTotalAmount().toFixed(2)} ${currency}`;
                    }
                }
            }
        }
    }

    showAddedMessage(productName) {
        // Create a temporary toast message
        const toast = document.createElement('div');
        toast.className = 'toast position-fixed bottom-0 start-50 translate-middle-x mb-3';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <div class="toast-body bg-success text-white rounded">
                <i class="fas fa-check-circle me-2"></i>
                ${productName} додано до кошика!
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it hides
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }

    clear() {
        this.items = [];
        this.saveToStorage();
        this.updateCartUI();
    }
}

// Initialize shopping cart
const cart = new ShoppingCart();

// Add to cart function (called from HTML)
function addToCart(productId) {
    // Get product details from the page or make an API call
    // For now, we'll extract from the current page elements
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);
    if (productElement) {
        const name = productElement.querySelector('.card-title').textContent;
        const priceText = productElement.querySelector('.text-primary').textContent;
        const [price, currency] = priceText.split(' ');
        const image = productElement.querySelector('img')?.src.split('/').pop();
        
        cart.addItem(productId, name, parseFloat(price), currency, image);
    } else {
        // Fallback: make API call to get product details
        fetch(`/api/products?product_id=${productId}`)
            .then(response => response.json())
            .then(products => {
                if (products.length > 0) {
                    const product = products[0];
                    cart.addItem(productId, product.name, product.price, product.currency, product.image);
                }
            })
            .catch(error => console.error('Error fetching product:', error));
    }
}

// Checkout function
async function checkout() {
    if (cart.items.length === 0) {
        alert('Кошик порожній!');
        return;
    }

    try {
        const response = await fetch('/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                items: cart.items.map(item => ({
                    product_id: item.productId,
                    quantity: item.quantity
                }))
            })
        });

        const data = await response.json();
        
        if (data.session_id) {
            if (data.demo_mode) {
                // Demo mode - redirect directly to success page
                window.location.href = data.redirect_url;
            } else {
                // Real Stripe checkout
                if (typeof Stripe !== 'undefined' && STRIPE_PUBLISHABLE_KEY) {
                    const stripe = Stripe(STRIPE_PUBLISHABLE_KEY);
                    await stripe.redirectToCheckout({
                        sessionId: data.session_id
                    });
                } else {
                    // Fallback for when Stripe is not configured
                    alert('Stripe не настроен. Перенаправляю на демо-страницу...');
                    window.location.href = `/checkout/success?session_id=${data.session_id}`;
                }
            }
        } else {
            alert('Помилка при створенні сесії оплати: ' + (data.error || 'Невідома помилка'));
        }
    } catch (error) {
        console.error('Checkout error:', error);
        alert('Помилка при оформленні замовлення');
    }
}

// Chatbot functionality
class Chatbot {
    constructor() {
        this.messages = [];
        this.currentLanguage = document.documentElement.lang || 'uk';
        this.sessionId = this.getOrCreateSessionId();
    }

    getOrCreateSessionId() {
        // Get session ID from localStorage or create new one
        let sessionId = localStorage.getItem('chatbot_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chatbot_session_id', sessionId);
        }
        return sessionId;
    }

    async sendMessage(message) {
        if (!message.trim()) return;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTyping();

        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTyping();

            if (data.response) {
                this.addMessage(data.response, 'bot');
                // Update session ID if returned from server
                if (data.session_id) {
                    this.sessionId = data.session_id;
                    localStorage.setItem('chatbot_session_id', this.sessionId);
                }
            } else {
                this.addMessage('Вибачте, сталася помилка. Спробуйте пізніше.', 'bot');
            }
        } catch (error) {
            this.hideTyping();
            console.error('Chatbot error:', error);
            this.addMessage('Помилка з\'єднання. Перевірте інтернет-з\'єднання.', 'bot');
        }
    }

    addMessage(message, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.textContent = message;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTyping() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-message bot';
        typingDiv.innerHTML = '<div class="spinner"></div>';
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize chatbot
const chatbot = new Chatbot();

// Send chat message function
function sendChatMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();
    
    if (message) {
        chatbot.sendMessage(message);
        input.value = '';
    }
}

// Language management
function changeLanguage(lang) {
    // Store language preference
    localStorage.setItem('preferred_language', lang);
    
    // Redirect to set language route
    window.location.href = `/set_language/${lang}`;
}

// Utility functions
function formatPrice(price, currency) {
    return new Intl.NumberFormat('uk-UA', {
        style: 'currency',
        currency: currency || 'EUR'
    }).format(price);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA');
}

// Image lazy loading
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize lazy loading
    lazyLoadImages();
    
    // Set up chatbot input enter key listener
    const chatbotInput = document.getElementById('chatbot-input');
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    // Load preferred language
    const preferredLanguage = localStorage.getItem('preferred_language');
    if (preferredLanguage && preferredLanguage !== document.documentElement.lang) {
        // Optional: could auto-redirect to preferred language
    }
    
    // Initialize tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize product cards with data attributes
    document.querySelectorAll('.product-card').forEach(card => {
        const productData = card.querySelector('[data-product-id]');
        if (productData) {
            card.setAttribute('data-product-id', productData.dataset.productId);
        }
    });
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send error reports to server in production
});

// Service Worker registration (for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

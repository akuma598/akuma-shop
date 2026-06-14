from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>TechStore | Магазин электроники</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
        }
        
        .header {
            background: #ffffff;
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid #e0e0e0;
            padding: 12px 20px;
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(135deg, #1d1d1f, #4a4a4a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .cart-icon {
            position: relative;
            cursor: pointer;
            font-size: 24px;
        }
        
        .cart-count {
            position: absolute;
            top: -8px;
            right: -12px;
            background: #ff4444;
            color: white;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 10px;
            min-width: 18px;
            text-align: center;
        }
        
        .filters {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            background: white;
            border: 1px solid #ddd;
            padding: 8px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: 0.2s;
            font-size: 14px;
        }
        
        .filter-btn.active {
            background: #1d1d1f;
            color: white;
            border-color: #1d1d1f;
        }
        
        .products {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
        }
        
        .product-card {
            background: white;
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }
        
        .product-image {
            background: #f5f5f7;
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 80px;
        }
        
        .product-info {
            padding: 16px;
        }
        
        .product-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .product-category {
            font-size: 12px;
            color: #888;
            margin-bottom: 8px;
        }
        
        .product-price {
            font-size: 20px;
            font-weight: bold;
            color: #1d1d1f;
            margin-bottom: 12px;
        }
        
        .product-old-price {
            font-size: 14px;
            color: #888;
            text-decoration: line-through;
            margin-left: 8px;
            font-weight: normal;
        }
        
        .add-to-cart {
            background: #1d1d1f;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 30px;
            width: 100%;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .add-to-cart:hover {
            background: #333;
        }
        
        .cart-modal {
            display: none;
            position: fixed;
            top: 0;
            right: 0;
            width: 100%;
            max-width: 400px;
            height: 100%;
            background: white;
            box-shadow: -4px 0 20px rgba(0,0,0,0.1);
            z-index: 200;
            flex-direction: column;
        }
        
        .cart-modal.open {
            display: flex;
        }
        
        .cart-header {
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .cart-items {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .cart-item {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .cart-item-image {
            width: 60px;
            height: 60px;
            background: #f5f5f7;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
        }
        
        .cart-item-info {
            flex: 1;
        }
        
        .cart-item-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .cart-item-price {
            color: #ff4444;
            font-weight: bold;
        }
        
        .cart-item-quantity {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 8px;
        }
        
        .qty-btn {
            background: #f0f0f0;
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .cart-total {
            padding: 20px;
            border-top: 1px solid #e0e0e0;
            background: white;
        }
        
        .checkout-btn {
            background: #1d1d1f;
            color: white;
            border: none;
            padding: 14px;
            width: 100%;
            border-radius: 30px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        
        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 150;
        }
        
        .overlay.open {
            display: block;
        }
        
        .product-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            max-width: 500px;
            background: white;
            border-radius: 24px;
            z-index: 250;
            overflow: hidden;
        }
        
        .product-modal.open {
            display: block;
        }
        
        .product-modal-content {
            padding: 24px;
        }
        
        .close-modal {
            float: right;
            font-size: 24px;
            cursor: pointer;
        }
        
        .footer {
            background: #1d1d1f;
            color: #888;
            text-align: center;
            padding: 30px;
            margin-top: 40px;
        }
        
        @media (max-width: 768px) {
            .products {
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 15px;
            }
            .cart-modal {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">⚡ TECHSTORE</div>
            <div class="cart-icon" onclick="openCart()">
                🛒
                <span class="cart-count" id="cartCount">0</span>
            </div>
        </div>
    </div>
    
    <div class="filters">
        <button class="filter-btn active" data-category="all">Все товары</button>
        <button class="filter-btn" data-category="headphones">🎧 Наушники</button>
        <button class="filter-btn" data-category="phones">📱 Смартфоны</button>
        <button class="filter-btn" data-category="accessories">🔌 Аксессуары</button>
        <button class="filter-btn" data-category="laptops">💻 Ноутбуки</button>
    </div>
    
    <div class="products" id="products"></div>
    
    <div class="footer">
        <p>© 2025 TechStore — Магазин качественной электроники</p>
        <p style="margin-top: 10px; font-size: 12px;">Быстрая доставка | Официальная гарантия</p>
    </div>
    
    <div class="overlay" id="overlay" onclick="closeCart()"></div>
    <div class="cart-modal" id="cartModal">
        <div class="cart-header">
            <h3>🛒 Корзина</h3>
            <span style="font-size: 24px; cursor: pointer;" onclick="closeCart()">✕</span>
        </div>
        <div class="cart-items" id="cartItems"></div>
        <div class="cart-total">
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <span>Итого:</span>
                <span id="cartTotal" style="font-size: 22px; font-weight: bold;">0 ₽</span>
            </div>
            <button class="checkout-btn" onclick="checkout()">Оформить заказ</button>
        </div>
    </div>
    
    <div class="product-modal" id="productModal">
        <div class="product-modal-content">
            <span class="close-modal" onclick="closeProductModal()">✕</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        const products = [
            {
                id: 1,
                name: "AirPods Pro 2",
                category: "headphones",
                price: 24990,
                oldPrice: 29990,
                color: "Темно-серый",
                image: "🎧",
                description: "Активное шумоподавление, прозрачный режим, пространственное аудио, адаптивная эквалайзер. До 6 часов работы."
            },
            {
                id: 2,
                name: "AirPods 4",
                category: "headphones",
                price: 14990,
                oldPrice: 17990,
                color: "Темно-серый",
                image: "🎧",
                description: "Новый дизайн, улучшенный звук, сенсорное управление, быстрая зарядка."
            },
            {
                id: 3,
                name: "Sony WH-1000XM5",
                category: "headphones",
                price: 34990,
                oldPrice: 39990,
                color: "Черный",
                image: "🎧",
                description: "Лучшее шумоподавление, 30 часов работы, быстрая зарядка."
            },
            {
                id: 4,
                name: "iPhone 15 Pro",
                category: "phones",
                price: 99990,
                oldPrice: 109990,
                color: "Натуральный титан",
                image: "📱",
                description: "Чип A17 Pro, титановый корпус, 48 МП камера, USB-C."
            },
            {
                id: 5,
                name: "Samsung Galaxy S24 Ultra",
                category: "phones",
                price: 89990,
                oldPrice: 99990,
                color: "Титан",
                image: "📱",
                description: "200 МП камера, S Pen, ИИ-функции."
            },
            {
                id: 6,
                name: "MacBook Pro 14",
                category: "laptops",
                price: 199990,
                oldPrice: 229990,
                color: "Космический серый",
                image: "💻",
                description: "Чип M3 Pro, 16 ГБ RAM, 512 ГБ SSD, дисплей Liquid Retina XDR."
            },
            {
                id: 7,
                name: "Belkin MagSafe Power Bank",
                category: "accessories",
                price: 4990,
                oldPrice: 6990,
                color: "Белый",
                image: "🔋",
                description: "Беспроводная зарядка 15 Вт, магнитная фиксация."
            },
            {
                id: 8,
                name: "Apple Watch Ultra 2",
                category: "accessories",
                price: 72990,
                oldPrice: 79990,
                color: "Титан",
                image: "⌚",
                description: "49-мм корпус из титана, GPS, водонепроницаемость."
            }
        ];
        
        let cart = JSON.parse(localStorage.getItem('cart')) || {};
        let currentCategory = 'all';
        
        function formatPrice(price) {
            return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }
        
        function getCategoryName(cat) {
            const names = {
                headphones: 'Наушники',
                phones: 'Смартфоны',
                laptops: 'Ноутбуки',
                accessories: 'Аксессуары'
            };
            return names[cat] || cat;
        }
        
        function renderProducts() {
            const container = document.getElementById('products');
            if (!container) return;
            
            const filtered = currentCategory === 'all' 
                ? products 
                : products.filter(p => p.category === currentCategory);
            
            let html = '';
            for (let product of filtered) {
                html += `
                    <div class="product-card" onclick="openProductModal(${product.id})">
                        <div class="product-image">${product.image}</div>
                        <div class="product-info">
                            <div class="product-title">${product.name}</div>
                            <div class="product-category">${product.color} | ${getCategoryName(product.category)}</div>
                            <div class="product-price">
                                ${formatPrice(product.price)} ₽
                                ${product.oldPrice ? `<span class="product-old-price">${formatPrice(product.oldPrice)} ₽</span>` : ''}
                            </div>
                            <button class="add-to-cart" onclick="event.stopPropagation(); addToCart(${product.id})">В корзину</button>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }
        
        function addToCart(productId) {
            if (!cart[productId]) {
                cart[productId] = { quantity: 1 };
            } else {
                cart[productId].quantity++;
            }
            saveCart();
            updateCartCount();
            renderCart();
        }
        
        function removeFromCart(productId) {
            if (cart[productId]) {
                cart[productId].quantity--;
                if (cart[productId].quantity <= 0) {
                    delete cart[productId];
                }
            }
            saveCart();
            updateCartCount();
            renderCart();
        }
        
        function updateCartCount() {
            let count = 0;
            for (let id in cart) {
                count += cart[id].quantity;
            }
            const cartCountEl = document.getElementById('cartCount');
            if (cartCountEl) cartCountEl.innerText = count;
        }
        
        function saveCart() {
            localStorage.setItem('cart', JSON.stringify(cart));
        }
        
        function renderCart() {
            const container = document.getElementById('cartItems');
            if (!container) return;
            
            let total = 0;
            let html = '';
            
            for (let id in cart) {
                const product = products.find(p => p.id == id);
                if (product) {
                    const itemTotal = product.price * cart[id].quantity;
                    total += itemTotal;
                    html += `
                        <div class="cart-item">
                            <div class="cart-item-image">${product.image}</div>
                            <div class="cart-item-info">
                                <div class="cart-item-title">${product.name}</div>
                                <div class="cart-item-price">${formatPrice(product.price)} ₽</div>
                                <div class="cart-item-quantity">
                                    <button class="qty-btn" onclick="removeFromCart(${product.id})">-</button>
                                    <span>${cart[id].quantity}</span>
                                    <button class="qty-btn" onclick="addToCart(${product.id})">+</button>
                                </div>
                            </div>
                            <div style="font-weight: bold;">${formatPrice(itemTotal)} ₽</div>
                        </div>
                    `;
                }
            }
            
            if (Object.keys(cart).length === 0) {
                html = '<div style="text-align: center; padding: 40px; color: #888;">Корзина пуста</div>';
            }
            
            container.innerHTML = html;
            const cartTotalEl = document.getElementById('cartTotal');
            if (cartTotalEl) cartTotalEl.innerHTML = formatPrice(total) + ' ₽';
        }
        
        function openCart() {
            renderCart();
            const cartModal = document.getElementById('cartModal');
            const overlay = document.getElementById('overlay');
            if (cartModal) cartModal.classList.add('open');
            if (overlay) overlay.classList.add('open');
        }
        
        function closeCart() {
            const cartModal = document.getElementById('cartModal');
            const overlay = document.getElementById('overlay');
            if (cartModal) cartModal.classList.remove('open');
            if (overlay) overlay.classList.remove('open');
        }
        
        function openProductModal(productId) {
            const product = products.find(p => p.id === productId);
            if (!product) return;
            
            const inCart = cart[productId] ? cart[productId].quantity : 0;
            const modalContent = document.getElementById('modalContent');
            if (!modalContent) return;
            
            modalContent.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 80px; margin: 20px 0;">${product.image}</div>
                    <h2 style="margin-bottom: 10px;">${product.name}</h2>
                    <div style="color: #888; margin-bottom: 15px;">${product.color} | ${getCategoryName(product.category)}</div>
                    <div style="font-size: 28px; font-weight: bold; color: #ff4444; margin-bottom: 10px;">
                        ${formatPrice(product.price)} ₽
                        ${product.oldPrice ? `<span style="font-size: 18px; color: #888; text-decoration: line-through; margin-left: 10px;">${formatPrice(product.oldPrice)} ₽</span>` : ''}
                    </div>
                    <p style="color: #666; line-height: 1.5; margin-bottom: 20px;">${product.description}</p>
                    <div style="display: flex; gap: 10px;">
                        <button class="add-to-cart" onclick="addToCart(${product.id}); closeProductModal();" style="flex: 1;">В корзину</button>
                        <button class="add-to-cart" onclick="closeProductModal()" style="background: #666;">Закрыть</button>
                    </div>
                    ${inCart > 0 ? `<p style="margin-top: 15px; color: #888;">Уже в корзине: ${inCart} шт.</p>` : ''}
                </div>
            `;
            
            const productModal = document.getElementById('productModal');
            const overlay = document.getElementById('overlay');
            if (productModal) productModal.classList.add('open');
            if (overlay) overlay.classList.add('open');
        }
        
        function closeProductModal() {
            const productModal = document.getElementById('productModal');
            const overlay = document.getElementById('overlay');
            if (productModal) productModal.classList.remove('open');
            if (overlay) overlay.classList.remove('open');
        }
        
        function checkout() {
            if (Object.keys(cart).length === 0) {
                alert('Корзина пуста');
                return;
            }
            alert('✅ Заказ оформлен!\n\nС вами свяжется менеджер для подтверждения.\n\nСпасибо за покупку!');
            cart = {};
            saveCart();
            updateCartCount();
            closeCart();
            renderProducts();
        }
        
        // Фильтры
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentCategory = this.dataset.category;
                renderProducts();
            });
        });
        
        renderProducts();
        updateCartCount();
        
        // Закрытие модалки по клику на overlay
        document.getElementById('overlay')?.addEventListener('click', () => {
            closeCart();
            closeProductModal();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

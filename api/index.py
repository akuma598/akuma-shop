from flask import Flask, request, jsonify
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "akuma_ucbot")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8504217011"))

temp_orders = {}
order_counter = 1

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>PUBG Mobile Shop</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 24px;
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            color: #888;
            font-size: 12px;
            margin-top: 5px;
        }
        
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.05);
            padding: 5px;
            border-radius: 12px;
        }
        
        .nav-item {
            flex: 1;
            text-align: center;
            padding: 12px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            font-weight: bold;
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            color: #1a1a2e;
        }
        
        .banner {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .banner h2 {
            color: #1a1a2e;
            margin-bottom: 5px;
        }
        
        .banner p {
            color: #1a1a2e;
            font-size: 12px;
            opacity: 0.8;
        }
        
        .products {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 30px;
        }
        
        .product-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.2s;
            cursor: pointer;
        }
        
        .product-card:hover {
            background: rgba(255,255,255,0.1);
            border-color: #ffcc00;
        }
        
        .product-image {
            width: 60px;
            height: 60px;
            margin: 0 auto 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
        }
        
        .product-name {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .product-price {
            color: #ffcc00;
            font-weight: bold;
            font-size: 16px;
        }
        
        .product-old-price {
            color: #888;
            font-size: 12px;
            text-decoration: line-through;
            margin-left: 8px;
        }
        
        .cart-section {
            background: rgba(0,0,0,0.5);
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid rgba(255,204,0,0.3);
        }
        
        .cart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .cart-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .cart-total {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.2);
            font-size: 18px;
            font-weight: bold;
            text-align: right;
            color: #ffcc00;
        }
        
        .clear-cart {
            background: rgba(255,0,0,0.2);
            border: 1px solid #ff4444;
            color: #ff4444;
            padding: 8px 15px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .buy-code-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 16px;
            width: 100%;
            border-radius: 12px;
            color: #1a1a2e;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .pubg-input {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .pubg-input input {
            width: 100%;
            padding: 14px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 16px;
            outline: none;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #666;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 20px;
        }
        
        .footer a {
            color: #ffcc00;
            text-decoration: none;
        }
        
        .hide {
            display: none;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #2e004d, #1a0033);
            border-radius: 24px;
            padding: 30px;
            text-align: center;
            border: 2px solid #ffcc00;
            max-width: 350px;
            margin: 20px;
        }
        
        .modal-content h2 {
            color: #ffcc00;
            margin-bottom: 15px;
            font-size: 24px;
        }
        
        .modal-content .order-id {
            font-size: 32px;
            font-weight: bold;
            color: #ffcc00;
            margin: 15px 0;
        }
        
        .modal-content .total {
            font-size: 28px;
            color: #ffcc00;
            font-weight: bold;
        }
        
        .modal-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 12px 30px;
            border-radius: 12px;
            color: #1a0033;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            font-size: 16px;
            width: 100%;
        }
        
        .copy-btn {
            background: rgba(255,255,255,0.1);
            border: 1px solid #ffcc00;
            padding: 8px 20px;
            border-radius: 10px;
            color: #ffcc00;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            width: 100%;
        }
        
        @media (max-width: 480px) {
            .products {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 PUBG Mobile Shop</h1>
            <p>Пополнение по ID | Мгновенная выдача</p>
        </div>
        
        <div class="nav">
            <div class="nav-item active" onclick="switchTab('uc')">UC</div>
            <div class="nav-item" onclick="switchTab('pp')">ПП</div>
            <div class="nav-item" onclick="switchTab('skins')">Скины</div>
            <div class="nav-item" onclick="switchTab('subscriptions')">Подписки</div>
        </div>
        
        <div class="banner">
            <h2>🎮 Пополнение по ID</h2>
            <p>UC будут зачислены на указанный вами ID автоматически в течение 5 минут!</p>
        </div>
        
        <div id="tab-uc"><div class="products" id="uc-products"></div></div>
        <div id="tab-pp" class="hide"><div class="products" id="pp-products"></div></div>
        <div id="tab-skins" class="hide"><div class="products" id="skins-products"></div></div>
        <div id="tab-subscriptions" class="hide"><div class="products" id="subscriptions-products"></div></div>
        
        <div class="pubg-input">
            <input type="number" id="pubg_id" placeholder="Введите PUBG ID получателя (начинается с 5)">
        </div>
        
        <div class="cart-section">
            <div class="cart-header">
                <h3>🛒 Корзина</h3>
                <button class="clear-cart" onclick="clearCart()">Очистить</button>
            </div>
            <div id="cart-items"></div>
            <div id="cart-total" class="cart-total">Итого: 0 ₽</div>
        </div>
        
        <button class="buy-code-btn" onclick="createOrderFromCart()">💳 Оформить заказ</button>
        
        <div class="footer">
            <p>Вопросы: <a href="https://t.me/aakumma">@aakumma</a></p>
        </div>
    </div>
    
    <div id="orderModal" class="modal">
        <div class="modal-content">
            <h2>✅ ЗАКАЗ ПРИНЯТ!</h2>
            <div class="order-id" id="modalOrderId">#0</div>
            <p>на сумму</p>
            <div class="total" id="modalTotal">0 ₽</div>
            <button class="copy-btn" onclick="copyOrderId()">📋 Скопировать номер заказа</button>
            <button class="modal-btn" onclick="goToBot()">📱 Перейти в бота для оплаты</button>
            <p style="font-size: 11px; color: #b87dff; margin-top: 15px;">
                💡 Если бот не открылся — нажмите три точки (⋮) → «Открыть в браузере»
            </p>
        </div>
    </div>
    
    <script>
        // UC ТОВАРЫ
        const ucProducts = {
            "60": {"name": "60 UC", "price": 71, "oldPrice": 80, "icon": "🎮"},
            "120": {"name": "120 UC", "price": 141, "oldPrice": 162, "icon": "🎮"},
            "180": {"name": "180 UC", "price": 211, "oldPrice": 243, "icon": "🎮"},
            "240": {"name": "240 UC", "price": 281, "oldPrice": 324, "icon": "🎮"},
            "325": {"name": "325 UC", "price": 349, "oldPrice": 405, "icon": "🎮"},
            "385": {"name": "385 UC", "price": 419, "oldPrice": 485, "icon": "🎮"},
            "445": {"name": "445 UC", "price": 482, "oldPrice": 560, "icon": "🎮"},
            "660": {"name": "660 UC", "price": 708, "oldPrice": 820, "icon": "🎮"},
            "720": {"name": "720 UC", "price": 771, "oldPrice": 895, "icon": "🎮"},
            "985": {"name": "985 UC", "price": 1049, "oldPrice": 1220, "icon": "🎮"},
            "1320": {"name": "1320 UC", "price": 1401, "oldPrice": 1630, "icon": "🎮"},
            "1800": {"name": "1800 UC", "price": 1891, "oldPrice": 2200, "icon": "🎮"}
        };
        
        // ПП ТОВАРЫ
        const ppProducts = {
            "10000": {"name": "10 000 ПП", "price": 152, "icon": "👑"},
            "20000": {"name": "20 000 ПП", "price": 289, "icon": "👑"},
            "30000": {"name": "30 000 ПП", "price": 424, "icon": "👑"},
            "40000": {"name": "40 000 ПП", "price": 561, "icon": "👑"},
            "50000": {"name": "50 000 ПП", "price": 696, "icon": "👑"},
            "60000": {"name": "60 000 ПП", "price": 833, "icon": "👑"}
        };
        
        // СКИНЫ
        const skinsProducts = {
            "1": {"name": "❄️ Frozen Dragon", "price": 1500, "icon": "🐉"},
            "2": {"name": "🔥 Phoenix Wings", "price": 1800, "icon": "🔥"},
            "3": {"name": "🗡️ Shadow Blade", "price": 1200, "icon": "🗡️"}
        };
        
        // ПОДПИСКИ
        const subscriptionsProducts = {
            "1m": {"name": "Prime (1 месяц)", "price": 125, "icon": "⭐"},
            "3m": {"name": "Prime (3 месяца)", "price": 318, "icon": "⭐⭐"},
            "6m": {"name": "Prime (6 месяцев)", "price": 550, "icon": "⭐⭐⭐"},
            "12m": {"name": "Prime (12 месяцев)", "price": 1027, "icon": "⭐⭐⭐⭐"}
        };
        
        const botUsername = "akuma_ucbot";
        
        let cart = JSON.parse(localStorage.getItem('cart')) || {};
        let currentTab = 'uc';
        
        function renderProducts(containerId, products) {
            const container = document.getElementById(containerId);
            let html = '';
            for (const [key, product] of Object.entries(products)) {
                const quantity = cart[key] ? cart[key].quantity : 0;
                html += `
                    <div class="product-card">
                        <div class="product-image">${product.icon}</div>
                        <div class="product-name">${product.name}</div>
                        <div>
                            <span class="product-price">${product.price} ₽</span>
                            ${product.oldPrice ? `<span class="product-old-price">${product.oldPrice} ₽</span>` : ''}
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 10px;">
                            <button class="clear-cart" style="padding: 5px 10px;" onclick="updateQuantity('${key}', -1)">-</button>
                            <span style="min-width: 30px; text-align: center;">${quantity}</span>
                            <button class="clear-cart" style="padding: 5px 10px; background: rgba(255,204,0,0.2); border-color: #ffcc00; color: #ffcc00;" onclick="updateQuantity('${key}', 1)">+</button>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }
        
        function updateQuantity(key, delta) {
            if (!cart[key]) {
                const product = getProductByKey(key);
                if (!product) return;
                cart[key] = {name: product.name, price: product.price, quantity: 0};
            }
            let newQty = cart[key].quantity + delta;
            if (newQty <= 0) {
                delete cart[key];
            } else {
                cart[key].quantity = newQty;
            }
            saveCart();
            updateCartDisplay();
            renderCurrentTab();
        }
        
        function getProductByKey(key) {
            const allProducts = {...ucProducts, ...ppProducts, ...skinsProducts, ...subscriptionsProducts};
            return allProducts[key];
        }
        
        function addToCart(key, name, price) {
            if (!cart[key]) cart[key] = {name: name, price: price, quantity: 0};
            cart[key].quantity++;
            saveCart();
            updateCartDisplay();
            renderCurrentTab();
        }
        
        function updateCartDisplay() {
            const container = document.getElementById('cart-items');
            let total = 0;
            let html = '';
            for (const [key, item] of Object.entries(cart)) {
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                html += `<div class="cart-item"><span>${item.name} x${item.quantity}</span><span>${itemTotal} ₽</span></div>`;
            }
            container.innerHTML = Object.keys(cart).length === 0 ? '<div style="text-align:center;color:#888;">Корзина пуста</div>' : html;
            document.getElementById('cart-total').innerHTML = 'Итого: ' + total + ' ₽';
            return total;
        }
        
        function clearCart() {
            cart = {};
            saveCart();
            updateCartDisplay();
            renderCurrentTab();
            alert('🗑 Корзина очищена');
        }
        
        function saveCart() {
            localStorage.setItem('cart', JSON.stringify(cart));
        }
        
        function renderCurrentTab() {
            if (currentTab === 'uc') renderProducts('uc-products', ucProducts);
            else if (currentTab === 'pp') renderProducts('pp-products', ppProducts);
            else if (currentTab === 'skins') renderProducts('skins-products', skinsProducts);
            else if (currentTab === 'subscriptions') renderProducts('subscriptions-products', subscriptionsProducts);
        }
        
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            document.querySelector(`.nav-item[onclick="switchTab('${tab}')"]`).classList.add('active');
            
            document.getElementById('tab-uc').classList.add('hide');
            document.getElementById('tab-pp').classList.add('hide');
            document.getElementById('tab-skins').classList.add('hide');
            document.getElementById('tab-subscriptions').classList.add('hide');
            document.getElementById(`tab-${tab}`).classList.remove('hide');
            renderCurrentTab();
        }
        
        function copyOrderId() {
            const orderId = document.getElementById('modalOrderId').innerText;
            navigator.clipboard.writeText(orderId);
            alert('✅ Номер заказа скопирован: ' + orderId);
        }
        
        function goToBot() {
            window.location.href = 'https://t.me/' + botUsername;
        }
        
        function showOrderModal(orderId, total) {
            const modal = document.getElementById('orderModal');
            document.getElementById('modalOrderId').innerText = '#' + orderId;
            document.getElementById('modalTotal').innerText = total + ' ₽';
            modal.style.display = 'flex';
        }
        
        async function createOrderFromCart() {
            const pubgId = document.getElementById('pubg_id').value;
            
            if (!pubgId) {
                alert('❌ Введите PUBG ID получателя');
                return;
            }
            if (!pubgId.toString().startsWith('5') || pubgId.toString().length < 10) {
                alert('❌ PUBG ID должен начинаться с 5 и содержать минимум 10 цифр');
                return;
            }
            if (Object.keys(cart).length === 0) {
                alert('❌ Корзина пуста');
                return;
            }
            
            let total = 0;
            for (const item of Object.values(cart)) total += item.price * item.quantity;
            
            try {
                const response = await fetch('/create-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({pubg_id: pubgId, items: cart, total: total})
                });
                const data = await response.json();
                if (data.ok && data.order_id) {
                    showOrderModal(data.order_id, total);
                    cart = {};
                    saveCart();
                    updateCartDisplay();
                    renderCurrentTab();
                } else {
                    alert('❌ Ошибка при создании заказа');
                }
            } catch (error) {
                alert('❌ Ошибка сервера');
            }
        }
        
        renderCurrentTab();
        updateCartDisplay();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

@app.route('/create-order', methods=['POST'])
def create_order():
    global order_counter
    data = request.json
    pubg_id = data.get('pubg_id')
    items = data.get('items')
    total = data.get('total')
    
    print(f"📥 НОВЫЙ ЗАКАЗ: pubg_id={pubg_id}, total={total}")
    print(f"📦 ТОВАРЫ: {items}")
    
    if not pubg_id or not items:
        return jsonify({'error': 'Missing data'}), 400
    
    order_id = order_counter
    order_counter += 1
    
    temp_orders[order_id] = {
        'pubg_id': pubg_id,
        'items': items,
        'total': total,
        'status': 'pending',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Отправляем уведомление админу
    if BOT_TOKEN:
        try:
            items_text = '\n'.join([f"• {item['name']} x{item['quantity']} = {item['price'] * item['quantity']}₽" for item in items.values()])
            admin_text = f"🆕 **НОВЫЙ ЗАКАЗ С САЙТА**\n\n🆔 Номер: #{order_id}\n🎮 PUBG ID: {pubg_id}\n📦 **Товары:**\n{items_text}\n\n💰 **ИТОГО: {total}₽**"
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": ADMIN_ID,
                "text": admin_text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
            print(f"✅ Уведомление админу отправлено: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
    else:
        print("❌ BOT_TOKEN не установлен!")
    
    return jsonify({'ok': True, 'order_id': order_id})

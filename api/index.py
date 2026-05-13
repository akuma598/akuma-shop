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
    <title>Akuma UC BOT 24/7</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:#fff;padding:20px;}
        .container{max-width:600px;margin:0 auto;}
        .header{text-align:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px;}
        .header h1{font-size:24px;background:linear-gradient(135deg,#ffcc00,#ff9900);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .header p{color:#888;font-size:12px;margin-top:5px;}
        .tabs{display:flex;gap:10px;margin-bottom:20px;background:rgba(255,255,255,0.05);padding:5px;border-radius:12px;}
        .tab{flex:1;text-align:center;padding:12px;border-radius:10px;cursor:pointer;transition:all 0.3s;font-size:14px;font-weight:bold;}
        .tab.active{background:linear-gradient(135deg,#ffcc00,#ff9900);color:#1a1a2e;}
        .product-card{background:rgba(255,255,255,0.05);border-radius:16px;padding:16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;border:1px solid rgba(255,255,255,0.1);}
        .product-card:hover{background:rgba(255,255,255,0.1);border-color:#ffcc00;}
        .product-info h3{font-size:18px;margin-bottom:5px;}
        .product-info .price{color:#ffcc00;font-weight:bold;}
        .product-actions{display:flex;align-items:center;gap:15px;}
        .quantity-control{display:flex;align-items:center;gap:10px;}
        .quantity-btn{background:rgba(255,255,255,0.1);border:none;width:32px;height:32px;border-radius:8px;color:#fff;font-size:20px;cursor:pointer;}
        .quantity-btn:hover{background:#ffcc00;color:#1a1a2e;}
        .quantity{font-size:16px;font-weight:bold;min-width:30px;text-align:center;}
        .select-btn{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:8px 20px;border-radius:10px;color:#1a1a2e;font-weight:bold;cursor:pointer;}
        .cart-section{background:rgba(0,0,0,0.5);border-radius:16px;padding:20px;margin-top:20px;border:1px solid rgba(255,204,0,0.3);}
        .cart-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;}
        .cart-header h3{font-size:18px;}
        .clear-cart{background:rgba(255,0,0,0.2);border:1px solid #ff4444;color:#ff4444;padding:8px 15px;border-radius:10px;cursor:pointer;font-size:14px;}
        .cart-item{display:flex;justify-content:space-between;margin-bottom:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.1);}
        .cart-total{margin-top:15px;padding-top:15px;border-top:1px solid rgba(255,255,255,0.2);font-size:18px;font-weight:bold;text-align:right;color:#ffcc00;}
        .pubg-section{background:rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin:20px 0;}
        .pubg-section input{width:100%;padding:14px;border:1px solid rgba(255,255,255,0.2);border-radius:12px;background:rgba(0,0,0,0.3);color:#fff;font-size:16px;outline:none;}
        .payment-methods{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:20px 0;}
        .payment-btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:15px;text-align:center;cursor:pointer;}
        .payment-btn.selected{border-color:#ffcc00;background:rgba(255,204,0,0.2);}
        .checkout-btn{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:16px;width:100%;border-radius:12px;color:#1a1a2e;font-size:18px;font-weight:bold;cursor:pointer;margin-top:20px;}
        .footer{text-align:center;padding:20px;font-size:12px;color:#666;border-top:1px solid rgba(255,255,255,0.1);margin-top:20px;}
        .footer a{color:#ffcc00;text-decoration:none;}
        .hide{display:none;}
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:1000;justify-content:center;align-items:center;}
        .modal-content{background:linear-gradient(135deg,#2e004d,#1a0033);border-radius:24px;padding:30px;text-align:center;border:2px solid #ffcc00;max-width:350px;margin:20px;}
        .modal-content h2{color:#ffcc00;margin-bottom:15px;}
        .modal-content .order-id{font-size:32px;font-weight:bold;color:#ffcc00;margin:15px 0;}
        .modal-content .total{font-size:28px;color:#ffcc00;font-weight:bold;}
        .modal-btn{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:12px 30px;border-radius:12px;color:#1a0033;font-weight:bold;cursor:pointer;margin-top:20px;width:100%;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Akuma UC BOT 24/7</h1>
            <p>Быстрая покупка UC | 24/7 | Мгновенная выдача</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" data-tab="uc">UC</div>
            <div class="tab" data-tab="pp">Популярность</div>
            <div class="tab" data-tab="prime">Подписки</div>
            <div class="tab" data-tab="costumes">X-костюмы</div>
        </div>
        
        <div id="uc-products" class="products-list"></div>
        <div id="pp-products" class="products-list hide"></div>
        <div id="prime-products" class="products-list hide"></div>
        <div id="costumes-products" class="products-list hide"></div>
        
        <div class="cart-section">
            <div class="cart-header">
                <h3>🛒 Корзина</h3>
                <button class="clear-cart" onclick="clearCart()">Очистить</button>
            </div>
            <div id="cart-items"></div>
            <div id="cart-total" class="cart-total">Итого: 0 ₽</div>
        </div>
        
        <div class="pubg-section">
            <input type="number" id="pubg_id" placeholder="Введите PUBG ID получателя (начинается с 5)">
        </div>
        
        <div class="payment-methods">
            <div class="payment-btn" onclick="selectPayment('sbp1')" data-method="sbp1">💳 СБП №1</div>
            <div class="payment-btn" onclick="selectPayment('sbp2')" data-method="sbp2">💳 СБП №2</div>
            <div class="payment-btn" onclick="selectPayment('card1')" data-method="card1">💳 Карта №1</div>
            <div class="payment-btn" onclick="selectPayment('card2')" data-method="card2">💳 Карта №2</div>
        </div>
        
        <button class="checkout-btn" onclick="checkout()">Купить</button>
        
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
            <button class="modal-btn" onclick="window.location.href='https://t.me/akuma_ucbot'">📱 Перейти в бота</button>
        </div>
    </div>
    
    <script>
        // UC ТОВАРЫ
        const ucProducts = {
            "60": {name: "60 UC", price: 87},
            "120": {name: "120 UC", price: 152},
            "180": {name: "180 UC", price: 223},
            "240": {name: "240 UC", price: 293},
            "325": {name: "325 UC", price: 387},
            "385": {name: "385 UC", price: 434},
            "445": {name: "445 UC", price: 482},
            "660": {name: "660 UC", price: 756},
            "720": {name: "720 UC", price: 771},
            "985": {name: "985 UC", price: 1049},
            "1320": {name: "1320 UC", price: 1401},
            "1800": {name: "1800 UC", price: 1891},
            "3850": {name: "3850 UC", price: 3753},
            "8100": {name: "8100 UC", price: 7243},
            "9900": {name: "9900 UC", price: 9790}
        };
        
        // ПП ТОВАРЫ
        const ppProducts = {
            "10000": {name: "10 000 ПП", price: 152},
            "20000": {name: "20 000 ПП", price: 289},
            "30000": {name: "30 000 ПП", price: 424},
            "40000": {name: "40 000 ПП", price: 561},
            "50000": {name: "50 000 ПП", price: 696},
            "60000": {name: "60 000 ПП", price: 833}
        };
        
        // PRIME ПОДПИСКИ
        const primeProducts = {
            "1m": {name: "Prime (1 месяц)", price: 125},
            "3m": {name: "Prime (3 месяца)", price: 318},
            "6m": {name: "Prime (6 месяцев)", price: 550},
            "12m": {name: "Prime (12 месяцев)", price: 1027}
        };
        
        // X-КОСТЮМЫ
        const costumesProducts = {
            "1": {name: "🐦‍⬛ Ворон", price: 4500},
            "2": {name: "🔥 Феникс", price: 4500}
        };
        
        let cart = JSON.parse(localStorage.getItem('cart')) || {};
        let selectedPayment = localStorage.getItem('selectedPayment') || null;
        
        function renderProducts(containerId, products, type) {
            const container = document.getElementById(containerId);
            if (!container) return;
            let html = '';
            for (const [key, product] of Object.entries(products)) {
                const qty = cart[key] ? cart[key].quantity : 0;
                if (type === 'uc') {
                    html += '<div class="product-card">' +
                        '<div class="product-info"><h3>' + product.name + '</h3><div class="price">' + product.price + ' ₽</div></div>' +
                        '<div class="product-actions">' +
                            '<div class="quantity-control">' +
                                '<button class="quantity-btn" onclick="updateQuantity(\'' + key + '\', -1)">-</button>' +
                                '<span class="quantity">' + qty + '</span>' +
                                '<button class="quantity-btn" onclick="updateQuantity(\'' + key + '\', 1)">+</button>' +
                            '</div>' +
                        '</div>' +
                    '</div>';
                } else {
                    html += '<div class="product-card">' +
                        '<div class="product-info"><h3>' + product.name + '</h3><div class="price">' + product.price + ' ₽</div></div>' +
                        '<div class="product-actions"><button class="select-btn" onclick="addToCart(\'' + key + '\', \'' + product.name + '\', ' + product.price + ')">Выбрать</button></div>' +
                    '</div>';
                }
            }
            container.innerHTML = html;
        }
        
        function updateQuantity(key, delta) {
            if (!cart[key]) cart[key] = {name: ucProducts[key].name, price: ucProducts[key].price, quantity: 0};
            let newQty = cart[key].quantity + delta;
            if (newQty <= 0) delete cart[key];
            else cart[key].quantity = newQty;
            saveCart();
            updateCartDisplay();
            renderProducts('uc-products', ucProducts, 'uc');
        }
        
        function addToCart(key, name, price) {
            if (!cart[key]) cart[key] = {name: name, price: price, quantity: 0};
            cart[key].quantity++;
            saveCart();
            updateCartDisplay();
            alert('✅ ' + name + ' добавлен в корзину');
        }
        
        function updateCartDisplay() {
            let total = 0;
            let html = '';
            for (const [key, item] of Object.entries(cart)) {
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                html += '<div class="cart-item"><span>' + item.name + ' x' + item.quantity + '</span><span>' + itemTotal + ' ₽</span></div>';
            }
            document.getElementById('cart-items').innerHTML = Object.keys(cart).length === 0 ? '<div style="text-align:center;color:#888;">Корзина пуста</div>' : html;
            document.getElementById('cart-total').innerHTML = 'Итого: ' + total + ' ₽';
        }
        
        function clearCart() {
            cart = {};
            saveCart();
            updateCartDisplay();
            renderProducts('uc-products', ucProducts, 'uc');
            alert('🗑 Корзина очищена');
        }
        
        function saveCart() {
            localStorage.setItem('cart', JSON.stringify(cart));
            if (selectedPayment) localStorage.setItem('selectedPayment', selectedPayment);
        }
        
        function selectPayment(method) {
            selectedPayment = method;
            saveCart();
            document.querySelectorAll('.payment-btn').forEach(btn => btn.classList.remove('selected'));
            document.querySelector(`.payment-btn[data-method="${method}"]`).classList.add('selected');
        }
        
        let currentTab = 'uc';
        
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab[data-tab="${tab}"]`).classList.add('active');
            document.getElementById('uc-products').classList.add('hide');
            document.getElementById('pp-products').classList.add('hide');
            document.getElementById('prime-products').classList.add('hide');
            document.getElementById('costumes-products').classList.add('hide');
            document.getElementById(`${tab}-products`).classList.remove('hide');
            
            if (tab === 'uc') renderProducts('uc-products', ucProducts, 'uc');
            if (tab === 'pp') renderProducts('pp-products', ppProducts, 'pp');
            if (tab === 'prime') renderProducts('prime-products', primeProducts, 'prime');
            if (tab === 'costumes') renderProducts('costumes-products', costumesProducts, 'costumes');
        }
        
        function showOrderModal(orderId, total) {
            document.getElementById('modalOrderId').innerText = '#' + orderId;
            document.getElementById('modalTotal').innerText = total + ' ₽';
            document.getElementById('orderModal').style.display = 'flex';
        }
        
        async function checkout() {
            const pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) { alert('❌ Введите PUBG ID'); return; }
            if (!pubgId.toString().startsWith('5') || pubgId.toString().length < 10) { alert('❌ PUBG ID должен начинаться с 5 (10+ цифр)'); return; }
            if (Object.keys(cart).length === 0) { alert('❌ Корзина пуста'); return; }
            if (!selectedPayment) { alert('❌ Выберите способ оплаты'); return; }
            
            let total = 0;
            for (const item of Object.values(cart)) total += item.price * item.quantity;
            
            try {
                const response = await fetch('/create-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({pubg_id: pubgId, items: cart, total: total, payment_method: selectedPayment})
                });
                const data = await response.json();
                if (data.ok && data.order_id) {
                    showOrderModal(data.order_id, total);
                    cart = {};
                    saveCart();
                    updateCartDisplay();
                    renderProducts('uc-products', ucProducts, 'uc');
                    selectedPayment = null;
                    document.querySelectorAll('.payment-btn').forEach(btn => btn.classList.remove('selected'));
                } else {
                    alert('❌ Ошибка при создании заказа');
                }
            } catch (error) {
                alert('❌ Ошибка сервера');
            }
        }
        
        // Запуск
        const urlParams = new URLSearchParams(window.location.search);
        const section = urlParams.get('section');
        if (section === 'uc') switchTab('uc');
        else if (section === 'pp') switchTab('pp');
        else if (section === 'prime') switchTab('prime');
        else if (section === 'costumes') switchTab('costumes');
        else switchTab('uc');
        
        if (selectedPayment) {
            const btn = document.querySelector(`.payment-btn[data-method="${selectedPayment}"]`);
            if (btn) btn.classList.add('selected');
        }
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
    payment_method = data.get('payment_method')
    
    print(f"📥 НОВЫЙ ЗАКАЗ: pubg_id={pubg_id}, total={total}, payment={payment_method}")
    
    if not pubg_id or not items:
        return jsonify({'error': 'Missing data'}), 400
    
    order_id = order_counter
    order_counter += 1
    
    temp_orders[order_id] = {
        'pubg_id': pubg_id,
        'items': items,
        'total': total,
        'payment_method': payment_method,
        'status': 'pending',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if BOT_TOKEN:
        try:
            items_text = '\n'.join([f"• {item['name']} x{item['quantity']} = {item['price'] * item['quantity']}₽" for item in items.values()])
            admin_text = f"🆕 **НОВЫЙ ЗАКАЗ С САЙТА**\n\n🆔 #{order_id}\n🎮 PUBG ID: {pubg_id}\n📦 **Товары:**\n{items_text}\n\n💰 **ИТОГО: {total}₽**\n💳 Оплата: {payment_method}"
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": ADMIN_ID,
                "text": admin_text,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload)
            print(f"✅ Уведомление админу отправлено")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    return jsonify({'ok': True, 'order_id': order_id})

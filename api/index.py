from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akuma UC Shop</title>
    <style>
        body {
            font-family: Arial;
            background: #1a1a2e;
            color: #fff;
            padding: 20px;
        }
        .product {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .price {
            color: #ffcc00;
        }
        .tab {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            background: #333;
            border-radius: 10px;
            cursor: pointer;
        }
        .tab.active {
            background: #ffcc00;
            color: #1a1a2e;
        }
        button {
            background: #ffcc00;
            color: #1a1a2e;
            border: none;
            padding: 8px 15px;
            border-radius: 8px;
            cursor: pointer;
        }
        .qty-btn {
            background: #333;
            color: #fff;
            width: 30px;
            height: 30px;
            padding: 0;
        }
        .cart-item {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
        }
        .checkout {
            background: #ffcc00;
            color: #1a1a2e;
            padding: 16px;
            width: 100%;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 18px;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            border: none;
            margin: 10px 0;
        }
        .cart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
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
            background: #2e004d;
            border-radius: 24px;
            padding: 30px;
            text-align: center;
            border: 2px solid #ffcc00;
            max-width: 350px;
        }
        .modal-content h2 {
            color: #ffcc00;
        }
        .modal-order-id {
            font-size: 32px;
            font-weight: bold;
            color: #ffcc00;
            margin: 15px 0;
        }
        .modal-total {
            font-size: 28px;
            color: #ffcc00;
            font-weight: bold;
        }
        .modal-btn {
            background: #ffcc00;
            border: none;
            padding: 12px 30px;
            border-radius: 12px;
            color: #1a0033;
            font-weight: bold;
            margin-top: 20px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>🔥 Akuma UC BOT 24/7</h1>
    <p>Быстрая покупка UC | 24/7 | Мгновенная выдача</p>
    
    <div id="tabs">
        <div class="tab active" onclick="showTab('uc')">UC</div>
        <div class="tab" onclick="showTab('pp')">Популярность</div>
        <div class="tab" onclick="showTab('prime')">Подписки</div>
        <div class="tab" onclick="showTab('costumes')">X-костюмы</div>
    </div>
    
    <div id="products" style="margin-top:20px;"></div>
    
    <div style="margin-top:20px;background:rgba(0,0,0,0.5);padding:20px;border-radius:10px;">
        <div class="cart-header">
            <h3>🛒 Корзина</h3>
            <button onclick="clearCart()">Очистить</button>
        </div>
        <div id="cart"></div>
        <div id="total" style="text-align:right;margin-top:15px;font-size:18px;font-weight:bold;color:#ffcc00;">Итого: 0 ₽</div>
    </div>
    
    <input type="number" id="pubg_id" placeholder="Введите PUBG ID получателя (начинается с 5)">
    
    <button class="checkout" onclick="checkout()">Купить</button>
    
    <div id="orderModal" class="modal">
        <div class="modal-content">
            <h2>✅ ЗАКАЗ ПРИНЯТ!</h2>
            <div class="modal-order-id" id="modalOrderId">#0</div>
            <p>на сумму</p>
            <div class="modal-total" id="modalTotal">0 ₽</div>
            <button class="modal-btn" onclick="window.location.href='https://t.me/akuma_ucbot'">📱 Перейти в бота</button>
        </div>
    </div>
    
    <script>
        // ВСЕ ТОВАРЫ
        var allProducts = {
            uc: [
                ["60 UC", 87], ["120 UC", 152], ["180 UC", 223], ["240 UC", 293],
                ["325 UC", 387], ["385 UC", 434], ["445 UC", 482], ["660 UC", 756],
                ["720 UC", 771], ["985 UC", 1049], ["1320 UC", 1401], ["1800 UC", 1891],
                ["3850 UC", 3753], ["8100 UC", 7243], ["9900 UC", 9790]
            ],
            pp: [
                ["10 000 ПП", 152], ["20 000 ПП", 289], ["30 000 ПП", 424],
                ["40 000 ПП", 561], ["50 000 ПП", 696], ["60 000 ПП", 833]
            ],
            prime: [
                ["Prime (1 месяц)", 125], ["Prime (3 месяца)", 318],
                ["Prime (6 месяцев)", 550], ["Prime (12 месяцев)", 1027]
            ],
            costumes: [
                ["🐦‍⬛ Ворон", 4500], ["🔥 Феникс", 4500]
            ]
        };
        
        var cart = {};
        var currentTab = 'uc';
        
        function showTab(tab) {
            currentTab = tab;
            var tabs = document.querySelectorAll('.tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            event.target.classList.add('active');
            renderProducts();
        }
        
        function renderProducts() {
            var container = document.getElementById('products');
            var products = allProducts[currentTab];
            var html = '';
            
            for (var i = 0; i < products.length; i++) {
                var name = products[i][0];
                var price = products[i][1];
                var key = name.replace(/ /g, '_');
                var qty = cart[key] ? cart[key].qty : 0;
                
                if (currentTab === 'uc') {
                    html += '<div class="product">' +
                        '<div><strong>' + name + '</strong><br><span class="price">' + price + ' ₽</span></div>' +
                        '<div>' +
                            '<button class="qty-btn" onclick="updateQty(\'' + key + '\', \'' + name + '\', ' + price + ', -1)">-</button> ' +
                            '<span style="min-width:40px;display:inline-block;text-align:center;">' + qty + '</span> ' +
                            '<button class="qty-btn" onclick="updateQty(\'' + key + '\', \'' + name + '\', ' + price + ', 1)" style="background:#ffcc00;color:#1a1a2e;">+</button>' +
                        '</div>' +
                    '</div>';
                } else {
                    html += '<div class="product">' +
                        '<div><strong>' + name + '</strong><br><span class="price">' + price + ' ₽</span></div>' +
                        '<div><button onclick="addToCart(\'' + key + '\', \'' + name + '\', ' + price + ')">Выбрать</button></div>' +
                    '</div>';
                }
            }
            container.innerHTML = html;
        }
        
        function updateQty(key, name, price, delta) {
            if (!cart[key]) cart[key] = {name: name, price: price, qty: 0};
            var newQty = cart[key].qty + delta;
            if (newQty <= 0) {
                delete cart[key];
            } else {
                cart[key].qty = newQty;
            }
            saveCart();
            updateCartDisplay();
            renderProducts();
        }
        
        function addToCart(key, name, price) {
            if (!cart[key]) cart[key] = {name: name, price: price, qty: 0};
            cart[key].qty++;
            saveCart();
            updateCartDisplay();
            alert('✅ ' + name + ' добавлен в корзину');
        }
        
        function updateCartDisplay() {
            var total = 0;
            var html = '';
            for (var key in cart) {
                var item = cart[key];
                var itemTotal = item.price * item.qty;
                total += itemTotal;
                html += '<div class="cart-item"><span>' + item.name + ' x' + item.qty + '</span><span>' + itemTotal + ' ₽</span></div>';
            }
            document.getElementById('cart').innerHTML = Object.keys(cart).length === 0 ? '<div style="text-align:center;color:#888;">Корзина пуста</div>' : html;
            document.getElementById('total').innerHTML = 'Итого: ' + total + ' ₽';
        }
        
        function clearCart() {
            cart = {};
            saveCart();
            updateCartDisplay();
            renderProducts();
            alert('🗑 Корзина очищена');
        }
        
        function saveCart() {
            localStorage.setItem('cart', JSON.stringify(cart));
        }
        
        function showOrderModal(orderId, total) {
            var modal = document.getElementById('orderModal');
            document.getElementById('modalOrderId').innerHTML = '#' + orderId;
            document.getElementById('modalTotal').innerHTML = total + ' ₽';
            modal.style.display = 'flex';
        }
        
        async function checkout() {
            var pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) { alert('Введите PUBG ID'); return; }
            if (!pubgId.toString().startsWith('5') || pubgId.length < 10) { alert('PUBG ID должен начинаться с 5 (10+ цифр)'); return; }
            if (Object.keys(cart).length === 0) { alert('Корзина пуста'); return; }
            
            var total = 0;
            for (var key in cart) total += cart[key].price * cart[key].qty;
            
            try {
                var response = await fetch('/create-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({pubg_id: pubgId, items: cart, total: total})
                });
                var data = await response.json();
                if (data.ok && data.order_id) {
                    showOrderModal(data.order_id, total);
                    cart = {};
                    saveCart();
                    updateCartDisplay();
                    renderProducts();
                } else {
                    alert('Ошибка при создании заказа');
                }
            } catch(e) {
                alert('Ошибка сервера');
            }
        }
        
        renderProducts();
        updateCartDisplay();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

@app.route('/create-order', methods=['POST'])
def create_order():
    import json
    import requests
    data = request.json
    print("📥 НОВЫЙ ЗАКАЗ:", data)
    
    # Уведомление админу
    bot_token = os.environ.get("BOT_TOKEN")
    admin_id = os.environ.get("ADMIN_ID", "8504217011")
    
    if bot_token:
        try:
            items_text = ''
            for key, item in data['items'].items():
                items_text += f"• {item['name']} x{item['qty']} = {item['price'] * item['qty']}₽\n"
            
            admin_text = f"🆕 **НОВЫЙ ЗАКАЗ С САЙТА**\n\n🎮 PUBG ID: {data['pubg_id']}\n📦 **Товары:**\n{items_text}\n💰 **ИТОГО: {data['total']}₽**"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": admin_id, "text": admin_text, "parse_mode": "Markdown"})
            print("✅ Уведомление отправлено")
        except Exception as e:
            print("❌ Ошибка:", e)
    
    return jsonify({'ok': True, 'order_id': 1})

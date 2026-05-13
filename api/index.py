from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akuma UC Shop</title>
    <style>
        body{font-family:Arial;background:#1a1a2e;color:#fff;padding:20px;}
        .product{background:rgba(255,255,255,0.1);padding:15px;margin:10px 0;border-radius:10px;display:flex;justify-content:space-between;align-items:center;}
        .price{color:#ffcc00;}
        .tab{display:inline-block;padding:10px 20px;margin:5px;background:#333;border-radius:10px;cursor:pointer;}
        .tab.active{background:#ffcc00;color:#1a1a2e;}
        .cart-item{background:rgba(255,255,255,0.05);padding:10px;margin:5px 0;border-radius:8px;display:flex;justify-content:space-between;}
        button{background:#ffcc00;color:#1a1a2e;border:none;padding:8px 15px;border-radius:8px;cursor:pointer;}
        .qty-btn{background:#333;color:#fff;width:30px;height:30px;padding:0;}
        .checkout{background:#ffcc00;color:#1a1a2e;padding:16px;width:100%;border-radius:10px;margin-top:20px;font-size:18px;font-weight:bold;}
        input{width:100%;padding:14px;border-radius:10px;border:none;margin:10px 0;}
        .cart-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
    </style>
</head>
<body>
    <h1>🔥 Akuma UC BOT 24/7</h1>
    <p>Быстрая покупка UC | 24/7 | Мгновенная выдача</p>
    
    <div>
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
    
    <div class="modal" id="orderModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:1000;justify-content:center;align-items:center;">
        <div style="background:#2e004d;border-radius:24px;padding:30px;text-align:center;border:2px solid #ffcc00;max-width:350px;">
            <h2 style="color:#ffcc00;">✅ ЗАКАЗ ПРИНЯТ!</h2>
            <div id="modalOrderId" style="font-size:32px;font-weight:bold;color:#ffcc00;margin:15px 0;">#0</div>
            <p>на сумму</p>
            <div id="modalTotal" style="font-size:28px;color:#ffcc00;font-weight:bold;">0 ₽</div>
            <button onclick="window.location.href='https://t.me/akuma_ucbot'" style="background:#ffcc00;border:none;padding:12px 30px;border-radius:12px;color:#1a0033;font-weight:bold;margin-top:20px;width:100%;">📱 Перейти в бота</button>
        </div>
    </div>
    
    <script>
        // ТОВАРЫ
        var products = {
            uc: {
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
            },
            pp: {
                "10000": {name: "10 000 ПП", price: 152},
                "20000": {name: "20 000 ПП", price: 289},
                "30000": {name: "30 000 ПП", price: 424},
                "40000": {name: "40 000 ПП", price: 561},
                "50000": {name: "50 000 ПП", price: 696},
                "60000": {name: "60 000 ПП", price: 833}
            },
            prime: {
                "1m": {name: "Prime (1 месяц)", price: 125},
                "3m": {name: "Prime (3 месяца)", price: 318},
                "6m": {name: "Prime (6 месяцев)", price: 550},
                "12m": {name: "Prime (12 месяцев)", price: 1027}
            },
            costumes: {
                "1": {name: "🐦‍⬛ Ворон", price: 4500},
                "2": {name: "🔥 Феникс", price: 4500}
            }
        };
        
        var cart = JSON.parse(localStorage.getItem('cart')) || {};
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
            var productList = products[currentTab];
            var html = '';
            
            for (var key in productList) {
                var p = productList[key];
                var qty = cart[key] ? cart[key].quantity : 0;
                
                if (currentTab === 'uc') {
                    html += '<div class="product">' +
                        '<div><strong>' + p.name + '</strong><br><span class="price">' + p.price + ' ₽</span></div>' +
                        '<div>' +
                            '<button class="qty-btn" onclick="updateQty(\'' + key + '\', -1)">-</button> ' +
                            '<span style="min-width:40px;display:inline-block;text-align:center;">' + qty + '</span> ' +
                            '<button class="qty-btn" onclick="updateQty(\'' + key + '\', 1)" style="background:#ffcc00;color:#1a1a2e;">+</button>' +
                        '</div>' +
                    '</div>';
                } else {
                    html += '<div class="product">' +
                        '<div><strong>' + p.name + '</strong><br><span class="price">' + p.price + ' ₽</span></div>' +
                        '<div><button onclick="addToCart(\'' + key + '\', \'' + p.name + '\', ' + p.price + ')">Выбрать</button></div>' +
                    '</div>';
                }
            }
            container.innerHTML = html;
        }
        
        function updateQty(key, delta) {
            if (!cart[key]) cart[key] = {name: products.uc[key].name, price: products.uc[key].price, quantity: 0};
            var newQty = cart[key].quantity + delta;
            if (newQty <= 0) {
                delete cart[key];
            } else {
                cart[key].quantity = newQty;
            }
            saveCart();
            updateCartDisplay();
            renderProducts();
        }
        
        function addToCart(key, name, price) {
            if (!cart[key]) cart[key] = {name: name, price: price, quantity: 0};
            cart[key].quantity++;
            saveCart();
            updateCartDisplay();
            alert('✅ ' + name + ' добавлен в корзину');
        }
        
        function updateCartDisplay() {
            var total = 0;
            var html = '';
            for (var key in cart) {
                var item = cart[key];
                var itemTotal = item.price * item.quantity;
                total += itemTotal;
                html += '<div class="cart-item"><span>' + item.name + ' x' + item.quantity + '</span><span>' + itemTotal + ' ₽</span></div>';
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
            document.getElementById('modalOrderId').innerText = '#' + orderId;
            document.getElementById('modalTotal').innerText = total + ' ₽';
            modal.style.display = 'flex';
        }
        
        async function checkout() {
            var pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) { alert('❌ Введите PUBG ID'); return; }
            if (!pubgId.toString().startsWith('5') || pubgId.length < 10) { alert('❌ PUBG ID должен начинаться с 5 (10+ цифр)'); return; }
            if (Object.keys(cart).length === 0) { alert('❌ Корзина пуста'); return; }
            
            var total = 0;
            for (var key in cart) total += cart[key].price * cart[key].quantity;
            
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
                    alert('❌ Ошибка при создании заказа');
                }
            } catch(e) {
                alert('❌ Ошибка сервера');
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
    data = request.json
    print("НОВЫЙ ЗАКАЗ:", data)
    
    # Отправляем уведомление админу
    bot_token = os.environ.get("BOT_TOKEN")
    admin_id = os.environ.get("ADMIN_ID", "8504217011")
    
    if bot_token:
        try:
            items_text = '\n'.join([f"• {item['name']} x{item['quantity']} = {item['price'] * item['quantity']}₽" for item in data['items'].values()])
            admin_text = f"🆕 **НОВЫЙ ЗАКАЗ С САЙТА**\n\n🎮 PUBG ID: {data['pubg_id']}\n📦 **Товары:**\n{items_text}\n\n💰 **ИТОГО: {data['total']}₽**"
            
            import requests
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": admin_id, "text": admin_text, "parse_mode": "Markdown"})
        except Exception as e:
            print("Ошибка отправки:", e)
    
    return jsonify({'ok': True, 'order_id': 1})

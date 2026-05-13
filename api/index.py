from flask import Flask, request, jsonify
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "akuma_ucbot")
ADMIN_ID = os.environ.get("ADMIN_ID", "8504217011")

temp_orders = {}
order_counter = 1

# Прямые ссылки на картинки (ImgBB)
UC_IMAGE = "https://i.ibb.co/PHd6LDM/uc.jpg"
PP_IMAGE = "https://i.ibb.co/zTkCcsbX/pp.jpg"
PRIME_IMAGE = "https://i.ibb.co/8np0w8bN/prime.jpg"
COSTUME1_IMAGE = "https://i.ibb.co/zH4pfW3y/costume1.jpg"
COSTUME2_IMAGE = "https://i.ibb.co/RTj8grp4/costume2.jpg"

HTML = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>NeoN UC BOT 24/7</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(135deg,#4a0080,#2e004d,#1a0033);min-height:100vh;color:#fff;padding:20px;}}
        .container{{max-width:600px;margin:0 auto;}}
        .header{{text-align:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px;}}
        .header h1{{font-size:24px;background:linear-gradient(135deg,#ffcc00,#ff9900);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
        .header p{{color:#b87dff;font-size:12px;margin-top:5px;}}
        .tabs{{display:flex;gap:10px;margin-bottom:20px;background:rgba(255,255,255,0.05);padding:5px;border-radius:12px;}}
        .tab{{flex:1;text-align:center;padding:12px;border-radius:10px;cursor:pointer;transition:all 0.3s;font-size:14px;font-weight:bold;}}
        .tab.active{{background:linear-gradient(135deg,#ffcc00,#ff9900);color:#1a0033;}}
        .product-card{{background:rgba(255,255,255,0.05);border-radius:16px;padding:16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;border:1px solid rgba(255,255,255,0.1);backdrop-filter:blur(10px);}}
        .product-card:hover{{background:rgba(255,255,255,0.1);border-color:#ffcc00;}}
        .product-info{{display:flex;align-items:center;gap:15px;}}
        .product-icon{{width:50px;height:50px;border-radius:12px;object-fit:cover;}}
        .product-details h3{{font-size:18px;margin-bottom:5px;}}
        .product-details .price{{color:#ffcc00;font-weight:bold;}}
        .buy-btn,.select-btn{{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:8px 20px;border-radius:10px;color:#1a0033;font-weight:bold;cursor:pointer;font-size:14px;}}
        .buy-btn:hover,.select-btn:hover{{opacity:0.9;}}
        .cart-section{{background:rgba(0,0,0,0.5);border-radius:16px;padding:20px;margin-top:20px;border:1px solid rgba(255,204,0,0.3);}}
        .cart-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;}}
        .cart-header h3{{font-size:18px;}}
        .clear-cart{{background:rgba(255,0,0,0.2);border:1px solid #ff4444;color:#ff4444;padding:8px 15px;border-radius:10px;cursor:pointer;font-size:14px;}}
        .clear-cart:hover{{background:rgba(255,0,0,0.3);}}
        .cart-item{{display:flex;justify-content:space-between;margin-bottom:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.1);}}
        .cart-total{{margin-top:15px;padding-top:15px;border-top:1px solid rgba(255,255,255,0.2);font-size:18px;font-weight:bold;text-align:right;color:#ffcc00;}}
        .pubg-section{{background:rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin:20px 0;}}
        .pubg-section input{{width:100%;padding:14px;border:1px solid rgba(255,255,255,0.2);border-radius:12px;background:rgba(0,0,0,0.3);color:#fff;font-size:16px;outline:none;}}
        .pubg-section input:focus{{border-color:#ffcc00;}}
        .payment-methods{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:20px 0;}}
        .payment-btn{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:15px;text-align:center;cursor:pointer;transition:all 0.2s;}}
        .payment-btn:hover,.payment-btn.selected{{border-color:#ffcc00;background:rgba(255,204,0,0.1);}}
        .payment-btn.selected{{border-color:#ffcc00;background:rgba(255,204,0,0.2);}}
        .payment-btn .method-name{{font-weight:bold;margin-bottom:5px;}}
        .payment-btn .method-desc{{font-size:11px;color:#b87dff;}}
        .checkout-btn{{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:16px;width:100%;border-radius:12px;color:#1a0033;font-size:18px;font-weight:bold;cursor:pointer;margin-top:20px;}}
        .checkout-btn:hover{{opacity:0.9;}}
        .footer{{text-align:center;padding:20px;font-size:12px;color:#b87dff;border-top:1px solid rgba(255,255,255,0.1);margin-top:20px;}}
        .footer a{{color:#ffcc00;text-decoration:none;}}
        .hide{{display:none;}}
        
        .modal {{
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
        }}
        .modal-content {{
            background: linear-gradient(135deg, #2e004d, #1a0033);
            border-radius: 24px;
            padding: 30px;
            text-align: center;
            border: 2px solid #ffcc00;
            max-width: 350px;
            margin: 20px;
        }}
        .modal-content h2 {{
            color: #ffcc00;
            margin-bottom: 15px;
            font-size: 24px;
        }}
        .modal-content p {{
            margin: 10px 0;
            font-size: 16px;
        }}
        .modal-content .order-id {{
            font-size: 32px;
            font-weight: bold;
            color: #ffcc00;
            margin: 15px 0;
        }}
        .modal-content .total {{
            font-size: 28px;
            color: #ffcc00;
            font-weight: bold;
        }}
        .modal-btn {{
            background: linear-gradient(135deg,#ffcc00,#ff9900);
            border: none;
            padding: 12px 30px;
            border-radius: 12px;
            color: #1a0033;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            font-size: 16px;
            width: 100%;
        }}
        .modal-btn:hover {{
            opacity: 0.9;
        }}
        .copy-btn {{
            background: rgba(255,255,255,0.1);
            border: 1px solid #ffcc00;
            padding: 8px 20px;
            border-radius: 10px;
            color: #ffcc00;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Akuma UC BOT 24/7</h1>
            <p>Быстрая покупка UC | 24/7 | Мгновенная выдача</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('uc')">UC</div>
            <div class="tab" onclick="switchTab('pp')">Популярность</div>
            <div class="tab" onclick="switchTab('prime')">Подписки</div>
            <div class="tab" onclick="switchTab('costumes')">X-костюмы</div>
        </div>
        
        <div id="tab-uc"><div id="uc-products"></div></div>
        <div id="tab-pp" class="hide"><div id="pp-products"></div></div>
        <div id="tab-prime" class="hide"><div id="prime-products"></div></div>
        <div id="tab-costumes" class="hide"><div id="costumes-products"></div></div>
        
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
            <div class="payment-btn" onclick="selectPayment('sbp1')" data-method="sbp1">
                <div class="method-name">💳 СБП №1</div>
                <div class="method-desc">система быстрых платежей</div>
            </div>
            <div class="payment-btn" onclick="selectPayment('sbp2')" data-method="sbp2">
                <div class="method-name">💳 СБП №2</div>
                <div class="method-desc">система быстрых платежей</div>
            </div>
            <div class="payment-btn" onclick="selectPayment('card1')" data-method="card1">
                <div class="method-name">💳 Карта №1</div>
                <div class="method-desc">МИР VISA Mastercard</div>
            </div>
            <div class="payment-btn" onclick="selectPayment('card2')" data-method="card2">
                <div class="method-name">💳 Карта №2</div>
                <div class="method-desc">МИР VISA Mastercard</div>
            </div>
        </div>
        
        <button class="checkout-btn" onclick="checkout()">Купить</button>
        
        <div class="footer">
            <p>Вопросы: <a href="https://t.me/aakumma">@aakumma</a></p>
        </div>
    </div>
    
    <div id="orderModal" class="modal">
        <div class="modal-content">
            <h2>✅ ЗАКАЗ ПРИНЯТ!</h2>
            <p>Ваш заказ успешно оформлен</p>
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
        const ucProducts = {{
            "60": {{"name": "60 UC", "price": 87, "icon": "{UC_IMAGE}"}},
            "120": {{"name": "120 UC", "price": 152, "icon": "{UC_IMAGE}"}},
            "180": {{"name": "180 UC", "price": 223, "icon": "{UC_IMAGE}"}},
            "240": {{"name": "240 UC", "price": 293, "icon": "{UC_IMAGE}"}},
            "325": {{"name": "325 UC", "price": 387, "icon": "{UC_IMAGE}"}},
            "385": {{"name": "385 UC", "price": 434, "icon": "{UC_IMAGE}"}},
            "445": {{"name": "445 UC", "price": 482, "icon": "{UC_IMAGE}"}},
            "660": {{"name": "660 UC", "price": 756, "icon": "{UC_IMAGE}"}},
            "720": {{"name": "720 UC", "price": 771, "icon": "{UC_IMAGE}"}},
            "985": {{"name": "985 UC", "price": 1049, "icon": "{UC_IMAGE}"}},
            "1320": {{"name": "1320 UC", "price": 1401, "icon": "{UC_IMAGE}"}},
            "1800": {{"name": "1800 UC", "price": 1891, "icon": "{UC_IMAGE}"}},
            "3850": {{"name": "3850 UC", "price": 3753, "icon": "{UC_IMAGE}"}},
            "8100": {{"name": "8100 UC", "price": 7243, "icon": "{UC_IMAGE}"}},
            "9900": {{"name": "9900 UC", "price": 9790, "icon": "{UC_IMAGE}"}}
        }};
        
        const ppProducts = {{
            "10000": {{"name": "10 000 ПП", "price": 152, "icon": "{PP_IMAGE}"}},
            "20000": {{"name": "20 000 ПП", "price": 289, "icon": "{PP_IMAGE}"}},
            "30000": {{"name": "30 000 ПП", "price": 424, "icon": "{PP_IMAGE}"}},
            "40000": {{"name": "40 000 ПП", "price": 561, "icon": "{PP_IMAGE}"}},
            "50000": {{"name": "50 000 ПП", "price": 696, "icon": "{PP_IMAGE}"}},
            "60000": {{"name": "60 000 ПП", "price": 833, "icon": "{PP_IMAGE}"}}
        }};
        
        const primeProducts = {{
            "1m": {{"name": "Prime (1 месяц)", "price": 125, "icon": "{PRIME_IMAGE}"}},
            "3m": {{"name": "Prime (3 месяца)", "price": 318, "icon": "{PRIME_IMAGE}"}},
            "6m": {{"name": "Prime (6 месяцев)", "price": 550, "icon": "{PRIME_IMAGE}"}},
            "12m": {{"name": "Prime (12 месяцев)", "price": 1027, "icon": "{PRIME_IMAGE}"}}
        }};
        
        const costumesProducts = {{
            "1": {{"name": "🐦‍⬛ Ворон", "price": 4500, "icon": "{COSTUME1_IMAGE}"}},
            "2": {{"name": "🔥 Феникс", "price": 4500, "icon": "{COSTUME2_IMAGE}"}}
        }};
        
        const botUsername = "{BOT_USERNAME}";
        
        let cart = {{}};
        let selectedPayment = null;
        
        function renderUCProducts() {{
            const container = document.getElementById('uc-products');
            let html = '';
            for (const [key, product] of Object.entries(ucProducts)) {{
                html += '<div class="product-card">' +
                    '<div class="product-info">' +
                        '<img class="product-icon" src="' + product.icon + '" alt="icon">' +
                        '<div class="product-details">' +
                            '<h3>' + product.name + '</h3>' +
                            '<div class="price">' + product.price + ' ₽</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="product-actions"><button class="buy-btn" onclick="addToCart(\\'' + key + '\\', \\'' + product.name + '\\', ' + product.price + ')">Купить</button></div>' +
                '</div>';
            }}
            container.innerHTML = html;
        }}
        
        function renderPPProducts() {{
            const container = document.getElementById('pp-products');
            let html = '';
            for (const [key, product] of Object.entries(ppProducts)) {{
                html += '<div class="product-card">' +
                    '<div class="product-info">' +
                        '<img class="product-icon" src="' + product.icon + '" alt="icon">' +
                        '<div class="product-details">' +
                            '<h3>' + product.name + '</h3>' +
                            '<div class="price">' + product.price + ' ₽</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="product-actions"><button class="select-btn" onclick="addToCart(\\'' + key + '\\', \\'' + product.name + '\\', ' + product.price + ')">Выбрать</button></div>' +
                '</div>';
            }}
            container.innerHTML = html;
        }}
        
        function renderPrimeProducts() {{
            const container = document.getElementById('prime-products');
            let html = '';
            for (const [key, product] of Object.entries(primeProducts)) {{
                html += '<div class="product-card">' +
                    '<div class="product-info">' +
                        '<img class="product-icon" src="' + product.icon + '" alt="icon">' +
                        '<div class="product-details">' +
                            '<h3>' + product.name + '</h3>' +
                            '<div class="price">' + product.price + ' ₽</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="product-actions"><button class="select-btn" onclick="addToCart(\\'' + key + '\\', \\'' + product.name + '\\', ' + product.price + ')">Выбрать</button></div>' +
                '</div>';
            }}
            container.innerHTML = html;
        }}
        
        function renderCostumesProducts() {{
            const container = document.getElementById('costumes-products');
            let html = '';
            for (const [key, product] of Object.entries(costumesProducts)) {{
                html += '<div class="product-card">' +
                    '<div class="product-info">' +
                        '<img class="product-icon" src="' + product.icon + '" alt="icon">' +
                        '<div class="product-details">' +
                            '<h3>' + product.name + '</h3>' +
                            '<div class="price">' + product.price + ' ₽</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="product-actions"><button class="select-btn" onclick="addToCart(\\'' + key + '\\', \\'' + product.name + '\\', ' + product.price + ')">Выбрать</button></div>' +
                '</div>';
            }}
            container.innerHTML = html;
        }}
        
        function addToCart(key, name, price) {{
            if (!cart[key]) cart[key] = {{name: name, price: price, quantity: 0}};
            cart[key].quantity++;
            updateCartDisplay();
            alert('✅ ' + name + ' добавлен в корзину');
        }}
        
        function updateCartDisplay() {{
            const container = document.getElementById('cart-items');
            let total = 0;
            let html = '';
            for (const [key, item] of Object.entries(cart)) {{
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                html += '<div class="cart-item"><span>' + item.name + ' x' + item.quantity + '</span><span>' + itemTotal + ' ₽</span></div>';
            }}
            container.innerHTML = Object.keys(cart).length === 0 ? '<div style="text-align:center;color:#b87dff;">Корзина пуста</div>' : html;
            document.getElementById('cart-total').innerHTML = 'Итого: ' + total + ' ₽';
        }}
        
        function clearCart() {{
            cart = {{}};
            updateCartDisplay();
            alert('🗑 Корзина очищена');
        }}
        
        function selectPayment(method) {{
            selectedPayment = method;
            document.querySelectorAll('.payment-btn').forEach(btn => btn.classList.remove('selected'));
            document.querySelector(`.payment-btn[data-method="${{method}}"]`).classList.add('selected');
        }}
        
        function switchTab(tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab[onclick="switchTab('${{tab}}')"]`).classList.add('active');
            document.getElementById('tab-uc').classList.add('hide');
            document.getElementById('tab-pp').classList.add('hide');
            document.getElementById('tab-prime').classList.add('hide');
            document.getElementById('tab-costumes').classList.add('hide');
            document.getElementById(`tab-${{tab}}`).classList.remove('hide');
        }}
        
        function copyOrderId() {{
            const orderId = document.getElementById('modalOrderId').innerText;
            navigator.clipboard.writeText(orderId);
            alert('✅ Номер заказа скопирован: ' + orderId);
        }}
        
        function goToBot() {{
            // Закрываем текущее окно/вкладку
            window.close();
            
            // Открываем бота
            window.location.href = 'https://t.me/' + botUsername;
        }}
        
        function showOrderModal(orderId, total) {{
            const modal = document.getElementById('orderModal');
            document.getElementById('modalOrderId').innerText = '#' + orderId;
            document.getElementById('modalTotal').innerText = total + ' ₽';
            modal.style.display = 'flex';
        }}
        
        async function checkout() {{
            const pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) {{ alert('❌ Введите PUBG ID'); return; }}
            if (!pubgId.toString().startsWith('5') || pubgId.toString().length < 10) {{ alert('❌ PUBG ID должен начинаться с 5 (10+ цифр)'); return; }}
            if (Object.keys(cart).length === 0) {{ alert('❌ Корзина пуста'); return; }}
            if (!selectedPayment) {{ alert('❌ Выберите способ оплаты'); return; }}
            
            let total = 0;
            for (const item of Object.values(cart)) total += item.price * item.quantity;
            
            try {{
                const response = await fetch('/create-order', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{pubg_id: pubgId, items: cart, total: total, payment_method: selectedPayment}})
                }});
                const data = await response.json();
                if (data.ok && data.order_id) {{
                    showOrderModal(data.order_id, total);
                    cart = {{}};
                    updateCartDisplay();
                    selectedPayment = null;
                    document.querySelectorAll('.payment-btn').forEach(btn => btn.classList.remove('selected'));
                }} else {{
                    alert('❌ Ошибка при создании заказа');
                }}
            }} catch (error) {{
                alert('❌ Ошибка сервера');
            }}
        }}
        
        renderUCProducts();
        renderPPProducts();
        renderPrimeProducts();
        renderCostumesProducts();
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
    payment_method = data.get('payment_method')
    
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
        except Exception as e:
            print(f"Ошибка: {e}")
    
    return jsonify({'ok': True, 'order_id': order_id})

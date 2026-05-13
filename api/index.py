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
        .product{background:rgba(255,255,255,0.1);padding:15px;margin:10px 0;border-radius:10px;display:flex;justify-content:space-between;}
        .price{color:#ffcc00;}
        .tab{display:inline-block;padding:10px 20px;margin:5px;background:#333;border-radius:10px;cursor:pointer;}
        .tab.active{background:#ffcc00;color:#1a1a2e;}
    </style>
</head>
<body>
    <h1>🔥 Akuma UC BOT 24/7</h1>
    
    <div>
        <div class="tab active" onclick="showTab('uc')">UC</div>
        <div class="tab" onclick="showTab('pp')">Популярность</div>
        <div class="tab" onclick="showTab('prime')">Подписки</div>
        <div class="tab" onclick="showTab('costumes')">X-костюмы</div>
    </div>
    
    <div id="products"></div>
    
    <div style="margin-top:20px;background:rgba(0,0,0,0.5);padding:20px;border-radius:10px;">
        <h3>🛒 Корзина</h3>
        <div id="cart"></div>
        <div id="total">Итого: 0 ₽</div>
        <button onclick="clearCart()" style="background:#ff4444;color:#fff;border:none;padding:10px;border-radius:10px;">Очистить</button>
    </div>
    
    <div style="margin-top:20px;">
        <input type="number" id="pubg_id" placeholder="Введите PUBG ID (начинается с 5)" style="width:100%;padding:14px;border-radius:10px;">
    </div>
    
    <button onclick="checkout()" style="background:#ffcc00;color:#1a1a2e;padding:16px;width:100%;border-radius:10px;margin-top:20px;font-size:18px;">Купить</button>
    
    <script>
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
                "1800": {name: "1800 UC", price: 1891}
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
            var productList = products[currentTab];
            var html = '';
            
            for (var key in productList) {
                var p = productList[key];
                var qty = cart[key] ? cart[key].quantity : 0;
                
                if (currentTab === 'uc') {
                    html += '<div class="product">' +
                        '<div><strong>' + p.name + '</strong><br><span class="price">' + p.price + ' ₽</span></div>' +
                        '<div><button onclick="updateQty(\'' + key + '\', -1)" style="background:#333;color:#fff;border:none;width:30px;height:30px;border-radius:8px;">-</button> ' +
                        '<span style="min-width:30px;display:inline-block;text-align:center;">' + qty + '</span> ' +
                        '<button onclick="updateQty(\'' + key + '\', 1)" style="background:#ffcc00;color:#1a1a2e;border:none;width:30px;height:30px;border-radius:8px;">+</button></div>' +
                    '</div>';
                } else {
                    html += '<div class="product">' +
                        '<div><strong>' + p.name + '</strong><br><span class="price">' + p.price + ' ₽</span></div>' +
                        '<div><button onclick="addToCart(\'' + key + '\', \'' + p.name + '\', ' + p.price + ')" style="background:#ffcc00;color:#1a1a2e;border:none;padding:8px 20px;border-radius:10px;">Выбрать</button></div>' +
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
                html += '<div>' + item.name + ' x' + item.quantity + ' = ' + itemTotal + ' ₽</div>';
            }
            document.getElementById('cart').innerHTML = Object.keys(cart).length === 0 ? 'Корзина пуста' : html;
            document.getElementById('total').innerHTML = 'Итого: ' + total + ' ₽';
        }
        
        function clearCart() {
            cart = {};
            saveCart();
            updateCartDisplay();
            renderProducts();
            alert('Корзина очищена');
        }
        
        function saveCart() {
            localStorage.setItem('cart', JSON.stringify(cart));
        }
        
        async function checkout() {
            var pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) { alert('Введите PUBG ID'); return; }
            if (!pubgId.toString().startsWith('5') || pubgId.length < 10) { alert('PUBG ID должен начинаться с 5 (10+ цифр)'); return; }
            if (Object.keys(cart).length === 0) { alert('Корзина пуста'); return; }
            
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
                    alert('✅ ЗАКАЗ ПРИНЯТ! Номер: #' + data.order_id + '\nСумма: ' + total + ' ₽\nПерейдите в бота для оплаты');
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
    data = request.json
    print("Заказ:", data)
    return jsonify({'ok': True, 'order_id': 1})

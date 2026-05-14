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
            color: white;
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
        button {
            background: #ffcc00;
            color: #1a1a2e;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            border: none;
            margin: 10px 0;
        }
        h1 {
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>🔥 Akuma UC Shop</h1>
    
    <input type="number" id="pubg_id" placeholder="Введите PUBG ID (начинается с 5)">
    
    <div id="products"></div>
    
    <script>
        var products = [
            {name: "60 UC", price: 87},
            {name: "120 UC", price: 152},
            {name: "180 UC", price: 223},
            {name: "240 UC", price: 293},
            {name: "325 UC", price: 387},
            {name: "385 UC", price: 434},
            {name: "445 UC", price: 482},
            {name: "660 UC", price: 756},
            {name: "720 UC", price: 771},
            {name: "985 UC", price: 1049},
            {name: "1320 UC", price: 1401},
            {name: "1800 UC", price: 1891}
        ];
        
        function buy(name, price) {
            var pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) {
                alert('Введите PUBG ID');
                return;
            }
            if (!pubgId.startsWith('5') || pubgId.length < 10) {
                alert('PUBG ID должен начинаться с 5 (10+ цифр)');
                return;
            }
            
            fetch('/create-order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pubg_id: pubgId, product: name, price: price})
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) {
                    alert('✅ ЗАКАЗ ПРИНЯТ! Номер: #' + data.order_id + '\nСумма: ' + price + ' ₽\nПерейдите в бота для оплаты');
                    window.location.href = 'https://t.me/akuma_ucbot';
                } else {
                    alert('Ошибка');
                }
            })
            .catch(err => alert('Ошибка сервера'));
        }
        
        var html = '';
        for (var i = 0; i < products.length; i++) {
            html += '<div class="product">' +
                '<div><strong>' + products[i].name + '</strong><br><span class="price">' + products[i].price + ' ₽</span></div>' +
                '<div><button onclick="buy(\'' + products[i].name + '\', ' + products[i].price + ')">Купить</button></div>' +
            '</div>';
        }
        document.getElementById('products').innerHTML = html;
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
    print("ЗАКАЗ:", data)
    
    bot_token = os.environ.get("BOT_TOKEN")
    admin_id = os.environ.get("ADMIN_ID", "8504217011")
    
    if bot_token:
        try:
            text = f"🆕 **НОВЫЙ ЗАКАЗ**\n\n🎮 PUBG ID: {data['pubg_id']}\n📦 {data['product']}\n💰 {data['price']}₽"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": admin_id, "text": text, "parse_mode": "Markdown"})
        except:
            pass
    
    return jsonify({'ok': True, 'order_id': 1})

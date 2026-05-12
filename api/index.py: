from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "AkumaUCBOT")
ADMIN_ID = os.environ.get("ADMIN_ID", "8504217011")

orders_db = {}
order_counter = 1

PRODUCTS = {
    "60": {"amount": 60, "price": 78},
    "120": {"amount": 120, "price": 141},
    "180": {"amount": 180, "price": 204},
    "240": {"amount": 240, "price": 267},
    "325": {"amount": 325, "price": 356},
    "385": {"amount": 385, "price": 419},
    "445": {"amount": 445, "price": 482},
    "660": {"amount": 660, "price": 708},
    "720": {"amount": 720, "price": 771},
    "985": {"amount": 985, "price": 1049},
    "1320": {"amount": 1320, "price": 1401},
    "1800": {"amount": 1800, "price": 1905}
}

HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akuma UC Shop</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:#fff;padding:20px;}
        .container{max-width:600px;margin:0 auto;}
        .header{text-align:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px;}
        .header h1{font-size:28px;background:linear-gradient(135deg,#ffcc00,#ff9900);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .id-section{background:rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin-bottom:20px;}
        .id-section input{width:100%;padding:14px;border:1px solid rgba(255,255,255,0.2);border-radius:12px;background:rgba(0,0,0,0.3);color:#fff;font-size:16px;}
        .products{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:30px;}
        .product-card{background:rgba(255,255,255,0.05);border-radius:16px;padding:16px;text-align:center;cursor:pointer;border:1px solid rgba(255,255,255,0.1);}
        .product-card:hover{background:rgba(255,255,255,0.1);}
        .product-amount{font-size:20px;font-weight:bold;color:#ffcc00;}
        .product-price{font-size:14px;color:#aaa;margin-top:5px;}
        .btn-buy{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:16px;width:100%;border-radius:12px;color:#1a1a2e;font-size:18px;font-weight:bold;cursor:pointer;}
        .footer{text-align:center;padding:20px;font-size:12px;color:#666;border-top:1px solid rgba(255,255,255,0.1);margin-top:20px;}
        .footer a{color:#ffcc00;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 AKUMA UC SHOP</h1>
            <p>Быстрая покупка UC | 24/7</p>
        </div>
        <div class="id-section">
            <input type="number" id="pubg_id" placeholder="Введите PUBG ID (начинается с 5)">
        </div>
        <div class="products" id="products">
            <div style="text-align:center;padding:20px;">Загрузка...</div>
        </div>
        <div class="footer">
            <p>Вопросы: <a href="https://t.me/aakumma">@aakumma</a></p>
        </div>
    </div>
    <script>
        const products = {{ products|tojson }};
        const botUsername = "{{ bot_username }}";
        
        function renderProducts() {
            const container = document.getElementById('products');
            let html = '';
            for (const [key, product] of Object.entries(products)) {
                html += `<div class="product-card" onclick="createOrder('${key}')">
                            <div class="product-amount">${product.amount} UC</div>
                            <div class="product-price">${product.price} ₽</div>
                        </div>`;
            }
            container.innerHTML = html;
        }
        
        async function createOrder(amount) {
            const pubgId = document.getElementById('pubg_id').value;
            if (!pubgId) { alert('Введите PUBG ID'); return; }
            if (!pubgId.toString().startsWith('5') || pubgId.length < 10) { alert('PUBG ID должен начинаться с 5 (10+ цифр)'); return; }
            
            const res = await fetch('/create-order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pubg_id: pubgId, amount: amount})
            });
            const data = await res.json();
            if (data.ok) {
                window.location.href = `https://t.me/${botUsername}?start=web_${data.order_id}`;
            } else {
                alert('Ошибка создания заказа');
            }
        }
        
        renderProducts();
    </script>
</body>
</html>'''

def send_notification(order_id, pubg_id, amount, price):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": f"🆕 **ЗАКАЗ С САЙТА**\nНомер: #{order_id}\nPUBG ID: {pubg_id}\nUC: {amount}\nСумма: {price}₽",
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload)
    except:
        pass

@app.route('/')
def index():
    return HTML.replace('{{ products|tojson }}', json.dumps(PRODUCTS)).replace('{{ bot_username }}', BOT_USERNAME)

@app.route('/create-order', methods=['POST'])
def create_order():
    global order_counter
    data = request.json
    pubg_id = data.get('pubg_id')
    amount = data.get('amount')
    
    if not pubg_id or not amount:
        return jsonify({'error': 'Missing data'}), 400
    
    product = PRODUCTS.get(amount)
    if not product:
        return jsonify({'error': 'Invalid amount'}), 400
    
    order_id = order_counter
    order_counter += 1
    
    orders_db[order_id] = {
        'pubg_id': pubg_id,
        'amount': amount,
        'price': product['price'],
        'status': 'pending'
    }
    
    send_notification(order_id, pubg_id, amount, product['price'])
    
    return jsonify({'ok': True, 'order_id': order_id})

@app.route('/order/<int:order_id>')
def get_order(order_id):
    order = orders_db.get(order_id)
    if not order:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(order)

@app.route('/products')
def get_products():
    return jsonify(PRODUCTS)

# Для Vercel
app = app

if __name__ == '__main__':
    app.run()

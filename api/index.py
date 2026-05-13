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
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Akuma UC Shop</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:#fff;padding:20px;}
        .container{max-width:600px;margin:0 auto;}
        .header{text-align:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px;}
        .header h1{font-size:28px;background:linear-gradient(135deg,#ffcc00,#ff9900);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .header p{color:#888;font-size:14px;margin-top:5px;}
        .id-section{background:rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin-bottom:20px;}
        .id-section label{display:block;margin-bottom:8px;font-size:14px;color:#ccc;}
        .id-section input{width:100%;padding:14px;border:1px solid rgba(255,255,255,0.2);border-radius:12px;background:rgba(0,0,0,0.3);color:#fff;font-size:16px;outline:none;}
        .id-section input:focus{border-color:#ffcc00;}
        .products{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:30px;}
        .product-card{background:rgba(255,255,255,0.05);border-radius:16px;padding:16px;text-align:center;cursor:pointer;border:1px solid rgba(255,255,255,0.1);transition:all 0.2s;}
        .product-card:hover{background:rgba(255,255,255,0.1);border-color:#ffcc00;transform:translateY(-2px);}
        .product-amount{font-size:20px;font-weight:bold;color:#ffcc00;}
        .product-price{font-size:14px;color:#aaa;margin-top:5px;}
        .card-details{background:rgba(0,0,0,0.5);border-radius:16px;padding:20px;margin:20px 0;text-align:center;border:1px solid rgba(255,204,0,0.3);}
        .card-details h3{color:#ffcc00;margin-bottom:15px;}
        .card-number{font-size:22px;font-weight:bold;letter-spacing:2px;background:#1a1a2e;padding:12px;border-radius:12px;font-family:monospace;}
        .pay-button{background:linear-gradient(135deg,#ffcc00,#ff9900);border:none;padding:16px;width:100%;border-radius:12px;color:#1a1a2e;font-size:18px;font-weight:bold;cursor:pointer;margin-top:20px;}
        .footer{text-align:center;padding:20px;font-size:12px;color:#666;border-top:1px solid rgba(255,255,255,0.1);margin-top:20px;}
        .footer a{color:#ffcc00;text-decoration:none;}
        .hidden{display:none;}
        .back-link{text-align:center;margin-top:15px;}
        .back-link a{color:#ffcc00;text-decoration:none;font-size:14px;}
        @media (max-width:480px){.products{grid-template-columns:1fr;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 AKUMA UC SHOP</h1>
            <p>Быстрая покупка UC | 24/7</p>
        </div>
        
        <div id="order-form">
            <div class="id-section">
                <label>🎮 Введите ваш PUBG ID (начинается с 5):</label>
                <input type="number" id="pubg_id" placeholder="Например: 51867875896" autocomplete="off">
            </div>
            <div class="products" id="products"></div>
        </div>
        
        <div id="payment-info" class="hidden">
            <div class="card-details">
                <h3>💳 РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ</h3>
                <p>Переведите точную сумму на карту:</p>
                <div class="card-number">**** **** **** 1234</div>
                <p style="margin-top: 15px;">Получатель: <strong>АКУМА</strong></p>
                <p style="font-size: 12px; color: #888; margin-top: 15px;">Сумма к оплате: <strong id="pay-amount">0</strong> ₽</p>
                <button class="pay-button" onclick="confirmPayment()">✅ Я ОПЛАТИЛ</button>
            </div>
            <div class="back-link">
                <a href="#" onclick="backToCatalog(); return false;">◀️ Назад к выбору товара</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Вопросы: <a href="https://t.me/aakumma">@aakumma</a></p>
        </div>
    </div>
    
    <script>
        const products = {
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
        };
        const botUsername = "akuma_ucbot";
        let currentAmount = null;
        let currentPrice = null;
        let currentPubgId = null;
        
        function renderProducts() {
            const container = document.getElementById('products');
            let html = '';
            for (const [key, product] of Object.entries(products)) {
                html += '<div class="product-card" onclick="selectProduct(' + key + ')">' +
                            '<div class="product-amount">' + product.amount + ' UC</div>' +
                            '<div class="product-price">' + product.price + ' ₽</div>' +
                        '</div>';
            }
            container.innerHTML = html;
        }
        
        function selectProduct(amount) {
            const pubgId = document.getElementById('pubg_id').value;
            
            if (!pubgId) {
                alert('❌ Введите PUBG ID');
                document.getElementById('pubg_id').focus();
                return;
            }
            
            if (!pubgId.toString().startsWith('5') || pubgId.toString().length < 10) {
                alert('❌ PUBG ID должен начинаться с 5 и содержать минимум 10 цифр');
                return;
            }
            
            const product = products[amount];
            if (!product) return;
            
            currentAmount = product.amount;
            currentPrice = product.price;
            currentPubgId = pubgId;
            
            document.getElementById('pay-amount').innerText = currentPrice;
            document.getElementById('order-form').classList.add('hidden');
            document.getElementById('payment-info').classList.remove('hidden');
        }
        
        async function confirmPayment() {
            if (!currentPubgId || !currentAmount || !currentPrice) {
                alert('❌ Ошибка: данные не найдены');
                return;
            }
            
            try {
                const response = await fetch('/create-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        pubg_id: currentPubgId,
                        amount: currentAmount.toString(),
                        price: currentPrice
                    })
                });
                
                const data = await response.json();
                
                if (data.ok && data.order_id) {
                    window.location.href = 'https://t.me/' + botUsername + '?start=order_' + data.order_id;
                } else {
                    alert('❌ Ошибка при создании заказа');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('❌ Ошибка сервера. Попробуйте позже.');
            }
        }
        
        function backToCatalog() {
            document.getElementById('order-form').classList.remove('hidden');
            document.getElementById('payment-info').classList.add('hidden');
            currentAmount = null;
            currentPrice = null;
            currentPubgId = null;
        }
        
        renderProducts();
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
    amount = data.get('amount')
    price = data.get('price')
    
    if not pubg_id or not amount:
        return jsonify({'error': 'Missing data'}), 400
    
    order_id = order_counter
    order_counter += 1
    
    temp_orders[order_id] = {
        'pubg_id': pubg_id,
        'amount': amount,
        'price': price,
        'status': 'pending',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Отправляем уведомление админу (опционально)
    if BOT_TOKEN:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": ADMIN_ID,
                "text": f"🆕 **ЗАКАЗ С САЙТА**\n🆔 #{order_id}\n🎮 PUBG ID: {pubg_id}\n📦 {amount} UC\n💰 {price}₽",
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload)
        except:
            pass
    
    return jsonify({'ok': True, 'order_id': order_id})

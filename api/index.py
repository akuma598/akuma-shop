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
    </style>
</head>
<body>
    <h1>🔥 Akuma UC BOT 24/7</h1>
    <div id="products"></div>
    
    <script>
        const products = {
            "60": {"name": "60 UC", "price": 87},
            "120": {"name": "120 UC", "price": 152},
            "180": {"name": "180 UC", "price": 223},
            "240": {"name": "240 UC", "price": 293},
            "325": {"name": "325 UC", "price": 387},
            "385": {"name": "385 UC", "price": 434},
            "445": {"name": "445 UC", "price": 482},
            "660": {"name": "660 UC", "price": 756},
            "720": {"name": "720 UC", "price": 771},
            "985": {"name": "985 UC", "price": 1049},
            "1320": {"name": "1320 UC", "price": 1401},
            "1800": {"name": "1800 UC", "price": 1891}
        };
        
        let html = '';
        for (const [key, p] of Object.entries(products)) {
            html += '<div class="product"><span>' + p.name + '</span><span class="price">' + p.price + ' ₽</span></div>';
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
    return jsonify({'ok': True, 'order_id': 1})

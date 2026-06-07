from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Akuma UC Shop | Играй и покупай</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        
        .container {
            max-width: 500px;
            margin: 0 auto;
        }
        
        /* Хедер */
        .header {
            text-align: center;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 28px;
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
        
        /* ИГРА */
        .game-container {
            background: rgba(0,0,0,0.4);
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid rgba(255,204,0,0.3);
        }
        
        .game-title {
            font-size: 18px;
            margin-bottom: 15px;
            color: #ffcc00;
        }
        
        .game-stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
        }
        
        .score-box {
            font-size: 24px;
            font-weight: bold;
        }
        
        .score-box span {
            color: #ffcc00;
        }
        
        .best-box {
            font-size: 24px;
            font-weight: bold;
        }
        
        .best-box span {
            color: #ffcc00;
        }
        
        .game-area {
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
            min-height: 300px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            gap: 15px;
            cursor: pointer;
        }
        
        .hole {
            width: 80px;
            height: 80px;
            background: #2a1a3a;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.1s ease;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5), 0 5px 0 #1a0a2a;
        }
        
        .hole.active {
            background: #ffcc00;
            transform: scale(0.95);
            box-shadow: inset 0 0 10px rgba(0,0,0,0.3), 0 2px 0 #cc9900;
        }
        
        .hole.active .mole {
            font-size: 45px;
            display: block;
        }
        
        .mole {
            font-size: 0;
            display: none;
            transition: all 0.1s;
        }
        
        .game-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 12px 30px;
            border-radius: 30px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
            transition: opacity 0.2s;
        }
        
        .game-btn:hover {
            opacity: 0.9;
        }
        
        .game-timer {
            font-size: 28px;
            font-weight: bold;
            margin: 15px 0;
            color: #ffcc00;
        }
        
        /* Цены */
        .prices {
            background: rgba(0,0,0,0.4);
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .prices h3 {
            text-align: center;
            margin-bottom: 15px;
            color: #ffcc00;
        }
        
        .price-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .price-item {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 12px;
            text-align: center;
            font-size: 14px;
        }
        
        .price-item .amount {
            font-weight: bold;
            color: #ffcc00;
        }
        
        /* Кнопка в бота */
        .bot-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 18px;
            width: 100%;
            border-radius: 16px;
            color: #1a1a2e;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            transition: opacity 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .bot-btn:hover {
            opacity: 0.9;
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
        
        @media (max-width: 480px) {
            .hole {
                width: 65px;
                height: 65px;
            }
            .hole.active .mole {
                font-size: 35px;
            }
            .price-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Akuma UC Shop</h1>
            <p>Играй и получай скидку на UC!</p>
        </div>
        
        <!-- ИГРА: Ударь крота -->
        <div class="game-container">
            <div class="game-title">🎮 УДАРЬ КРОТА 🎮</div>
            <div class="game-stats">
                <div class="score-box">🎯 <span id="score">0</span></div>
                <div class="best-box">🏆 <span id="best">0</span></div>
            </div>
            <div class="game-area" id="gameArea">
                <!-- 9 ячеек будут созданы через JS -->
            </div>
            <div class="game-timer" id="timer">⏱️ 30s</div>
            <button class="game-btn" id="startBtn">▶️ НАЧАТЬ ИГРУ</button>
            <div style="margin-top: 15px; font-size: 12px; color: #888;">
                💡 За каждые 10 очков — скидка 1% (до 20%)
            </div>
        </div>
        
        <!-- Цены -->
        <div class="prices">
            <h3>💰 ЦЕНЫ НА UC</h3>
            <div class="price-grid">
                <div class="price-item"><span class="amount">60 UC</span> — 87₽</div>
                <div class="price-item"><span class="amount">120 UC</span> — 152₽</div>
                <div class="price-item"><span class="amount">180 UC</span> — 223₽</div>
                <div class="price-item"><span class="amount">240 UC</span> — 293₽</div>
                <div class="price-item"><span class="amount">325 UC</span> — 387₽</div>
                <div class="price-item"><span class="amount">385 UC</span> — 434₽</div>
                <div class="price-item"><span class="amount">445 UC</span> — 482₽</div>
                <div class="price-item"><span class="amount">660 UC</span> — 756₽</div>
                <div class="price-item"><span class="amount">720 UC</span> — 771₽</div>
                <div class="price-item"><span class="amount">985 UC</span> — 1049₽</div>
                <div class="price-item"><span class="amount">1320 UC</span> — 1401₽</div>
                <div class="price-item"><span class="amount">1800 UC</span> — 1891₽</div>
            </div>
        </div>
        
        <!-- Кнопка перехода в бота -->
        <button class="bot-btn" id="botBtn">
            🤖 ПЕРЕЙТИ В БОТ ДЛЯ ПОКУПКИ 🤖
        </button>
        
        <div class="footer">
            <p>Вопросы: <a href="https://t.me/aakumma">@aakumma</a></p>
        </div>
    </div>
    
    <script>
        // ---- ИГРА: УДАРЬ КРОТА ----
        let score = 0;
        let best = localStorage.getItem('bestScore') || 0;
        let activeHole = null;
        let gameInterval = null;
        let timeLeft = 30;
        let isPlaying = false;
        let gameSpeed = 800;
        
        const holes = [];
        
        document.getElementById('best').innerText = best;
        
        // Создаём 9 ячеек
        const gameArea = document.getElementById('gameArea');
        for (let i = 0; i < 9; i++) {
            const hole = document.createElement('div');
            hole.className = 'hole';
            hole.dataset.index = i;
            const mole = document.createElement('div');
            mole.className = 'mole';
            mole.innerHTML = '🐭';
            hole.appendChild(mole);
            hole.onclick = (function(idx) {
                return function() { whack(idx); };
            })(i);
            gameArea.appendChild(hole);
            holes.push(hole);
        }
        
        function showMole() {
            if (!isPlaying) return;
            
            // Скрываем текущего крота
            if (activeHole !== null) {
                holes[activeHole].classList.remove('active');
            }
            
            // Показываем в новой случайной ячейке
            let newHole;
            do {
                newHole = Math.floor(Math.random() * holes.length);
            } while (newHole === activeHole);
            
            activeHole = newHole;
            holes[activeHole].classList.add('active');
            
            // Увеличиваем скорость со временем
            if (timeLeft < 20) gameSpeed = 600;
            if (timeLeft < 10) gameSpeed = 450;
            
            clearTimeout(gameInterval);
            gameInterval = setTimeout(showMole, gameSpeed);
        }
        
        function whack(index) {
            if (!isPlaying) return;
            if (activeHole === index) {
                // Попал!
                score++;
                document.getElementById('score').innerText = score;
                
                // Обновляем рекорд
                if (score > best) {
                    best = score;
                    document.getElementById('best').innerText = best;
                    localStorage.setItem('bestScore', best);
                }
                
                // Крот убегает
                holes[activeHole].classList.remove('active');
                activeHole = null;
                
                clearTimeout(gameInterval);
                gameInterval = setTimeout(showMole, gameSpeed);
            }
        }
        
        function startGame() {
            if (isPlaying) return;
            
            score = 0;
            timeLeft = 30;
            gameSpeed = 800;
            document.getElementById('score').innerText = '0';
            document.getElementById('timer').innerHTML = '⏱️ 30s';
            document.getElementById('startBtn').innerText = '🎮 ИГРА ИДЁТ...';
            document.getElementById('startBtn').disabled = true;
            document.getElementById('startBtn').style.opacity = '0.6';
            
            isPlaying = true;
            
            // Таймер
            const timerInterval = setInterval(() => {
                if (!isPlaying) {
                    clearInterval(timerInterval);
                    return;
                }
                timeLeft--;
                document.getElementById('timer').innerHTML = `⏱️ ${timeLeft}s`;
                
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    endGame();
                }
            }, 1000);
            
            showMole();
        }
        
        function endGame() {
            isPlaying = false;
            clearTimeout(gameInterval);
            
            if (activeHole !== null) {
                holes[activeHole].classList.remove('active');
                activeHole = null;
            }
            
            // Рассчитываем скидку (1% за 10 очков, макс 20%)
            let discount = Math.min(Math.floor(score / 10), 20);
            
            document.getElementById('startBtn').innerText = '▶️ НАЧАТЬ ИГРУ';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('startBtn').style.opacity = '1';
            
            if (score > 0) {
                alert(`🎉 ИГРА ОКОНЧЕНА!\n\n🏆 Ваш счёт: ${score}\n🎁 Скидка на первый заказ: ${discount}%\n\n👉 Перейдите в бота и укажите промокод GAME${discount} для получения скидки!`);
                
                // Сохраняем скидку в localStorage
                localStorage.setItem('gameDiscount', discount);
                localStorage.setItem('gameCode', `GAME${discount}`);
            } else {
                alert(`🎮 ИГРА ОКОНЧЕНА!\n\n🏆 Ваш счёт: ${score}\n\nПопробуйте ещё раз, чтобы получить скидку!`);
            }
        }
        
        document.getElementById('startBtn').onclick = startGame;
        
        // ---- КНОПКА ПЕРЕХОДА В БОТА ----
        document.getElementById('botBtn').onclick = function() {
            let discount = localStorage.getItem('gameDiscount') || 0;
            let promoCode = localStorage.getItem('gameCode') || '';
            
            let url = 'https://t.me/akuma_ucbot';
            if (discount > 0 && promoCode) {
                url += `?start=promo_${promoCode}`;
                alert(`🎁 Ваша скидка ${discount}%! Промокод: ${promoCode}\n\nПри переходе в бота скидка применится автоматически!`);
            }
            
            window.location.href = url;
        };
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

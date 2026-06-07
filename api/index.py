from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Истребитель | Akuma Game</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .game-container {
            text-align: center;
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            border-radius: 16px;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
            background: linear-gradient(180deg, #1a3a5c 0%, #0a1a2c 100%);
            cursor: none;
        }
        
        .info {
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }
        
        .score-box, .health-box, .kills-box {
            text-align: center;
            background: rgba(0,0,0,0.5);
            padding: 8px 20px;
            border-radius: 30px;
            backdrop-filter: blur(10px);
        }
        
        .score-box span, .health-box span, .kills-box span {
            color: #ffcc00;
            font-size: 28px;
            font-weight: bold;
            display: block;
        }
        
        .score-box p, .health-box p, .kills-box p {
            font-size: 11px;
            color: #aaa;
            margin-top: 3px;
        }
        
        .start-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 12px 35px;
            border-radius: 40px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 18px;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s, opacity 0.2s;
        }
        
        .start-btn:hover {
            transform: scale(1.05);
            opacity: 0.9;
        }
        
        .status {
            margin-top: 12px;
            font-size: 13px;
            color: #aaa;
        }
        
        .controls {
            margin-top: 12px;
            display: flex;
            justify-content: center;
            gap: 15px;
            font-size: 11px;
            color: #888;
            flex-wrap: wrap;
        }
        
        .controls span {
            background: rgba(0,0,0,0.3);
            padding: 4px 10px;
            border-radius: 20px;
        }
        
        .footer {
            margin-top: 15px;
            font-size: 11px;
            color: #666;
            text-align: center;
        }
        
        .footer a {
            color: #ffcc00;
            text-decoration: none;
        }
        
        @media (max-width: 600px) {
            canvas {
                width: 100%;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="700" height="500"></canvas>
        
        <div class="info">
            <div class="score-box">
                <span id="score">0</span>
                <p>ОЧКИ</p>
            </div>
            <div class="kills-box">
                <span id="kills">0</span>
                <p>СБИТО</p>
            </div>
            <div class="health-box">
                <span id="health">❤️ 100</span>
                <p>ЗДОРОВЬЕ</p>
            </div>
        </div>
        
        <button class="start-btn" id="startBtn">🚀 НАЧАТЬ БОЙ</button>
        <div class="controls">
            <span>🖱️ МЫШЬ — ДВИЖЕНИЕ</span>
            <span>🔫 ЛКМ / КЛИК — РАКЕТА</span>
        </div>
        <div class="status" id="status">✈️ Уничтожай вражеские вертолёты!</div>
        
        <div class="footer">
            <p>🎮 Веди мышкой — истребитель летит за курсором. Кликай — пускай ракеты!</p>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 700;
        const canvasHeight = 500;
        
        // Истребитель
        let player = {
            x: canvasWidth / 2 - 25,
            y: canvasHeight - 80,
            width: 50,
            height: 50,
            health: 100,
            maxHealth: 100
        };
        
        // Ракеты
        let missiles = [];
        let shootCooldown = 0;
        let shootDelay = 12;
        
        // Вертолёты врагов
        let enemies = [];
        let enemySpawnCounter = 0;
        let enemySpawnDelay = 45;
        let kills = 0;
        let score = 0;
        
        let gameRunning = false;
        let gameOver = false;
        
        // Мышь
        let mouseX = canvasWidth / 2;
        let mouseY = canvasHeight / 2;
        
        // Элементы DOM
        const scoreElement = document.getElementById('score');
        const killsElement = document.getElementById('kills');
        const healthElement = document.getElementById('health');
        const startBtn = document.getElementById('startBtn');
        const statusElement = document.getElementById('status');
        
        class Enemy {
            constructor() {
                this.width = 50;
                this.height = 40;
                this.x = Math.random() * (canvasWidth - this.width);
                this.y = -this.height;
                this.speed = 1.5 + Math.random() * 1.5;
            }
            
            move() {
                this.y += this.speed;
            }
            
            draw() {
                ctx.save();
                ctx.shadowBlur = 0;
                
                // Корпус вертолёта
                ctx.fillStyle = '#4a6a3a';
                ctx.fillRect(this.x, this.y, this.width, this.height - 10);
                
                // Кабина
                ctx.fillStyle = '#87CEEB';
                ctx.fillRect(this.x + 5, this.y + 5, 15, 15);
                
                // Лопасти
                ctx.fillStyle = '#2a2a2a';
                const bladeY = this.y - 5;
                ctx.fillRect(this.x + 10, bladeY, 30, 8);
                ctx.fillRect(this.x + 20, bladeY - 5, 8, 18);
                
                // Хвост
                ctx.fillStyle = '#3a5a2a';
                ctx.fillRect(this.x + this.width - 10, this.y + 15, 15, 10);
                
                // Пулемёт
                ctx.fillStyle = '#555';
                ctx.fillRect(this.x + this.width - 5, this.y + 20, 10, 5);
                
                ctx.restore();
            }
        }
        
        class Missile {
            constructor(x, y, targetX, targetY) {
                this.x = x;
                this.y = y;
                this.width = 8;
                this.height = 5;
                // Направление от истребителя к цели (курсору)
                const dx = targetX - x;
                const dy = targetY - y;
                const len = Math.sqrt(dx * dx + dy * dy);
                this.vx = (dx / len) * 8;
                this.vy = (dy / len) * 8;
            }
            
            move() {
                this.x += this.vx;
                this.y += this.vy;
            }
            
            draw() {
                ctx.save();
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#ff6600';
                ctx.fillRect(this.x, this.y, this.width, this.height);
                ctx.fillStyle = '#ffcc00';
                ctx.fillRect(this.x + this.width - 2, this.y + 1, 4, 3);
                ctx.fillStyle = '#ff3300';
                ctx.beginPath();
                ctx.moveTo(this.x - 5, this.y + 2);
                ctx.lineTo(this.x, this.y);
                ctx.lineTo(this.x, this.y + 5);
                ctx.fill();
                ctx.restore();
            }
        }
        
        function initGame() {
            player.health = 100;
            player.x = canvasWidth / 2 - 25;
            player.y = canvasHeight - 80;
            missiles = [];
            enemies = [];
            kills = 0;
            score = 0;
            shootCooldown = 0;
            enemySpawnCounter = 0;
            gameOver = false;
            
            scoreElement.innerText = '0';
            killsElement.innerText = '0';
            healthElement.innerText = '❤️ 100';
        }
        
        function spawnEnemy() {
            if (enemies.length >= 6) return;
            enemies.push(new Enemy());
        }
        
        function shootMissile() {
            if (!gameRunning) return;
            const fromX = player.x + player.width / 2;
            const fromY = player.y + player.height / 2;
            missiles.push(new Missile(fromX, fromY, mouseX, mouseY));
        }
        
        function update() {
            if (!gameRunning || gameOver) return;
            
            // Движение истребителя за мышкой
            let targetX = mouseX - player.width / 2;
            let targetY = mouseY - player.height / 2;
            targetX = Math.min(Math.max(targetX, 0), canvasWidth - player.width);
            targetY = Math.min(Math.max(targetY, 0), canvasHeight - player.height);
            
            player.x = player.x * 0.8 + targetX * 0.2;
            player.y = player.y * 0.8 + targetY * 0.2;
            
            // Перезарядка
            if (shootCooldown > 0) shootCooldown--;
            
            // Ракеты
            for (let i = 0; i < missiles.length; i++) {
                missiles[i].move();
                if (missiles[i].x < -100 || missiles[i].x > canvasWidth + 100 ||
                    missiles[i].y < -100 || missiles[i].y > canvasHeight + 100) {
                    missiles.splice(i, 1);
                    i--;
                }
            }
            
            // Враги
            for (let i = 0; i < enemies.length; i++) {
                enemies[i].move();
                
                // Столкновение с истребителем
                if (enemies[i].x < player.x + player.width &&
                    enemies[i].x + enemies[i].width > player.x &&
                    enemies[i].y < player.y + player.height &&
                    enemies[i].y + enemies[i].height > player.y) {
                    
                    player.health -= 15;
                    healthElement.innerText = '❤️ ' + Math.max(0, player.health);
                    enemies.splice(i, 1);
                    i--;
                    
                    if (player.health <= 0) {
                        gameRunning = false;
                        gameOver = true;
                        statusElement.innerHTML = '💥 ИСТРЕБИТЕЛЬ СБИТ! ИГРА ОКОНЧЕНА 💥';
                        statusElement.style.color = '#ff6666';
                        startBtn.style.display = 'block';
                        return;
                    }
                    continue;
                }
                
                // Попадание ракет
                for (let j = 0; j < missiles.length; j++) {
                    if (missiles[j].x < enemies[i].x + enemies[i].width &&
                        missiles[j].x + missiles[j].width > enemies[i].x &&
                        missiles[j].y < enemies[i].y + enemies[i].height &&
                        missiles[j].y + missiles[j].height > enemies[i].y) {
                        
                        missiles.splice(j, 1);
                        enemies.splice(i, 1);
                        kills++;
                        score += 10;
                        scoreElement.innerText = score;
                        killsElement.innerText = kills;
                        i--;
                        
                        if (navigator.vibrate) navigator.vibrate(50);
                        break;
                    }
                }
            }
            
            // Спавн врагов
            if (enemies.length < 4) {
                enemySpawnCounter++;
                if (enemySpawnCounter > enemySpawnDelay) {
                    spawnEnemy();
                    enemySpawnCounter = 0;
                    enemySpawnDelay = Math.max(35, 45 - Math.floor(kills / 20));
                }
            }
        }
        
        function draw() {
            // Небо
            const grad = ctx.createLinearGradient(0, 0, 0, canvasHeight);
            grad.addColorStop(0, '#1a3a5c');
            grad.addColorStop(1, '#0a1a2c');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Облака
            ctx.fillStyle = 'rgba(255,255,255,0.1)';
            ctx.beginPath();
            ctx.ellipse(100, 100, 50, 30, 0, 0, Math.PI * 2);
            ctx.ellipse(140, 90, 40, 25, 0, 0, Math.PI * 2);
            ctx.ellipse(60, 90, 40, 25, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(550, 200, 60, 35, 0, 0, Math.PI * 2);
            ctx.ellipse(600, 190, 45, 28, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // Взлётная полоса
            ctx.fillStyle = '#3a3a3a';
            ctx.fillRect(0, canvasHeight - 60, canvasWidth, 60);
            ctx.fillStyle = '#ffcc00';
            for(let i = 0; i < 20; i++) {
                ctx.fillRect(i * 40, canvasHeight - 55, 20, 4);
            }
            
            // Ракеты
            for (let missile of missiles) {
                missile.draw();
            }
            
            // Враги
            for (let enemy of enemies) {
                enemy.draw();
            }
            
            // Истребитель
            ctx.save();
            ctx.shadowBlur = 0;
            
            // Фюзеляж
            ctx.fillStyle = '#5a7a5a';
            ctx.beginPath();
            ctx.moveTo(player.x + player.width/2, player.y);
            ctx.lineTo(player.x + player.width - 5, player.y + player.height - 10);
            ctx.lineTo(player.x + player.width/2, player.y + player.height);
            ctx.lineTo(player.x + 5, player.y + player.height - 10);
            ctx.fill();
            
            // Крылья
            ctx.fillStyle = '#4a6a4a';
            ctx.fillRect(player.x + 5, player.y + 15, 40, 8);
            ctx.fillRect(player.x + 10, player.y + 25, 30, 6);
            
            // Кабина
            ctx.fillStyle = '#87CEEB';
            ctx.beginPath();
            ctx.arc(player.x + player.width/2, player.y + 10, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#333';
            ctx.beginPath();
            ctx.arc(player.x + player.width/2 + 2, player.y + 8, 3, 0, Math.PI * 2);
            ctx.fill();
            
            // Двигатель
            ctx.fillStyle = '#ff6600';
            ctx.fillRect(player.x + player.width - 8, player.y + 20, 8, 12);
            
            // Полоска здоровья
            ctx.fillStyle = '#ff4444';
            ctx.fillRect(player.x, player.y - 10, player.width, 5);
            ctx.fillStyle = '#44ff44';
            ctx.fillRect(player.x, player.y - 10, player.width * (player.health / player.maxHealth), 5);
            
            ctx.restore();
            
            // Прицел
            ctx.beginPath();
            ctx.strokeStyle = '#ffcc00';
            ctx.lineWidth = 2;
            ctx.arc(mouseX, mouseY, 12, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(mouseX - 18, mouseY);
            ctx.lineTo(mouseX - 8, mouseY);
            ctx.moveTo(mouseX + 8, mouseY);
            ctx.lineTo(mouseX + 18, mouseY);
            ctx.moveTo(mouseX, mouseY - 18);
            ctx.lineTo(mouseX, mouseY - 8);
            ctx.moveTo(mouseX, mouseY + 8);
            ctx.lineTo(mouseX, mouseY + 18);
            ctx.stroke();
            
            // Информация
            ctx.font = 'bold 20px Arial';
            ctx.fillStyle = '#ffcc00';
            ctx.shadowBlur = 3;
            ctx.fillText(`СБИТО: ${kills}`, canvasWidth - 130, 40);
            ctx.font = '14px Arial';
            ctx.fillStyle = '#aaa';
            ctx.fillText(`Ракет: ${missiles.length}`, canvasWidth - 130, 70);
            ctx.shadowBlur = 0;
            
            if (!gameRunning && !gameOver) {
                ctx.font = 'bold 28px Arial';
                ctx.fillStyle = '#fff';
                ctx.fillText('✈️ ИСТРЕБИТЕЛЬ ✈️', canvasWidth / 2 - 140, canvasHeight / 2 - 50);
                ctx.font = '16px Arial';
                ctx.fillText('Веди мышкой — лети за курсором', canvasWidth / 2 - 160, canvasHeight / 2);
                ctx.fillText('Клик — пуск ракеты', canvasWidth / 2 - 80, canvasHeight / 2 + 30);
            }
        }
        
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        function startGame() {
            initGame();
            gameRunning = true;
            gameOver = false;
            startBtn.style.display = 'none';
            statusElement.innerHTML = '✈️ Уничтожай вражеские вертолёты!';
            statusElement.style.color = '#aaa';
            
            for(let i = 0; i < 2; i++) {
                setTimeout(() => spawnEnemy(), i * 800);
            }
        }
        
        // Управление
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            mouseX = (e.clientX - rect.left) * scaleX;
            mouseY = (e.clientY - rect.top) * scaleY;
            mouseX = Math.min(Math.max(mouseX, 0), canvasWidth);
            mouseY = Math.min(Math.max(mouseY, 0), canvasHeight);
        });
        
        canvas.addEventListener('click', (e) => {
            e.preventDefault();
            if (!gameRunning) return;
            if (shootCooldown <= 0) {
                shootMissile();
                shootCooldown = shootDelay;
                if (navigator.vibrate) navigator.vibrate(30);
            }
        });
        
        startBtn.addEventListener('click', startGame);
        
        gameLoop();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

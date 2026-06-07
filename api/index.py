from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Tanki Battle | Akuma Game</title>
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
            cursor: none;
            background: #2a2a3a;
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
                <p>УНИЧТОЖЕНО</p>
            </div>
            <div class="health-box">
                <span id="health">❤️ 100</span>
                <p>ЗДОРОВЬЕ</p>
            </div>
        </div>
        
        <button class="start-btn" id="startBtn">🚀 НАЧАТЬ БИТВУ</button>
        <div class="controls">
            <span>🖱️ МЫШЬ — ПРИЦЕЛ</span>
            <span>🔫 ЛКМ / КЛИК — СТРЕЛЯТЬ</span>
            <span>⬅️➡️ A/D — ДВИЖЕНИЕ</span>
        </div>
        <div class="status" id="status">🔫 Уничтожай вражеские танки!</div>
        
        <div class="footer">
            <p>🎮 Враги появляются волнами. За каждые 5 убийств — новая волна!</p>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 700;
        const canvasHeight = 500;
        
        // Игрок (танк)
        let player = {
            x: canvasWidth / 2 - 25,
            y: canvasHeight - 80,
            width: 50,
            height: 50,
            health: 100,
            maxHealth: 100
        };
        
        // Пули
        let bullets = [];
        let bulletSpeed = 8;
        let shootCooldown = 0;
        let shootDelay = 12;
        
        // Враги
        let enemies = [];
        let enemySpawnCounter = 0;
        let enemySpawnDelay = 60;
        let wave = 1;
        let kills = 0;
        let score = 0;
        
        // Мышь
        let mouseX = canvasWidth / 2;
        let mouseY = canvasHeight / 2;
        
        let gameRunning = false;
        let gameOver = false;
        
        // Элементы DOM
        const scoreElement = document.getElementById('score');
        const killsElement = document.getElementById('kills');
        const healthElement = document.getElementById('health');
        const startBtn = document.getElementById('startBtn');
        const statusElement = document.getElementById('status');
        
        // Движение танка
        let leftPressed = false;
        let rightPressed = false;
        
        // Класс врага
        class Enemy {
            constructor(x, y, type) {
                this.x = x;
                this.y = y;
                this.width = 45;
                this.height = 45;
                this.type = type || 'normal';
                this.health = this.type === 'heavy' ? 3 : 1;
                this.speed = this.type === 'fast' ? 2.5 : 1.5;
            }
            
            move() {
                this.y += this.speed;
            }
            
            draw() {
                ctx.save();
                ctx.shadowBlur = 0;
                
                if (this.type === 'heavy') {
                    ctx.fillStyle = '#8B0000';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = '#660000';
                    ctx.fillRect(this.x + 5, this.y + 5, this.width - 10, 10);
                    ctx.fillRect(this.x + 5, this.y + this.height - 15, this.width - 10, 10);
                    // Гусеницы
                    ctx.fillStyle = '#444';
                    ctx.fillRect(this.x - 5, this.y + 10, 5, 25);
                    ctx.fillRect(this.x + this.width, this.y + 10, 5, 25);
                    ctx.fillStyle = '#fff';
                    ctx.font = 'bold 14px Arial';
                    ctx.fillText('💪', this.x + 15, this.y + 30);
                } else if (this.type === 'fast') {
                    ctx.fillStyle = '#D2691E';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = '#B8860B';
                    ctx.fillRect(this.x + 5, this.y + 5, this.width - 10, 10);
                    ctx.fillRect(this.x + 5, this.y + this.height - 15, this.width - 10, 10);
                    ctx.fillStyle = '#444';
                    ctx.fillRect(this.x - 5, this.y + 10, 5, 25);
                    ctx.fillRect(this.x + this.width, this.y + 10, 5, 25);
                    ctx.fillStyle = '#fff';
                    ctx.font = 'bold 14px Arial';
                    ctx.fillText('⚡', this.x + 15, this.y + 30);
                } else {
                    ctx.fillStyle = '#DC143C';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = '#8B0000';
                    ctx.fillRect(this.x + 5, this.y + 5, this.width - 10, 10);
                    ctx.fillRect(this.x + 5, this.y + this.height - 15, this.width - 10, 10);
                    ctx.fillStyle = '#444';
                    ctx.fillRect(this.x - 5, this.y + 10, 5, 25);
                    ctx.fillRect(this.x + this.width, this.y + 10, 5, 25);
                }
                
                ctx.restore();
            }
        }
        
        function initGame() {
            player.health = 100;
            player.x = canvasWidth / 2 - 25;
            bullets = [];
            enemies = [];
            wave = 1;
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
            const rand = Math.random();
            let type = 'normal';
            if (wave >= 3 && rand < 0.3) type = 'heavy';
            else if (wave >= 2 && rand < 0.5) type = 'fast';
            
            const x = Math.random() * (canvasWidth - 45);
            enemies.push(new Enemy(x, -45, type));
        }
        
        function shoot() {
            if (!gameRunning) return;
            bullets.push({
                x: player.x + player.width / 2 - 3,
                y: player.y - 10,
                width: 6,
                height: 12,
                targetX: mouseX,
                targetY: mouseY
            });
        }
        
        function update() {
            if (!gameRunning || gameOver) return;
            
            // Движение танка
            if (leftPressed && player.x > 0) player.x -= 5;
            if (rightPressed && player.x < canvasWidth - player.width) player.x += 5;
            
            // Перезарядка
            if (shootCooldown > 0) shootCooldown--;
            
            // Пули
            for (let i = 0; i < bullets.length; i++) {
                bullets[i].y -= bulletSpeed;
                if (bullets[i].y + bullets[i].height < 0) {
                    bullets.splice(i, 1);
                    i--;
                }
            }
            
            // Враги
            for (let i = 0; i < enemies.length; i++) {
                enemies[i].move();
                
                // Проверка столкновения с игроком
                if (enemies[i].x < player.x + player.width &&
                    enemies[i].x + enemies[i].width > player.x &&
                    enemies[i].y < player.y + player.height &&
                    enemies[i].y + enemies[i].height > player.y) {
                    
                    const damage = enemies[i].type === 'heavy' ? 20 : 10;
                    player.health -= damage;
                    healthElement.innerText = '❤️ ' + Math.max(0, player.health);
                    enemies.splice(i, 1);
                    i--;
                    
                    if (player.health <= 0) {
                        gameRunning = false;
                        gameOver = true;
                        statusElement.innerHTML = '💀 ТАНК УНИЧТОЖЕН! ИГРА ОКОНЧЕНА 💀';
                        statusElement.style.color = '#ff6666';
                        startBtn.style.display = 'block';
                        return;
                    }
                    continue;
                }
                
                // Проверка столкновения пуль с врагами
                for (let j = 0; j < bullets.length; j++) {
                    if (bullets[j].x < enemies[i].x + enemies[i].width &&
                        bullets[j].x + bullets[j].width > enemies[i].x &&
                        bullets[j].y < enemies[i].y + enemies[i].height &&
                        bullets[j].y + bullets[j].height > enemies[i].y) {
                        
                        bullets.splice(j, 1);
                        enemies[i].health--;
                        
                        if (enemies[i].health <= 0) {
                            const points = enemies[i].type === 'heavy' ? 30 : enemies[i].type === 'fast' ? 20 : 10;
                            score += points;
                            kills++;
                            scoreElement.innerText = score;
                            killsElement.innerText = kills;
                            enemies.splice(i, 1);
                            
                            // Новая волна
                            if (kills % 5 === 0 && kills > 0) {
                                wave++;
                                statusElement.innerHTML = `🌊 ВОЛНА ${wave}! Враги сильнее! 🌊`;
                                setTimeout(() => {
                                    if (gameRunning) statusElement.innerHTML = '🔫 Уничтожай вражеские танки!';
                                }, 1500);
                            }
                        }
                        break;
                    }
                }
            }
            
            // Спавн врагов
            let enemiesToSpawn = Math.min(3 + Math.floor(wave / 2), 8);
            if (enemies.length < enemiesToSpawn) {
                enemySpawnCounter++;
                if (enemySpawnCounter > enemySpawnDelay) {
                    spawnEnemy();
                    enemySpawnCounter = 0;
                    enemySpawnDelay = Math.max(40, 60 - wave);
                }
            }
        }
        
        function draw() {
            // Фон
            ctx.fillStyle = '#2a2a3a';
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Земля
            ctx.fillStyle = '#3a3a4a';
            ctx.fillRect(0, canvasHeight - 60, canvasWidth, 60);
            ctx.fillStyle = '#4a4a5a';
            for(let i = 0; i < 20; i++) {
                ctx.fillRect(i * 40, canvasHeight - 55, 20, 5);
            }
            
            // Прицел
            ctx.beginPath();
            ctx.strokeStyle = '#ffcc00';
            ctx.lineWidth = 2;
            ctx.arc(mouseX, mouseY, 10, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(mouseX - 15, mouseY);
            ctx.lineTo(mouseX - 5, mouseY);
            ctx.moveTo(mouseX + 5, mouseY);
            ctx.lineTo(mouseX + 15, mouseY);
            ctx.moveTo(mouseX, mouseY - 15);
            ctx.lineTo(mouseX, mouseY - 5);
            ctx.moveTo(mouseX, mouseY + 5);
            ctx.lineTo(mouseX, mouseY + 15);
            ctx.stroke();
            
            // Пули
            for (let bullet of bullets) {
                ctx.fillStyle = '#ffcc00';
                ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
            }
            
            // Враги
            for (let enemy of enemies) {
                enemy.draw();
            }
            
            // Танк игрока
            ctx.save();
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#228B22';
            ctx.fillRect(player.x, player.y, player.width, player.height);
            ctx.fillStyle = '#006400';
            ctx.fillRect(player.x + 5, player.y + 5, player.width - 10, 10);
            ctx.fillRect(player.x + 5, player.y + player.height - 15, player.width - 10, 10);
            ctx.fillStyle = '#444';
            ctx.fillRect(player.x - 5, player.y + 10, 5, 30);
            ctx.fillRect(player.x + player.width, player.y + 10, 5, 30);
            
            // Башня (поворачивается к мышке)
            const angle = Math.atan2(mouseY - (player.y + player.height/2), mouseX - (player.x + player.width/2));
            ctx.translate(player.x + player.width/2, player.y + player.height/2);
            ctx.rotate(angle);
            ctx.fillStyle = '#2E8B57';
            ctx.fillRect(-12, -12, 24, 24);
            ctx.fillStyle = '#ffcc00';
            ctx.fillRect(-3, -20, 6, 15);
            ctx.restore();
            
            // Полоска здоровья
            ctx.fillStyle = '#ff4444';
            ctx.fillRect(player.x, player.y - 10, player.width, 5);
            ctx.fillStyle = '#44ff44';
            ctx.fillRect(player.x, player.y - 10, player.width * (player.health / player.maxHealth), 5);
            
            // Волна
            ctx.font = 'bold 20px Arial';
            ctx.fillStyle = '#ffcc00';
            ctx.shadowBlur = 3;
            ctx.fillText(`ВОЛНА ${wave}`, canvasWidth - 100, 40);
            ctx.font = '12px Arial';
            ctx.fillStyle = '#aaa';
            ctx.fillText(`Убийств: ${kills}`, canvasWidth - 100, 65);
            ctx.shadowBlur = 0;
            
            if (!gameRunning && !gameOver) {
                ctx.font = 'bold 24px Arial';
                ctx.fillStyle = '#fff';
                ctx.fillText('ТАНКИ БИТВА', canvasWidth / 2 - 100, canvasHeight / 2 - 50);
                ctx.font = '16px Arial';
                ctx.fillText('Нажмите "НАЧАТЬ БИТВУ"', canvasWidth / 2 - 110, canvasHeight / 2);
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
            statusElement.innerHTML = '🔫 Уничтожай вражеские танки!';
            statusElement.style.color = '#aaa';
            
            // Первые враги
            for(let i = 0; i < 3; i++) {
                setTimeout(() => spawnEnemy(), i * 500);
            }
        }
        
        // Управление
        document.addEventListener('mousemove', (e) => {
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
                shoot();
                shootCooldown = shootDelay;
                if (navigator.vibrate) navigator.vibrate(20);
            }
        });
        
        // Движение танка
        document.addEventListener('keydown', (e) => {
            if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') {
                leftPressed = true;
                e.preventDefault();
            }
            if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') {
                rightPressed = true;
                e.preventDefault();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') {
                leftPressed = false;
            }
            if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') {
                rightPressed = false;
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

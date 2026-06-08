from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Super Mario Bros | Classic Platformer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        
        .game-wrapper {
            background: #000;
            padding: 10px;
            border-radius: 16px;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            border-radius: 8px;
            cursor: pointer;
        }
        
        .info-panel {
            margin-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background: rgba(0,0,0,0.7);
            border-radius: 12px;
            color: white;
        }
        
        .info-box {
            background: rgba(0,0,0,0.5);
            padding: 5px 20px;
            border-radius: 20px;
            text-align: center;
        }
        
        .info-box span {
            color: #ffcc00;
            font-size: 28px;
            font-weight: bold;
            display: block;
        }
        
        .info-box p {
            font-size: 10px;
            color: #aaa;
        }
        
        .start-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 10px 30px;
            border-radius: 30px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .start-btn:active {
            transform: scale(0.95);
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        
        .ctrl-btn {
            background: rgba(0,0,0,0.6);
            border: 1px solid #ffcc00;
            padding: 8px 25px;
            border-radius: 30px;
            color: #ffcc00;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            font-family: monospace;
            transition: 0.1s;
        }
        
        .ctrl-btn:active {
            background: #ffcc00;
            color: #1a1a2e;
            transform: scale(0.95);
        }
        
        .game-status {
            text-align: center;
            margin-top: 10px;
            color: #ffcc00;
            font-size: 14px;
            font-weight: bold;
        }
        
        @media (max-width: 850px) {
            canvas {
                width: 100%;
                height: auto;
            }
            .ctrl-btn {
                padding: 6px 20px;
                font-size: 12px;
            }
            .info-box span {
                font-size: 22px;
            }
        }
    </style>
</head>
<body>
    <div>
        <div class="game-wrapper">
            <canvas id="gameCanvas" width="800" height="400"></canvas>
        </div>
        <div class="info-panel">
            <div class="info-box">
                <p>WORLD</p>
                <span>1-1</span>
            </div>
            <div class="info-box">
                <p>SCORE</p>
                <span id="score">0</span>
            </div>
            <div class="info-box">
                <p>COINS</p>
                <span id="coins">0</span>
            </div>
            <button class="start-btn" id="startBtn">🌟 START</button>
        </div>
        <div class="controls">
            <div class="ctrl-btn" id="leftBtn">◀ L</div>
            <div class="ctrl-btn" id="rightBtn">R ▶</div>
            <div class="ctrl-btn" id="jumpBtn">JUMP ⬆</div>
        </div>
        <div class="game-status" id="gameStatus">🏁 НАЖМИ START, ЧТОБЫ ИГРАТЬ! 🏁</div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 800;
        const canvasHeight = 400;
        const gravity = 0.6;
        const jumpPower = -9.5;
        
        // МАРИО
        let player = {
            x: 80,
            y: 300,
            width: 30,
            height: 30,
            vx: 0,
            vy: 0,
            onGround: true,
            facingRight: true,
            invincible: 0,
            size: 'big'
        };
        
        // ПЛАТФОРМЫ
        let platforms = [
            { x: 0, y: 360, width: 800, height: 40 },  // земля
            { x: 120, y: 310, width: 70, height: 20 },
            { x: 250, y: 270, width: 70, height: 20 },
            { x: 380, y: 310, width: 70, height: 20 },
            { x: 520, y: 270, width: 70, height: 20 },
            { x: 650, y: 310, width: 70, height: 20 },
            { x: 200, y: 220, width: 60, height: 20 },
            { x: 450, y: 220, width: 60, height: 20 },
            { x: 600, y: 200, width: 60, height: 20 },
            { x: 700, y: 260, width: 50, height: 20 }
        ];
        
        // МОНЕТЫ
        let coins = [];
        
        // ВРАГИ
        let enemies = [];
        
        let score = 0;
        let coinsCollected = 0;
        let gameRunning = false;
        let gameOver = false;
        let cameraX = 0;
        
        // УПРАВЛЕНИЕ
        let leftPressed = false;
        let rightPressed = false;
        let jumpRequested = false;
        
        // АНИМАЦИЯ
        let frame = 0;
        let walkCycle = 0;
        
        const scoreElement = document.getElementById('score');
        const coinsElement = document.getElementById('coins');
        const startBtn = document.getElementById('startBtn');
        const gameStatus = document.getElementById('gameStatus');
        
        function initGame() {
            // Монеты
            coins = [];
            for (let i = 0; i < 25; i++) {
                coins.push({
                    x: 60 + Math.random() * 700,
                    y: 100 + Math.random() * 250,
                    width: 10,
                    height: 10,
                    collected: false
                });
            }
            // Фиксированные монеты на платформах
            const fixedCoins = [
                { x: 145, y: 285 }, { x: 160, y: 285 },
                { x: 275, y: 245 }, { x: 290, y: 245 },
                { x: 405, y: 285 }, { x: 420, y: 285 },
                { x: 545, y: 245 }, { x: 560, y: 245 },
                { x: 675, y: 285 }, { x: 690, y: 285 },
                { x: 225, y: 195 }, { x: 240, y: 195 },
                { x: 475, y: 195 }, { x: 490, y: 195 },
                { x: 625, y: 175 }, { x: 640, y: 175 }
            ];
            fixedCoins.forEach(c => {
                coins.push({
                    x: c.x, y: c.y, width: 10, height: 10, collected: false
                });
            });
            
            // Враги (Гумбы)
            enemies = [
                { x: 300, y: 340, width: 28, height: 28, alive: true, direction: -1 },
                { x: 500, y: 340, width: 28, height: 28, alive: true, direction: 1 },
                { x: 650, y: 340, width: 28, height: 28, alive: true, direction: -1 },
                { x: 200, y: 280, width: 28, height: 28, alive: true, direction: 1 },
                { x: 550, y: 280, width: 28, height: 28, alive: true, direction: -1 }
            ];
            
            player = {
                x: 80,
                y: 300,
                width: 30,
                height: 30,
                vx: 0,
                vy: 0,
                onGround: true,
                facingRight: true,
                invincible: 0,
                size: 'big'
            };
            
            score = 0;
            coinsCollected = 0;
            gameOver = false;
            cameraX = 0;
            walkCycle = 0;
            
            scoreElement.innerText = '0';
            coinsElement.innerText = '0';
            gameStatus.innerHTML = '🎮 ИГРА ИДЁТ! СОБИРАЙ МОНЕТЫ! 🎮';
            gameStatus.style.color = '#ffcc00';
        }
        
        function checkCollisions() {
            // Горизонтальное движение
            player.x += player.vx;
            
            // Коллизия с платформами (по X)
            for (let platform of platforms) {
                if (player.x < platform.x + platform.width &&
                    player.x + player.width > platform.x &&
                    player.y + player.height > platform.y &&
                    player.y < platform.y + platform.height) {
                    if (player.vx > 0) {
                        player.x = platform.x - player.width;
                    } else if (player.vx < 0) {
                        player.x = platform.x + platform.width;
                    }
                }
            }
            
            // Гравитация
            player.vy += gravity;
            player.y += player.vy;
            player.onGround = false;
            
            // Коллизия с платформами (по Y)
            for (let platform of platforms) {
                if (player.x < platform.x + platform.width &&
                    player.x + player.width > platform.x &&
                    player.y + player.height > platform.y &&
                    player.y < platform.y + platform.height) {
                    if (player.vy >= 0) {
                        player.y = platform.y - player.height;
                        player.vy = 0;
                        player.onGround = true;
                    } else if (player.vy < 0) {
                        player.y = platform.y + platform.height;
                        player.vy = 0;
                    }
                }
            }
            
            // Монеты
            for (let coin of coins) {
                if (!coin.collected &&
                    player.x < coin.x + coin.width &&
                    player.x + player.width > coin.x &&
                    player.y < coin.y + coin.height &&
                    player.y + player.height > coin.y) {
                    coin.collected = true;
                    coinsCollected++;
                    score += 10;
                    scoreElement.innerText = score;
                    coinsElement.innerText = coinsCollected;
                }
            }
            
            // Враги
            for (let i = 0; i < enemies.length; i++) {
                let e = enemies[i];
                if (!e.alive) continue;
                
                // Движение врага
                e.x += e.direction * 1.2;
                if (e.x < 50 || e.x > 750) e.direction *= -1;
                
                // Столкновение с игроком
                if (player.x < e.x + e.width &&
                    player.x + player.width > e.x &&
                    player.y < e.y + e.height &&
                    player.y + player.height > e.y) {
                    
                    if (player.vy > 0 && player.y + player.height - e.y < 15) {
                        // Игрок прыгнул на врага
                        e.alive = false;
                        player.vy = -6;
                        score += 20;
                        scoreElement.innerText = score;
                    } else {
                        // Враг ударил игрока
                        if (player.invincible <= 0) {
                            player.invincible = 60;
                            if (player.size === 'big') {
                                player.size = 'small';
                                player.height = 20;
                                player.y += 10;
                            } else {
                                gameOver = true;
                                gameRunning = false;
                                gameStatus.innerHTML = '💀 GAME OVER! НАЖМИ START 💀';
                                gameStatus.style.color = '#ff6666';
                            }
                        }
                    }
                }
            }
            
            // Неуязвимость
            if (player.invincible > 0) {
                player.invincible--;
            }
            
            // Границы мира
            if (player.x < 20) player.x = 20;
            if (player.x > 750) player.x = 750;
            if (player.y > 400) {
                gameOver = true;
                gameRunning = false;
                gameStatus.innerHTML = '💀 GAME OVER! НАЖМИ START 💀';
                gameStatus.style.color = '#ff6666';
            }
            
            // Камера
            cameraX = Math.min(Math.max(player.x - 300, 0), 400);
            
            // Победа по монетам
            if (coinsCollected >= 20) {
                gameRunning = false;
                gameStatus.innerHTML = '🎉 ПОБЕДА! ТЫ СОБРАЛ ВСЕ МОНЕТЫ! 🎉';
                gameStatus.style.color = '#44ff44';
            }
        }
        
        function draw() {
            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            
            // Небо
            const grad = ctx.createLinearGradient(0, 0, 0, canvasHeight);
            grad.addColorStop(0, '#5c9eff');
            grad.addColorStop(1, '#8fcbff');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Облака
            ctx.fillStyle = 'rgba(255,255,255,0.8)';
            ctx.beginPath();
            ctx.ellipse(100 + cameraX * 0.3, 60, 40, 30, 0, 0, Math.PI*2);
            ctx.ellipse(140 + cameraX * 0.3, 50, 35, 25, 0, 0, Math.PI*2);
            ctx.ellipse(60 + cameraX * 0.3, 50, 35, 25, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(500 + cameraX * 0.2, 80, 50, 35, 0, 0, Math.PI*2);
            ctx.ellipse(550 + cameraX * 0.2, 70, 40, 30, 0, 0, Math.PI*2);
            ctx.ellipse(460 + cameraX * 0.2, 70, 40, 30, 0, 0, Math.PI*2);
            ctx.fill();
            
            // Платформы (кирпичики)
            for (let platform of platforms) {
                ctx.fillStyle = '#8B5A2B';
                ctx.fillRect(platform.x - cameraX, platform.y, platform.width, platform.height);
                ctx.fillStyle = '#A06B3A';
                for (let i = 0; i < platform.width; i += 20) {
                    ctx.fillRect(platform.x - cameraX + i, platform.y, 18, 5);
                }
            }
            
            // Монеты
            for (let coin of coins) {
                if (!coin.collected) {
                    ctx.fillStyle = '#ffcc00';
                    ctx.beginPath();
                    ctx.ellipse(coin.x - cameraX + 5, coin.y + 5, 6, 6, 0, 0, Math.PI*2);
                    ctx.fill();
                    ctx.fillStyle = '#ffaa00';
                    ctx.beginPath();
                    ctx.ellipse(coin.x - cameraX + 5, coin.y + 5, 4, 4, 0, 0, Math.PI*2);
                    ctx.fill();
                    ctx.fillStyle = '#ffdd66';
                    ctx.fillText('★', coin.x - cameraX + 2, coin.y + 9);
                }
            }
            
            // Враги (Гумбы)
            for (let enemy of enemies) {
                if (enemy.alive) {
                    // Тело
                    ctx.fillStyle = '#8B4513';
                    ctx.fillRect(enemy.x - cameraX, enemy.y, enemy.width, enemy.height);
                    ctx.fillStyle = '#A0522D';
                    ctx.fillRect(enemy.x - cameraX + 4, enemy.y, 20, 15);
                    // Глаза
                    ctx.fillStyle = 'white';
                    ctx.fillRect(enemy.x - cameraX + 6, enemy.y + 5, 6, 6);
                    ctx.fillRect(enemy.x - cameraX + 16, enemy.y + 5, 6, 6);
                    ctx.fillStyle = 'black';
                    ctx.fillRect(enemy.x - cameraX + 8, enemy.y + 7, 3, 3);
                    ctx.fillRect(enemy.x - cameraX + 18, enemy.y + 7, 3, 3);
                    // Брови
                    ctx.fillStyle = '#5a2a1a';
                    ctx.fillRect(enemy.x - cameraX + 6, enemy.y + 3, 6, 3);
                    ctx.fillRect(enemy.x - cameraX + 16, enemy.y + 3, 6, 3);
                }
            }
            
            // МАРИО
            walkCycle = (walkCycle + 0.2) % 4;
            let bodyColor = '#E52525';
            if (player.invincible > 0 && Math.floor(Date.now() / 50) % 2 === 0) {
                bodyColor = '#FFFFFF';
            }
            
            // Тело
            ctx.fillStyle = bodyColor;
            ctx.fillRect(player.x - cameraX, player.y, player.width, player.height);
            
            // Лицо
            ctx.fillStyle = '#FFDAB9';
            ctx.fillRect(player.x - cameraX + 5, player.y + 5, 20, 15);
            
            // Глаза
            ctx.fillStyle = 'white';
            ctx.fillRect(player.x - cameraX + 8, player.y + 8, 6, 6);
            ctx.fillRect(player.x - cameraX + 18, player.y + 8, 6, 6);
            ctx.fillStyle = 'black';
            ctx.fillRect(player.x - cameraX + 10, player.y + 10, 3, 3);
            ctx.fillRect(player.x - cameraX + 20, player.y + 10, 3, 3);
            
            // Усы
            ctx.fillStyle = '#8B4513';
            ctx.fillRect(player.x - cameraX + 12, player.y + 15, 8, 3);
            ctx.fillRect(player.x - cameraX + 16, player.y + 14, 4, 4);
            
            // Шляпа
            ctx.fillStyle = '#E52525';
            ctx.fillRect(player.x - cameraX + 2, player.y - 5, 26, 8);
            ctx.fillStyle = '#C41E1E';
            ctx.fillRect(player.x - cameraX + 12, player.y - 8, 8, 10);
            
            // Кепка
            ctx.fillStyle = '#C41E1E';
            ctx.fillRect(player.x - cameraX + 2, player.y - 8, 26, 5);
            
            // Ботинки
            ctx.fillStyle = '#8B4513';
            ctx.fillRect(player.x - cameraX + 5, player.y + player.height - 5, 10, 8);
            ctx.fillRect(player.x - cameraX + 17, player.y + player.height - 5, 10, 8);
            
            // Ноги при ходьбе
            if (Math.abs(player.vx) > 0.5 && player.onGround) {
                ctx.fillStyle = '#8B4513';
                if (walkCycle < 2) {
                    ctx.fillRect(player.x - cameraX + 5, player.y + player.height - 3, 8, 8);
                    ctx.fillRect(player.x - cameraX + 19, player.y + player.height - 8, 8, 8);
                } else {
                    ctx.fillRect(player.x - cameraX + 5, player.y + player.height - 8, 8, 8);
                    ctx.fillRect(player.x - cameraX + 19, player.y + player.height - 3, 8, 8);
                }
            }
            
            // Счёт на экране
            ctx.font = 'bold 16px "Courier New"';
            ctx.fillStyle = 'white';
            ctx.shadowBlur = 3;
            ctx.fillText('SCORE: ' + score, canvasWidth - 150, 30);
            ctx.fillText('x ' + coinsCollected, canvasWidth - 70, 30);
            ctx.fillStyle = '#ffcc00';
            ctx.fillText('★', canvasWidth - 90, 32);
            ctx.shadowBlur = 0;
        }
        
        function update() {
            if (!gameRunning) return;
            
            // Управление
            if (leftPressed) {
                player.vx = -4;
                player.facingRight = false;
            } else if (rightPressed) {
                player.vx = 4;
                player.facingRight = true;
            } else {
                player.vx *= 0.8;
            }
            
            if (jumpRequested && player.onGround) {
                player.vy = jumpPower;
                player.onGround = false;
                jumpRequested = false;
            }
            
            checkCollisions();
        }
        
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // УПРАВЛЕНИЕ (клавиатура)
        document.addEventListener('keydown', (e) => {
            if (!gameRunning) return;
            if (e.key === 'ArrowLeft') { leftPressed = true; e.preventDefault(); }
            if (e.key === 'ArrowRight') { rightPressed = true; e.preventDefault(); }
            if (e.key === 'ArrowUp') { jumpRequested = true; e.preventDefault(); }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft') leftPressed = false;
            if (e.key === 'ArrowRight') rightPressed = false;
        });
        
        // КНОПКИ ДЛЯ ТЕЛЕФОНА
        document.getElementById('leftBtn').addEventListener('touchstart', (e) => { e.preventDefault(); leftPressed = true; });
        document.getElementById('leftBtn').addEventListener('touchend', () => { leftPressed = false; });
        document.getElementById('leftBtn').addEventListener('mousedown', () => { leftPressed = true; });
        document.getElementById('leftBtn').addEventListener('mouseup', () => { leftPressed = false; });
        
        document.getElementById('rightBtn').addEventListener('touchstart', (e) => { e.preventDefault(); rightPressed = true; });
        document.getElementById('rightBtn').addEventListener('touchend', () => { rightPressed = false; });
        document.getElementById('rightBtn').addEventListener('mousedown', () => { rightPressed = true; });
        document.getElementById('rightBtn').addEventListener('mouseup', () => { rightPressed = false; });
        
        document.getElementById('jumpBtn').addEventListener('touchstart', (e) => { e.preventDefault(); jumpRequested = true; });
        document.getElementById('jumpBtn').addEventListener('mousedown', () => { jumpRequested = true; });
        
        function startGame() {
            initGame();
            gameRunning = true;
            gameOver = false;
        }
        
        startBtn.addEventListener('click', startGame);
        
        // Стартовый экран
        initGame();
        gameLoop();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

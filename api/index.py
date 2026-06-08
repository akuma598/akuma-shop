from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>NEON DASH | Хардкорная аркада</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            background: #050510;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Press Start 2P', 'Courier New', monospace;
            overflow: hidden;
        }
        
        .game-wrapper {
            position: relative;
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            border-radius: 0;
            cursor: pointer;
            box-shadow: 0 0 50px rgba(0,255,255,0.3);
        }
        
        .ui {
            position: absolute;
            top: 20px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            padding: 0 30px;
            pointer-events: none;
            z-index: 10;
        }
        
        .ui-box {
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
            padding: 10px 25px;
            border-radius: 10px;
            border-left: 4px solid #00ffff;
            font-family: monospace;
        }
        
        .ui-box span {
            color: #00ffff;
            font-size: 28px;
            font-weight: bold;
        }
        
        .ui-box p {
            color: #aaa;
            font-size: 10px;
            letter-spacing: 2px;
        }
        
        .start-screen {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(15px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }
        
        .game-title {
            font-size: 48px;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 20px #00ffff, 0 0 40px #0066ff;
            margin-bottom: 20px;
            letter-spacing: 5px;
        }
        
        .start-btn {
            background: linear-gradient(135deg, #00ffff, #0066ff);
            border: none;
            padding: 15px 50px;
            border-radius: 50px;
            color: white;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 30px;
            font-family: monospace;
            box-shadow: 0 0 20px #00ffff;
        }
        
        .start-btn:active {
            transform: scale(0.95);
        }
        
        .instructions {
            position: absolute;
            bottom: 30px;
            left: 0;
            right: 0;
            text-align: center;
            color: #888;
            font-size: 10px;
            font-family: monospace;
        }
        
        @media (max-width: 768px) {
            .game-title { font-size: 28px; }
            .ui-box span { font-size: 18px; }
            .ui-box { padding: 5px 15px; }
        }
    </style>
</head>
<body>
    <div class="game-wrapper">
        <canvas id="gameCanvas" width="800" height="400"></canvas>
        
        <div class="ui">
            <div class="ui-box">
                <span id="score">0</span>
                <p>SCORE</p>
            </div>
            <div class="ui-box">
                <span id="best">0</span>
                <p>BEST</p>
            </div>
        </div>
        
        <div class="start-screen" id="startScreen">
            <div class="game-title">⚡ NEON DASH ⚡</div>
            <button class="start-btn" id="startBtn">▶ СТАРТ</button>
            <div class="instructions">🔥 ТАПАЙ / ПРОБЕЛ — ПРЫЖОК | НЕ ВРЕЗАЙСЯ В ПРЕПЯТСТВИЯ 🔥</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 800;
        const canvasHeight = 400;
        const groundY = 330;
        
        let score = 0;
        let bestScore = localStorage.getItem('neonBest') || 0;
        let gameRunning = false;
        let gameSpeed = 6;
        let speedMultiplier = 1;
        
        // Игрок (квадратик с глазками)
        let player = {
            x: 100,
            y: groundY - 30,
            width: 30,
            height: 30,
            vy: 0,
            onGround: true,
            rotation: 0,
            trail: []
        };
        
        // Препятствия
        let obstacles = [];
        let frameCounter = 0;
        let particles = [];
        let nextObstacle = 60;
        
        // Параллакс
        let bgOffset = 0;
        let stars = [];
        
        for(let i=0;i<150;i++) {
            stars.push({
                x: Math.random() * canvasWidth,
                y: Math.random() * canvasHeight,
                size: Math.random() * 3 + 1,
                speed: Math.random() * 2 + 0.5
            });
        }
        
        const scoreElement = document.getElementById('score');
        const bestElement = document.getElementById('best');
        const startScreen = document.getElementById('startScreen');
        const startBtn = document.getElementById('startBtn');
        
        bestElement.innerText = bestScore;
        
        class Obstacle {
            constructor(x, type) {
                this.x = x;
                this.type = type;
                this.passed = false;
                this.width = 25;
                this.height = 35;
                
                if(type === 'spike') {
                    this.width = 25;
                    this.height = 25;
                    this.y = groundY - 25;
                } else if(type === 'block') {
                    this.width = 30;
                    this.height = 40;
                    this.y = groundY - 40;
                } else if(type === 'double') {
                    this.width = 20;
                    this.height = 35;
                    this.y = groundY - 35;
                    this.second = true;
                } else {
                    this.width = 28;
                    this.height = 38;
                    this.y = groundY - 38;
                }
            }
            
            draw() {
                if(this.type === 'spike') {
                    // Шипы
                    ctx.fillStyle = '#ff3366';
                    for(let i=0;i<3;i++) {
                        ctx.beginPath();
                        ctx.moveTo(this.x + i*9, this.y+this.height);
                        ctx.lineTo(this.x + i*9 + 4, this.y);
                        ctx.lineTo(this.x + i*9 + 8, this.y+this.height);
                        ctx.fill();
                    }
                } else if(this.type === 'block') {
                    // Куб с градиентом
                    const grad = ctx.createLinearGradient(this.x, this.y, this.x+this.width, this.y+this.height);
                    grad.addColorStop(0, '#ff0066');
                    grad.addColorStop(1, '#6600ff');
                    ctx.fillStyle = grad;
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(this.x+5, this.y+5, 5, 5);
                    ctx.fillRect(this.x+this.width-10, this.y+this.height-10, 5, 5);
                } else if(this.type === 'double') {
                    ctx.fillStyle = '#ffaa00';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillRect(this.x+this.width+5, this.y, this.width, this.height);
                } else {
                    ctx.fillStyle = '#00ffff';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(this.x+5, this.y+5, 5, 5);
                }
            }
            
            update() {
                this.x -= gameSpeed * speedMultiplier;
            }
        }
        
        function addParticle(x, y, color) {
            for(let i=0;i<8;i++) {
                particles.push({
                    x: x, y: y, vx: (Math.random() - 0.5) * 6,
                    vy: (Math.random() - 0.5) * 6 - 3,
                    life: 30, color: color, size: Math.random() * 4 + 2
                });
            }
        }
        
        function addTrail() {
            player.trail.push({ x: player.x + player.width/2, y: player.y + player.height/2, life: 15 });
            if(player.trail.length > 15) player.trail.shift();
        }
        
        function spawnObstacle() {
            const types = ['spike', 'block', 'normal', 'double', 'block'];
            const type = types[Math.floor(Math.random() * types.length)];
            obstacles.push(new Obstacle(canvasWidth, type));
            
            // Двойное препятствие иногда
            if(Math.random() < 0.3 && type !== 'double') {
                obstacles.push(new Obstacle(canvasWidth + 40, 'spike'));
            }
        }
        
        function resetGame() {
            score = 0;
            gameSpeed = 6;
            speedMultiplier = 1;
            obstacles = [];
            particles = [];
            player.trail = [];
            player.y = groundY - 30;
            player.vy = 0;
            player.onGround = true;
            player.rotation = 0;
            frameCounter = 0;
            scoreElement.innerText = '0';
        }
        
        function updateGame() {
            if(!gameRunning) return;
            
            // Гравитация
            player.vy += 0.8;
            player.y += player.vy;
            
            if(player.y >= groundY - player.height) {
                player.y = groundY - player.height;
                player.vy = 0;
                player.onGround = true;
            } else {
                player.onGround = false;
            }
            
            // Вращение при прыжке
            if(!player.onGround) {
                player.rotation += 0.2;
            } else {
                player.rotation = 0;
            }
            
            // Трейл при беге
            if(player.onGround && gameRunning) {
                addTrail();
            }
            
            // Спавн препятствий
            frameCounter++;
            let spawnDelay = Math.max(45, 70 - Math.floor(score / 200));
            if(frameCounter > spawnDelay) {
                spawnObstacle();
                frameCounter = 0;
            }
            
            // Обновление препятствий и коллизии
            for(let i=0;i<obstacles.length;i++) {
                obstacles[i].update();
                
                // Коллизия
                if(player.x < obstacles[i].x + obstacles[i].width &&
                    player.x + player.width > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].height &&
                    player.y + player.height > obstacles[i].y) {
                    
                    gameRunning = false;
                    if(score > bestScore) {
                        bestScore = score;
                        localStorage.setItem('neonBest', bestScore);
                        bestElement.innerText = bestScore;
                    }
                    startScreen.style.display = 'flex';
                    addParticle(player.x + player.width/2, player.y + player.height/2, '#ff0000');
                    return;
                }
                
                // Подсчёт очков
                if(!obstacles[i].passed && obstacles[i].x + obstacles[i].width < player.x) {
                    obstacles[i].passed = true;
                    score += 10;
                    scoreElement.innerText = score;
                    
                    // Увеличение скорости каждые 100 очков
                    speedMultiplier = 1 + Math.floor(score / 300) * 0.2;
                    if(speedMultiplier > 2) speedMultiplier = 2;
                    
                    addParticle(obstacles[i].x, obstacles[i].y, '#00ff00');
                }
                
                if(obstacles[i].x + obstacles[i].width < 0) {
                    obstacles.splice(i,1);
                    i--;
                }
            }
            
            // Партиклы
            for(let i=0;i<particles.length;i++) {
                particles[i].x += particles[i].vx;
                particles[i].y += particles[i].vy;
                particles[i].life--;
                if(particles[i].life <= 0) {
                    particles.splice(i,1);
                    i--;
                }
            }
            
            // Трейл
            for(let i=0;i<player.trail.length;i++) {
                player.trail[i].life--;
                if(player.trail[i].life <= 0) {
                    player.trail.splice(i,1);
                    i--;
                }
            }
            
            // Параллакс
            bgOffset = (bgOffset + gameSpeed * speedMultiplier) % canvasWidth;
        }
        
        function draw() {
            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            
            // Небо с градиентом
            const grad = ctx.createLinearGradient(0, 0, 0, canvasHeight);
            grad.addColorStop(0, '#050520');
            grad.addColorStop(1, '#0a0a3a');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Звёзды с мерцанием
            for(let star of stars) {
                ctx.fillStyle = `rgba(255,255,255,${0.5 + Math.sin(Date.now()*0.002)*0.3})`;
                ctx.fillRect(star.x, star.y, star.size, star.size);
            }
            
            // Луна
            ctx.fillStyle = '#ffeedd';
            ctx.shadowBlur = 30;
            ctx.shadowColor = '#00ffff';
            ctx.beginPath();
            ctx.arc(700, 60, 35, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = '#aaccff';
            ctx.beginPath();
            ctx.arc(690, 50, 8, 0, Math.PI*2);
            ctx.fill();
            ctx.shadowBlur = 0;
            
            // Земля с неоновой подсветкой
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, groundY, canvasWidth, canvasHeight - groundY);
            
            // Неоновые полоски на земле
            for(let i=0;i<20;i++) {
                ctx.fillStyle = `rgba(0,255,255,${0.3 + Math.sin(Date.now()*0.005 + i)*0.2})`;
                ctx.fillRect(i*50 + (bgOffset%50), groundY-3, 30, 3);
            }
            
            // Препятствия с неоновым свечением
            for(let obs of obstacles) {
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#00ffff';
                obs.draw();
            }
            ctx.shadowBlur = 0;
            
            // Трейл
            for(let t of player.trail) {
                ctx.fillStyle = `rgba(0,255,255,${t.life/15})`;
                ctx.beginPath();
                ctx.arc(t.x, t.y, 8, 0, Math.PI*2);
                ctx.fill();
            }
            
            // Партиклы
            for(let p of particles) {
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, p.size, p.size);
            }
            
            // Игрок (неоновый куб с глазками)
            ctx.save();
            ctx.translate(player.x + player.width/2, player.y + player.height/2);
            ctx.rotate(player.rotation);
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#00ffff';
            
            // Тело
            const gradPlayer = ctx.createLinearGradient(-15, -15, 15, 15);
            gradPlayer.addColorStop(0, '#00ffff');
            gradPlayer.addColorStop(1, '#0066ff');
            ctx.fillStyle = gradPlayer;
            ctx.fillRect(-15, -15, 30, 30);
            
            // Глаза
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(-8, -5, 6, 6);
            ctx.fillRect(2, -5, 6, 6);
            ctx.fillStyle = '#000000';
            ctx.fillRect(-6, -4, 3, 3);
            ctx.fillRect(4, -4, 3, 3);
            
            // Улыбка
            ctx.beginPath();
            ctx.arc(0, 5, 8, 0.1, Math.PI - 0.1);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            ctx.restore();
            
            // Эффект скорости (линии)
            if(gameRunning && gameSpeed * speedMultiplier > 8) {
                ctx.fillStyle = 'rgba(0,255,255,0.2)';
                for(let i=0;i<10;i++) {
                    ctx.fillRect(player.x - 10 - i*6, player.y + 10, 4, 15);
                }
            }
            
            // Счёт в неоне
            ctx.font = 'bold 20px "Courier New"';
            ctx.fillStyle = '#00ffff';
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#00ffff';
            ctx.fillText('⚡ ' + score, canvasWidth - 100, 50);
            ctx.fillText('🏆 ' + bestScore, canvasWidth - 100, 85);
            ctx.shadowBlur = 0;
        }
        
        function gameLoop() {
            updateGame();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Управление
        let jumpRequested = false;
        
        document.addEventListener('keydown', (e) => {
            if(!gameRunning && e.code === 'Space') {
                e.preventDefault();
                startBtn.click();
                return;
            }
            if(e.code === 'Space' || e.code === 'ArrowUp') {
                e.preventDefault();
                if(gameRunning && player.onGround) {
                    player.vy = -10;
                    player.onGround = false;
                    addParticle(player.x + player.width/2, player.y + player.height, '#00ffff');
                }
            }
        });
        
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if(!gameRunning) {
                startBtn.click();
                return;
            }
            if(gameRunning && player.onGround) {
                player.vy = -10;
                player.onGround = false;
                addParticle(player.x + player.width/2, player.y + player.height, '#00ffff');
            }
        });
        
        canvas.addEventListener('mousedown', (e) => {
            if(!gameRunning) {
                startBtn.click();
                return;
            }
            if(gameRunning && player.onGround) {
                player.vy = -10;
                player.onGround = false;
                addParticle(player.x + player.width/2, player.y + player.height, '#00ffff');
            }
        });
        
        function startGame() {
            resetGame();
            gameRunning = true;
            startScreen.style.display = 'none';
        }
        
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

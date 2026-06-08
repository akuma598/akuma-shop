from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>PARKOUR LEGENDS | Модная игра 2025</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Poppins', 'Courier New', monospace;
            overflow: hidden;
        }
        
        .game-container {
            position: relative;
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            border-radius: 20px;
            box-shadow: 0 0 40px rgba(0,0,0,0.5), 0 0 20px rgba(255,204,0,0.3);
            cursor: pointer;
        }
        
        .ui-overlay {
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
        
        .stat-card {
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
            padding: 12px 25px;
            border-radius: 30px;
            border: 1px solid rgba(255,204,0,0.5);
            font-family: monospace;
            text-align: center;
        }
        
        .stat-card span {
            color: #ffcc00;
            font-size: 28px;
            font-weight: bold;
            display: block;
        }
        
        .stat-card p {
            color: #aaa;
            font-size: 10px;
            letter-spacing: 2px;
        }
        
        .level-badge {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            padding: 8px 25px;
            border-radius: 40px;
            border: 1px solid #ffcc00;
            font-weight: bold;
            color: #ffcc00;
            font-size: 14px;
            letter-spacing: 2px;
            white-space: nowrap;
        }
        
        .controls-panel {
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 15px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
            border-radius: 60px;
            margin: 0 20px;
        }
        
        .ctrl-btn {
            background: rgba(0,0,0,0.7);
            border: 1px solid #ffcc00;
            padding: 12px 30px;
            border-radius: 40px;
            color: #ffcc00;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.1s;
            font-family: monospace;
            min-width: 100px;
            text-align: center;
        }
        
        .ctrl-btn:active {
            background: #ffcc00;
            color: #1a1a2e;
            transform: scale(0.95);
        }
        
        .start-screen {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(15px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 100;
            border-radius: 20px;
        }
        
        .game-title {
            font-size: 48px;
            font-weight: bold;
            background: linear-gradient(135deg, #ffcc00, #ff6600, #ff0066);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            text-shadow: 0 0 20px rgba(255,204,0,0.5);
        }
        
        .start-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 15px 50px;
            border-radius: 50px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 24px;
            cursor: pointer;
            transition: transform 0.2s;
            margin-top: 30px;
            font-family: monospace;
        }
        
        .start-btn:active {
            transform: scale(0.95);
        }
        
        .difficulty {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .difficulty-btn {
            background: rgba(255,255,255,0.1);
            border: 1px solid #ffcc00;
            padding: 8px 25px;
            border-radius: 30px;
            color: white;
            cursor: pointer;
            transition: 0.2s;
        }
        
        .difficulty-btn.active {
            background: #ffcc00;
            color: #1a1a2e;
        }
        
        .tip {
            position: absolute;
            bottom: 100px;
            left: 0;
            right: 0;
            text-align: center;
            color: #888;
            font-size: 12px;
            pointer-events: none;
        }
        
        @media (max-width: 768px) {
            .stat-card span { font-size: 20px; }
            .stat-card { padding: 8px 15px; }
            .ctrl-btn { padding: 8px 20px; font-size: 14px; min-width: 70px; }
            .game-title { font-size: 28px; }
            .start-btn { font-size: 18px; padding: 12px 35px; }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="900" height="500"></canvas>
        
        <div class="ui-overlay">
            <div class="stat-card">
                <span id="score">0</span>
                <p>SCORE</p>
            </div>
            <div class="stat-card">
                <span id="best">0</span>
                <p>BEST</p>
            </div>
        </div>
        
        <div class="level-badge" id="levelBadge">🔥 LEVEL 1 🔥</div>
        
        <div class="controls-panel">
            <div class="ctrl-btn" id="leftBtn">◀ L</div>
            <div class="ctrl-btn" id="rightBtn">R ▶</div>
            <div class="ctrl-btn" id="jumpBtn">JUMP ⬆</div>
            <div class="ctrl-btn" id="slideBtn">SLIDE ⬇</div>
        </div>
        
        <div class="tip">💡 ТАПАЙ — ПРЫЖОК | ДВОЙНОЙ ТАП — СЛАЙД | БЕГИ И НЕ ВРЕЗАЙСЯ!</div>
        
        <div class="start-screen" id="startScreen">
            <div class="game-title">🏃 PARKOUR LEGENDS 🏃</div>
            <div class="difficulty">
                <div class="difficulty-btn active" data-diff="easy">🎯 ЛЕГКИЙ</div>
                <div class="difficulty-btn" data-diff="normal">⚡ НОРМАЛ</div>
                <div class="difficulty-btn" data-diff="hard">🔥 ХАРДКОР</div>
                <div class="difficulty-btn" data-diff="extreme">💀 ЭКСТРИМ</div>
            </div>
            <button class="start-btn" id="startBtn">▶ СТАРТ</button>
            <p style="color:#888; margin-top: 20px; font-size: 12px;">ПРОБЕГИ МАКСИМАЛЬНОЕ РАССТОЯНИЕ!</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 900;
        const canvasHeight = 500;
        const groundY = 400;
        
        // Параметры игры
        let score = 0;
        let bestScore = localStorage.getItem('parkourBest') || 0;
        let gameRunning = false;
        let difficulty = 'normal';
        let level = 1;
        
        // Параметры сложности
        const difficultySettings = {
            easy: { speed: 5, obstacleFreq: 90, gapSize: 180, scoreMulti: 1 },
            normal: { speed: 7, obstacleFreq: 70, gapSize: 150, scoreMulti: 1.5 },
            hard: { speed: 9, obstacleFreq: 55, gapSize: 120, scoreMulti: 2 },
            extreme: { speed: 12, obstacleFreq: 40, gapSize: 90, scoreMulti: 3 }
        };
        
        let currentSpeed = difficultySettings.normal.speed;
        let obstacleFreq = difficultySettings.normal.obstacleFreq;
        let gapSize = difficultySettings.normal.gapSize;
        let scoreMulti = difficultySettings.normal.scoreMulti;
        
        // Игрок
        let player = {
            x: 150,
            y: groundY - 50,
            width: 35,
            height: 50,
            vy: 0,
            onGround: true,
            sliding: false,
            slideTimer: 0,
            invincible: 0,
            color: '#ff3366'
        };
        
        // Препятствия
        let obstacles = [];
        let frameCounter = 0;
        let particles = [];
        let bgOffset = 0;
        
        // Партиклы для эффектов
        let trail = [];
        
        // Управление
        let leftPressed = false;
        let rightPressed = false;
        let jumpRequested = false;
        let slideRequested = false;
        let lastTap = 0;
        
        const scoreElement = document.getElementById('score');
        const bestElement = document.getElementById('best');
        const levelBadge = document.getElementById('levelBadge');
        const startScreen = document.getElementById('startScreen');
        const startBtn = document.getElementById('startBtn');
        
        bestElement.innerText = bestScore;
        
        class Obstacle {
            constructor(x, type) {
                this.x = x;
                this.type = type;
                this.passed = false;
                
                if (type === 'wall') {
                    this.width = 30;
                    this.height = 80;
                    this.y = groundY - 80;
                } else if (type === 'spike') {
                    this.width = 40;
                    this.height = 30;
                    this.y = groundY - 30;
                } else if (type === 'hole') {
                    this.width = gapSize;
                    this.height = 10;
                    this.y = groundY;
                } else if (type === 'moving') {
                    this.width = 35;
                    this.height = 50;
                    this.y = groundY - 50;
                    this.dy = 0;
                } else {
                    this.width = 35;
                    this.height = 50;
                    this.y = groundY - 50;
                }
            }
            
            draw() {
                if (this.type === 'wall') {
                    ctx.fillStyle = '#8B4513';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = '#A0522D';
                    for(let i=0;i<3;i++) {
                        ctx.fillRect(this.x+5, this.y+10+i*25, 20, 5);
                    }
                } else if (this.type === 'spike') {
                    ctx.fillStyle = '#ff4444';
                    for(let i=0;i<4;i++) {
                        ctx.beginPath();
                        ctx.moveTo(this.x + i*10, this.y+this.height);
                        ctx.lineTo(this.x + i*10 + 5, this.y);
                        ctx.lineTo(this.x + i*10 + 10, this.y+this.height);
                        ctx.fill();
                    }
                } else if (this.type === 'hole') {
                    ctx.fillStyle = '#1a1a2e';
                    ctx.fillRect(this.x, this.y, this.width, 20);
                    ctx.fillStyle = '#0a0a1a';
                    for(let i=0;i<4;i++) {
                        ctx.fillRect(this.x+5+i*30, this.y-5, 20, 10);
                    }
                } else if (this.type === 'moving') {
                    ctx.fillStyle = '#ff6600';
                    ctx.fillRect(this.x, this.y + this.dy, this.width, this.height);
                    ctx.fillStyle = '#ffaa00';
                    ctx.fillRect(this.x+5, this.y+10 + this.dy, 25, 15);
                } else {
                    ctx.fillStyle = '#666';
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                }
            }
            
            update() {
                if (this.type === 'moving') {
                    this.dy = Math.sin(Date.now() * 0.008) * 20;
                }
                this.x -= currentSpeed;
            }
        }
        
        function addParticle(x, y, color) {
            particles.push({
                x: x, y: y, vx: (Math.random() - 0.5) * 4,
                vy: (Math.random() - 0.5) * 4 - 2,
                life: 30, color: color
            });
        }
        
        function addTrail() {
            trail.push({ x: player.x + player.width/2, y: player.y + player.height/2, life: 15 });
            if (trail.length > 20) trail.shift();
        }
        
        function spawnObstacle() {
            const types = ['wall', 'spike', 'moving', 'wall', 'spike'];
            const type = types[Math.floor(Math.random() * types.length)];
            obstacles.push(new Obstacle(canvasWidth, type));
        }
        
        function resetGame() {
            score = 0;
            level = 1;
            obstacles = [];
            particles = [];
            trail = [];
            frameCounter = 0;
            player.y = groundY - 50;
            player.vy = 0;
            player.onGround = true;
            player.sliding = false;
            player.invincible = 0;
            player.color = '#ff3366';
            currentSpeed = difficultySettings[difficulty].speed;
            obstacleFreq = difficultySettings[difficulty].obstacleFreq;
            gapSize = difficultySettings[difficulty].gapSize;
            scoreMulti = difficultySettings[difficulty].scoreMulti;
            scoreElement.innerText = '0';
            levelBadge.innerHTML = '🔥 LEVEL 1 🔥';
        }
        
        function updateGame() {
            if (!gameRunning) return;
            
            // Управление
            if (rightPressed) {
                addTrail();
            }
            
            // Физика
            player.vy += 0.8;
            player.y += player.vy;
            
            if (player.y >= groundY - (player.sliding ? 30 : player.height)) {
                player.y = groundY - (player.sliding ? 30 : player.height);
                player.vy = 0;
                player.onGround = true;
                
                if (player.sliding) {
                    player.slideTimer--;
                    if (player.slideTimer <= 0) player.sliding = false;
                }
            } else {
                player.onGround = false;
            }
            
            // Прыжок
            if (jumpRequested && player.onGround && !player.sliding) {
                player.vy = -12;
                player.onGround = false;
                jumpRequested = false;
                addParticle(player.x + player.width/2, player.y + player.height, '#ffcc00');
            }
            
            // Слайд
            if (slideRequested && player.onGround && !player.sliding) {
                player.sliding = true;
                player.slideTimer = 20;
                slideRequested = false;
                addParticle(player.x + player.width/2, player.y + player.height, '#66ff66');
            }
            
            // Инвincibility
            if (player.invincible > 0) player.invincible--;
            
            // Спавн препятствий
            frameCounter++;
            if (frameCounter > obstacleFreq - Math.floor(level / 2)) {
                spawnObstacle();
                frameCounter = 0;
            }
            
            // Обновление препятствий и проверка коллизий
            for (let i = 0; i < obstacles.length; i++) {
                obstacles[i].update();
                
                // Коллизия
                if (!player.sliding && 
                    player.x < obstacles[i].x + obstacles[i].width &&
                    player.x + player.width > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].height &&
                    player.y + player.height > obstacles[i].y) {
                    
                    if (player.invincible <= 0) {
                        gameRunning = false;
                        if (score > bestScore) {
                            bestScore = score;
                            localStorage.setItem('parkourBest', bestScore);
                            bestElement.innerText = bestScore;
                        }
                        startScreen.style.display = 'flex';
                        return;
                    }
                }
                
                // Слайд проходит под стенами
                if (player.sliding && obstacles[i].type === 'wall') {
                    // пропускаем
                } else if (!player.sliding && 
                    player.x < obstacles[i].x + obstacles[i].width &&
                    player.x + player.width > obstacles[i].x &&
                    player.y < obstacles[i].y + obstacles[i].height &&
                    player.y + player.height > obstacles[i].y) {
                    if (player.invincible <= 0) {
                        gameRunning = false;
                        if (score > bestScore) {
                            bestScore = score;
                            localStorage.setItem('parkourBest', bestScore);
                            bestElement.innerText = bestScore;
                        }
                        startScreen.style.display = 'flex';
                        return;
                    }
                }
                
                // Подсчёт очков
                if (!obstacles[i].passed && obstacles[i].x + obstacles[i].width < player.x) {
                    obstacles[i].passed = true;
                    score += Math.floor(10 * scoreMulti);
                    scoreElement.innerText = score;
                    
                    // Уровни
                    let newLevel = Math.floor(score / 500) + 1;
                    if (newLevel > level) {
                        level = newLevel;
                        levelBadge.innerHTML = `🔥 LEVEL ${level} 🔥`;
                        currentSpeed += 0.5;
                        obstacleFreq = Math.max(25, obstacleFreq - 2);
                        addParticle(canvasWidth/2, canvasHeight/2, '#ffcc00');
                        addParticle(canvasWidth/2, canvasHeight/2, '#ff6600');
                    }
                }
                
                if (obstacles[i].x + obstacles[i].width < 0) {
                    obstacles.splice(i, 1);
                    i--;
                }
            }
            
            // Партиклы
            for (let i = 0; i < particles.length; i++) {
                particles[i].x += particles[i].vx;
                particles[i].y += particles[i].vy;
                particles[i].life--;
                if (particles[i].life <= 0) {
                    particles.splice(i, 1);
                    i--;
                }
            }
            
            // Трейл
            for (let i = 0; i < trail.length; i++) {
                trail[i].life--;
                if (trail[i].life <= 0) {
                    trail.splice(i, 1);
                    i--;
                }
            }
            
            // Подсветка при инвинсе
            if (player.invincible > 0 && Math.floor(Date.now() / 50) % 2 === 0) {
                player.color = '#ffffff';
            } else {
                player.color = '#ff3366';
            }
        }
        
        function draw() {
            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            
            // Небо с градиентом
            const grad = ctx.createLinearGradient(0, 0, 0, canvasHeight);
            grad.addColorStop(0, '#0a0a2e');
            grad.addColorStop(1, '#1a1a3e');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Звёзды
            ctx.fillStyle = 'white';
            for(let i=0;i<100;i++) {
                if((i*131)%100 > 30) {
                    ctx.fillRect((i*97 + bgOffset) % canvasWidth, (i*53) % 200, 2, 2);
                }
            }
            
            // Луна
            ctx.fillStyle = '#ffeedd';
            ctx.shadowBlur = 30;
            ctx.shadowColor = '#ffcc00';
            ctx.beginPath();
            ctx.arc(750, 80, 40, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = '#ffdd99';
            ctx.beginPath();
            ctx.arc(760, 70, 8, 0, Math.PI*2);
            ctx.fill();
            ctx.shadowBlur = 0;
            
            // Земля
            ctx.fillStyle = '#2a2a3a';
            ctx.fillRect(0, groundY, canvasWidth, canvasHeight - groundY);
            ctx.fillStyle = '#3a3a4a';
            for(let i=0;i<20;i++) {
                ctx.fillRect(i*50 + (bgOffset%50), groundY-5, 30, 10);
            }
            
            // Трава
            ctx.fillStyle = '#44aa44';
            ctx.fillRect(0, groundY-5, canvasWidth, 5);
            
            // Препятствия
            for (let obs of obstacles) {
                obs.draw();
            }
            
            // Трейл
            for (let t of trail) {
                ctx.fillStyle = `rgba(255, 100, 100, ${t.life/15})`;
                ctx.beginPath();
                ctx.arc(t.x, t.y, 8, 0, Math.PI*2);
                ctx.fill();
            }
            
            // Партиклы
            for (let p of particles) {
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, 4, 4);
            }
            
            // ИГРОК (бегун)
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#ff3366';
            
            // Тело
            ctx.fillStyle = player.color;
            if (player.sliding) {
                ctx.fillRect(player.x, player.y + 25, player.width, 25);
                ctx.fillRect(player.x + 5, player.y + 15, 25, 15);
            } else {
                ctx.fillRect(player.x, player.y, player.width, player.height);
                // Голова
                ctx.fillStyle = '#ffcc99';
                ctx.fillRect(player.x + 5, player.y - 15, 25, 20);
                // Глаза
                ctx.fillStyle = 'white';
                ctx.fillRect(player.x + 10, player.y - 10, 6, 6);
                ctx.fillRect(player.x + 20, player.y - 10, 6, 6);
                ctx.fillStyle = 'black';
                ctx.fillRect(player.x + 12, player.y - 9, 3, 3);
                ctx.fillRect(player.x + 22, player.y - 9, 3, 3);
                // Волосы
                ctx.fillStyle = '#ff6600';
                ctx.fillRect(player.x + 8, player.y - 20, 20, 8);
            }
            
            // Ноги при беге
            if (!player.sliding && Math.abs(currentSpeed) > 0 && player.onGround) {
                ctx.fillStyle = '#cc3366';
                if (Date.now() % 200 < 100) {
                    ctx.fillRect(player.x + 5, player.y + player.height, 10, 10);
                    ctx.fillRect(player.x + 20, player.y + player.height - 5, 10, 15);
                } else {
                    ctx.fillRect(player.x + 5, player.y + player.height - 5, 10, 15);
                    ctx.fillRect(player.x + 20, player.y + player.height, 10, 10);
                }
            }
            
            ctx.shadowBlur = 0;
            
            // Эффект скорости
            if (currentSpeed > 8) {
                ctx.fillStyle = 'rgba(255,255,255,0.1)';
                for(let i=0;i<5;i++) {
                    ctx.fillRect(player.x - 5 - i*8, player.y + 20, 4, 15);
                }
            }
            
            // Индикатор слайда
            if (player.sliding) {
                ctx.fillStyle = 'rgba(100,255,100,0.5)';
                ctx.fillRect(player.x, player.y + 25, player.width, 10);
            }
            
            bgOffset += currentSpeed;
        }
        
        function gameLoop() {
            updateGame();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Управление
        document.addEventListener('keydown', (e) => {
            if (!gameRunning) return;
            if (e.key === 'ArrowLeft') { leftPressed = true; e.preventDefault(); }
            if (e.key === 'ArrowRight') { rightPressed = true; e.preventDefault(); }
            if (e.key === 'ArrowUp') { jumpRequested = true; e.preventDefault(); }
            if (e.key === 'ArrowDown') { slideRequested = true; e.preventDefault(); }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft') leftPressed = false;
            if (e.key === 'ArrowRight') rightPressed = false;
        });
        
        // Телефон
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
        
        document.getElementById('slideBtn').addEventListener('touchstart', (e) => { e.preventDefault(); slideRequested = true; });
        document.getElementById('slideBtn').addEventListener('mousedown', () => { slideRequested = true; });
        
        // Старт
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                difficulty = btn.dataset.diff;
            });
        });
        
        startBtn.addEventListener('click', () => {
            const settings = difficultySettings[difficulty];
            currentSpeed = settings.speed;
            obstacleFreq = settings.obstacleFreq;
            gapSize = settings.gapSize;
            scoreMulti = settings.scoreMulti;
            resetGame();
            gameRunning = true;
            startScreen.style.display = 'none';
        });
        
        resetGame();
        gameLoop();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

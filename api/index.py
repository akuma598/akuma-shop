from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Flappy Bird | Akuma Game</title>
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
            cursor: pointer;
        }
        
        .info {
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 40px;
        }
        
        .score-box, .best-box, .lives-box {
            text-align: center;
            background: rgba(0,0,0,0.5);
            padding: 10px 25px;
            border-radius: 30px;
            backdrop-filter: blur(10px);
        }
        
        .score-box span, .best-box span, .lives-box span {
            color: #ffcc00;
            font-size: 32px;
            font-weight: bold;
            display: block;
        }
        
        .score-box p, .best-box p, .lives-box p {
            font-size: 12px;
            color: #aaa;
            margin-top: 5px;
        }
        
        .start-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 14px 40px;
            border-radius: 40px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 18px;
            cursor: pointer;
            margin-top: 20px;
            transition: transform 0.2s, opacity 0.2s;
        }
        
        .start-btn:hover {
            transform: scale(1.05);
            opacity: 0.9;
        }
        
        .status {
            margin-top: 15px;
            font-size: 14px;
            color: #aaa;
        }
        
        .footer {
            margin-top: 30px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
        
        .footer a {
            color: #ffcc00;
            text-decoration: none;
        }
        
        @media (max-width: 500px) {
            canvas {
                width: 100%;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="400" height="600"></canvas>
        
        <div class="info">
            <div class="score-box">
                <span id="score">0</span>
                <p>ОЧКИ</p>
            </div>
            <div class="best-box">
                <span id="best">0</span>
                <p>РЕКОРД</p>
            </div>
            <div class="lives-box">
                <span id="lives">❤️ 5</span>
                <p>ЖИЗНИ</p>
            </div>
        </div>
        
        <button class="start-btn" id="startBtn">🚀 НАЧАТЬ ИГРУ</button>
        <div class="status" id="status">Нажмите на экран или пробел, чтобы лететь</div>
        
        <div class="footer">
            <p>🎮 У тебя 5 жизней! Врезаться в трубы можно 5 раз</p>
            <p>🐦 Тапай по экрану — птичка летит вверх</p>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 400;
        const canvasHeight = 600;
        
        // Птичка
        let bird = {
            x: 80,
            y: canvasHeight / 2,
            radius: 15,
            velocity: 0,
            gravity: 0.25,        // Меньше гравитация
            jump: -5.5,           // Выше прыжок
            rotation: 0
        };
        
        // Трубы
        let pipes = [];
        const pipeWidth = 55;      // Уже трубы
        const pipeGap = 180;       // Больше проход
        const pipeSpeed = 1.8;     // Медленнее
        let frameCount = 0;
        let pipeInterval = 100;     // Трубы реже
        
        // Жизни
        let lives = 5;
        let gameRunning = false;
        let score = 0;
        let bestScore = localStorage.getItem('flappyBest') || 0;
        
        const scoreElement = document.getElementById('score');
        const bestElement = document.getElementById('best');
        const livesElement = document.getElementById('lives');
        const startBtn = document.getElementById('startBtn');
        const statusElement = document.getElementById('status');
        
        bestElement.innerText = bestScore;
        
        function initGame() {
            pipes = [];
            frameCount = 0;
            score = 0;
            lives = 5;
            bird.y = canvasHeight / 2;
            bird.velocity = 0;
            bird.rotation = 0;
            scoreElement.innerText = '0';
            livesElement.innerText = '❤️ ' + lives;
        }
        
        function createPipe() {
            const minHeight = 100;
            const maxHeight = canvasHeight - pipeGap - minHeight;
            const topHeight = Math.floor(Math.random() * (maxHeight - minHeight + 1) + minHeight);
            
            pipes.push({
                x: canvasWidth,
                topHeight: topHeight,
                bottomY: topHeight + pipeGap,
                passed: false
            });
        }
        
        function update() {
            if (!gameRunning) return;
            
            bird.velocity += bird.gravity;
            bird.y += bird.velocity;
            bird.rotation = Math.min(Math.max(bird.velocity * 2.5, -20), 60);
            
            // Верх и низ
            if (bird.y - bird.radius <= 0) {
                bird.y = bird.radius;
                bird.velocity = 0;
            }
            if (bird.y + bird.radius >= canvasHeight) {
                loseLife();
                return;
            }
            
            // Трубы
            if (frameCount >= pipeInterval) {
                createPipe();
                frameCount = 0;
            } else {
                frameCount++;
            }
            
            for (let i = 0; i < pipes.length; i++) {
                pipes[i].x -= pipeSpeed;
                
                if (!pipes[i].passed && pipes[i].x + pipeWidth < bird.x) {
                    pipes[i].passed = true;
                    score++;
                    scoreElement.innerText = score;
                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestElement.innerText = bestScore;
                        localStorage.setItem('flappyBest', bestScore);
                    }
                }
            }
            
            pipes = pipes.filter(pipe => pipe.x + pipeWidth > 0);
            
            // Столкновение с трубами
            for (let pipe of pipes) {
                if (bird.x + bird.radius > pipe.x && bird.x - bird.radius < pipe.x + pipeWidth) {
                    if (bird.y - bird.radius < pipe.topHeight || bird.y + bird.radius > pipe.bottomY) {
                        loseLife();
                        return;
                    }
                }
            }
        }
        
        function loseLife() {
            lives--;
            livesElement.innerText = '❤️ ' + lives;
            
            if (lives <= 0) {
                gameOver();
            } else {
                // Откат птички в начало
                bird.y = canvasHeight / 2;
                bird.velocity = 0;
                // Лёгкая вибрация
                if (navigator.vibrate) navigator.vibrate(100);
                statusElement.innerHTML = `💔 -1 жизнь! Осталось ${lives} ❤️`;
                setTimeout(() => {
                    if (gameRunning) statusElement.innerHTML = '🎮 ЛЕТИ! Нажимай на экран 🎮';
                }, 1000);
            }
        }
        
        function gameOver() {
            gameRunning = false;
            statusElement.innerHTML = `💀 ИГРА ОКОНЧЕНА 💀<br>Счёт: ${score}<br>Нажмите "Начать игру"`;
            statusElement.style.color = '#ff6666';
            startBtn.style.display = 'block';
        }
        
        function startGame() {
            initGame();
            gameRunning = true;
            statusElement.innerHTML = '🎮 ЛЕТИ! Нажимай на экран 🎮';
            statusElement.style.color = '#aaa';
            startBtn.style.display = 'none';
            updateGame();
        }
        
        function jump() {
            if (!gameRunning) {
                startGame();
                return;
            }
            bird.velocity = bird.jump;
            if (navigator.vibrate) navigator.vibrate(30);
        }
        
        function updateGame() {
            update();
            draw();
            if (gameRunning) {
                requestAnimationFrame(updateGame);
            } else {
                draw();
            }
        }
        
        function draw() {
            // Небо
            const grad = ctx.createLinearGradient(0, 0, 0, canvasHeight);
            grad.addColorStop(0, '#87CEEB');
            grad.addColorStop(1, '#E0F6FF');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Облака
            ctx.fillStyle = 'rgba(255,255,255,0.8)';
            ctx.beginPath();
            ctx.ellipse(80, 100, 40, 30, 0, 0, Math.PI * 2);
            ctx.ellipse(110, 90, 35, 28, 0, 0, Math.PI * 2);
            ctx.ellipse(50, 90, 35, 28, 0, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.beginPath();
            ctx.ellipse(300, 200, 45, 35, 0, 0, Math.PI * 2);
            ctx.ellipse(340, 190, 40, 30, 0, 0, Math.PI * 2);
            ctx.ellipse(270, 190, 40, 30, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // Трава
            ctx.fillStyle = '#5c9e3e';
            ctx.fillRect(0, canvasHeight - 80, canvasWidth, 80);
            ctx.fillStyle = '#6ab04c';
            for(let i = 0; i < 20; i++) {
                ctx.beginPath();
                ctx.moveTo(i * 25, canvasHeight - 80);
                ctx.lineTo(i * 25 + 12, canvasHeight - 100);
                ctx.lineTo(i * 25 - 12, canvasHeight - 100);
                ctx.fill();
            }
            
            // Трубы
            for (let pipe of pipes) {
                ctx.fillStyle = '#4a7c3f';
                ctx.fillRect(pipe.x, 0, pipeWidth, pipe.topHeight);
                ctx.fillStyle = '#6ab04c';
                ctx.fillRect(pipe.x - 5, pipe.topHeight - 35, pipeWidth + 10, 35);
                ctx.fillStyle = '#2d5a27';
                ctx.fillRect(pipe.x, pipe.topHeight - 25, pipeWidth, 25);
                
                ctx.fillStyle = '#4a7c3f';
                ctx.fillRect(pipe.x, pipe.bottomY, pipeWidth, canvasHeight - pipe.bottomY);
                ctx.fillStyle = '#6ab04c';
                ctx.fillRect(pipe.x - 5, pipe.bottomY, pipeWidth + 10, 35);
                ctx.fillStyle = '#2d5a27';
                ctx.fillRect(pipe.x, pipe.bottomY, pipeWidth, 25);
            }
            
            // Птичка
            ctx.save();
            ctx.translate(bird.x, bird.y);
            ctx.rotate(bird.rotation * Math.PI / 180);
            
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.ellipse(0, 0, bird.radius, bird.radius - 3, 0, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(7, -5, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(8, -6, 2.5, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#ff6600';
            ctx.beginPath();
            ctx.moveTo(12, -4);
            ctx.lineTo(22, -2);
            ctx.lineTo(12, 1);
            ctx.fill();
            
            ctx.fillStyle = '#ff9900';
            ctx.beginPath();
            ctx.ellipse(-5, 3, 10, 7, -0.5, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
            
            if (gameRunning) {
                ctx.font = 'bold 32px "Courier New"';
                ctx.fillStyle = '#fff';
                ctx.shadowBlur = 5;
                ctx.shadowColor = 'black';
                ctx.fillText(score, canvasWidth / 2 - 20, 70);
                ctx.shadowBlur = 0;
            }
            
            if (!gameRunning && score === 0 && lives === 5) {
                ctx.font = 'bold 20px Arial';
                ctx.fillStyle = '#fff';
                ctx.shadowBlur = 3;
                ctx.fillText('ТАПАЙТЕ ПО ЭКРАНУ', canvasWidth / 2 - 120, canvasHeight / 2 - 50);
                ctx.font = '16px Arial';
                ctx.fillText('ЧТОБЫ НАЧАТЬ ИГРУ', canvasWidth / 2 - 95, canvasHeight / 2);
                ctx.shadowBlur = 0;
            }
        }
        
        canvas.addEventListener('click', jump);
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                jump();
            }
        });
        
        startBtn.addEventListener('click', startGame);
        
        function resizeCanvas() {
            const maxWidth = Math.min(400, window.innerWidth - 40);
            canvas.style.width = maxWidth + 'px';
            canvas.style.height = 'auto';
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        draw();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

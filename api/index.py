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
        
        .score-box, .best-box {
            text-align: center;
            background: rgba(0,0,0,0.5);
            padding: 10px 25px;
            border-radius: 30px;
            backdrop-filter: blur(10px);
        }
        
        .score-box span, .best-box span {
            color: #ffcc00;
            font-size: 32px;
            font-weight: bold;
            display: block;
        }
        
        .score-box p, .best-box p {
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
        </div>
        
        <button class="start-btn" id="startBtn">🚀 НАЧАТЬ ИГРУ</button>
        <div class="status" id="status">Нажмите на экран или пробел, чтобы лететь</div>
        
        <div class="footer">
            <p>🎮 Просто нажимай на экран — птичка летит вверх</p>
            <p>🐦 Не врезайся в трубы!</p>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Размеры
        const canvasWidth = 400;
        const canvasHeight = 600;
        
        // Птичка
        let bird = {
            x: 80,
            y: canvasHeight / 2,
            radius: 15,
            velocity: 0,
            gravity: 0.4,
            jump: -7,
            rotation: 0
        };
        
        // Трубы
        let pipes = [];
        const pipeWidth = 60;
        const pipeGap = 150;
        const pipeSpeed = 2.5;
        let frameCount = 0;
        let pipeInterval = 90;
        
        // Игра
        let gameRunning = false;
        let score = 0;
        let bestScore = localStorage.getItem('flappyBest') || 0;
        
        // Звуки (имитация)
        let audioCtx = null;
        
        // Элементы DOM
        const scoreElement = document.getElementById('score');
        const bestElement = document.getElementById('best');
        const startBtn = document.getElementById('startBtn');
        const statusElement = document.getElementById('status');
        
        bestElement.innerText = bestScore;
        
        // Инициализация труб
        function initPipes() {
            pipes = [];
            frameCount = 0;
            score = 0;
            scoreElement.innerText = '0';
        }
        
        // Создать трубу
        function createPipe() {
            const minHeight = 80;
            const maxHeight = canvasHeight - pipeGap - minHeight;
            const topHeight = Math.floor(Math.random() * (maxHeight - minHeight + 1) + minHeight);
            
            pipes.push({
                x: canvasWidth,
                topHeight: topHeight,
                bottomY: topHeight + pipeGap,
                passed: false
            });
        }
        
        // Обновление физики
        function update() {
            if (!gameRunning) return;
            
            // Птичка
            bird.velocity += bird.gravity;
            bird.y += bird.velocity;
            
            // Вращение птички
            bird.rotation = Math.min(Math.max(bird.velocity * 3, -30), 90);
            
            // Проверка границ
            if (bird.y - bird.radius <= 0 || bird.y + bird.radius >= canvasHeight) {
                gameOver();
                return;
            }
            
            // Трубы
            if (frameCount >= pipeInterval) {
                createPipe();
                frameCount = 0;
            } else {
                frameCount++;
            }
            
            // Движение труб
            for (let i = 0; i < pipes.length; i++) {
                pipes[i].x -= pipeSpeed;
                
                // Проверка прохождения трубы
                if (!pipes[i].passed && pipes[i].x + pipeWidth < bird.x) {
                    pipes[i].passed = true;
                    score++;
                    scoreElement.innerText = score;
                    
                    // Обновление рекорда
                    if (score > bestScore) {
                        bestScore = score;
                        bestElement.innerText = bestScore;
                        localStorage.setItem('flappyBest', bestScore);
                    }
                }
            }
            
            // Удаление труб за экраном
            pipes = pipes.filter(pipe => pipe.x + pipeWidth > 0);
            
            // Проверка столкновения с трубами
            for (let pipe of pipes) {
                if (bird.x + bird.radius > pipe.x && bird.x - bird.radius < pipe.x + pipeWidth) {
                    if (bird.y - bird.radius < pipe.topHeight || bird.y + bird.radius > pipe.bottomY) {
                        gameOver();
                        return;
                    }
                }
            }
        }
        
        // Отрисовка
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
                // Верхняя труба
                ctx.fillStyle = '#4a7c3f';
                ctx.fillRect(pipe.x, 0, pipeWidth, pipe.topHeight);
                ctx.fillStyle = '#6ab04c';
                ctx.fillRect(pipe.x - 5, pipe.topHeight - 40, pipeWidth + 10, 40);
                ctx.fillStyle = '#2d5a27';
                ctx.fillRect(pipe.x, pipe.topHeight - 30, pipeWidth, 30);
                
                // Нижняя труба
                ctx.fillStyle = '#4a7c3f';
                ctx.fillRect(pipe.x, pipe.bottomY, pipeWidth, canvasHeight - pipe.bottomY);
                ctx.fillStyle = '#6ab04c';
                ctx.fillRect(pipe.x - 5, pipe.bottomY, pipeWidth + 10, 40);
                ctx.fillStyle = '#2d5a27';
                ctx.fillRect(pipe.x, pipe.bottomY, pipeWidth, 30);
            }
            
            // Птичка
            ctx.save();
            ctx.translate(bird.x, bird.y);
            ctx.rotate(bird.rotation * Math.PI / 180);
            
            // Тело
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.ellipse(0, 0, bird.radius, bird.radius - 3, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // Глаз
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(7, -5, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(8, -6, 2.5, 0, Math.PI * 2);
            ctx.fill();
            
            // Клюв
            ctx.fillStyle = '#ff6600';
            ctx.beginPath();
            ctx.moveTo(12, -4);
            ctx.lineTo(22, -2);
            ctx.lineTo(12, 1);
            ctx.fill();
            
            // Крыло
            ctx.fillStyle = '#ff9900';
            ctx.beginPath();
            ctx.ellipse(-5, 3, 10, 7, -0.5, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
            
            // Счёт на экране
            if (gameRunning) {
                ctx.font = 'bold 32px "Courier New"';
                ctx.fillStyle = '#fff';
                ctx.shadowBlur = 5;
                ctx.shadowColor = 'black';
                ctx.fillText(score, canvasWidth / 2 - 20, 70);
                ctx.shadowBlur = 0;
            }
            
            // Сообщение о старте
            if (!gameRunning && score === 0) {
                ctx.font = 'bold 20px Arial';
                ctx.fillStyle = '#fff';
                ctx.shadowBlur = 3;
                ctx.fillText('ТАПАЙТЕ ПО ЭКРАНУ', canvasWidth / 2 - 120, canvasHeight / 2 - 50);
                ctx.font = '16px Arial';
                ctx.fillText('ЧТОБЫ НАЧАТЬ ИГРУ', canvasWidth / 2 - 95, canvasHeight / 2);
                ctx.shadowBlur = 0;
            }
        }
        
        // Игра окончена
        function gameOver() {
            gameRunning = false;
            statusElement.innerHTML = '💀 ИГРА ОКОНЧЕНА 💀<br>Нажмите "Начать игру"';
            statusElement.style.color = '#ff6666';
            startBtn.style.display = 'block';
            
            // Анимация падения
            if (bird.y < canvasHeight) {
                const fallInterval = setInterval(() => {
                    bird.velocity += bird.gravity;
                    bird.y += bird.velocity;
                    draw();
                    if (bird.y + bird.radius >= canvasHeight) {
                        clearInterval(fallInterval);
                    }
                }, 20);
            }
        }
        
        // Запуск игры
        function startGame() {
            gameRunning = true;
            bird.y = canvasHeight / 2;
            bird.velocity = 0;
            bird.rotation = 0;
            initPipes();
            statusElement.innerHTML = '🎮 ЛЕТИ! Нажимай на экран 🎮';
            statusElement.style.color = '#aaa';
            startBtn.style.display = 'none';
            updateGame();
        }
        
        // Прыжок
        function jump() {
            if (!gameRunning) {
                startGame();
                return;
            }
            bird.velocity = bird.jump;
            // Звук (вибрация на телефоне)
            if (navigator.vibrate) navigator.vibrate(50);
        }
        
        // Игровой цикл
        function updateGame() {
            update();
            draw();
            if (gameRunning) {
                requestAnimationFrame(updateGame);
            } else {
                draw();
            }
        }
        
        // События
        canvas.addEventListener('click', jump);
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                jump();
            }
        });
        
        startBtn.addEventListener('click', startGame);
        
        // Начальная отрисовка
        draw();
        
        // Адаптация размера canvas
        function resizeCanvas() {
            const container = canvas.parentElement;
            const maxWidth = Math.min(400, window.innerWidth - 40);
            canvas.style.width = maxWidth + 'px';
            canvas.style.height = 'auto';
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

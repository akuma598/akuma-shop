from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Террария | 2D Survival</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            background: #0a0a1a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Courier New', monospace;
            overflow: hidden;
        }
        
        .game-container {
            position: relative;
        }
        
        canvas {
            display: block;
            margin: 0 auto;
            border-radius: 0;
            cursor: pointer;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
        }
        
        .ui {
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            display: flex;
            justify-content: space-between;
            padding: 10px 20px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(5px);
            border-radius: 10px;
            z-index: 10;
            pointer-events: none;
        }
        
        .ui-box {
            text-align: center;
        }
        
        .ui-box span {
            color: #ffcc00;
            font-size: 20px;
            font-weight: bold;
        }
        
        .ui-box p {
            color: #aaa;
            font-size: 10px;
        }
        
        .inventory {
            position: absolute;
            bottom: 10px;
            left: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
            border-radius: 10px;
            padding: 8px;
            display: flex;
            justify-content: center;
            gap: 8px;
            z-index: 10;
        }
        
        .slot {
            background: rgba(255,255,255,0.1);
            border: 1px solid #ffcc00;
            border-radius: 8px;
            padding: 8px 15px;
            color: white;
            font-size: 12px;
            text-align: center;
            cursor: pointer;
            pointer-events: auto;
        }
        
        .slot.active {
            background: #ffcc00;
            color: #1a1a2e;
            border-color: #ffffff;
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
            color: #ffcc00;
            text-shadow: 0 0 20px #ffcc00;
            margin-bottom: 20px;
        }
        
        .start-btn {
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 15px 50px;
            border-radius: 50px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 30px;
        }
        
        .start-btn:active {
            transform: scale(0.95);
        }
        
        @media (max-width: 768px) {
            .game-title { font-size: 28px; }
            .slot { padding: 5px 10px; font-size: 10px; }
            .ui-box span { font-size: 16px; }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="800" height="450"></canvas>
        
        <div class="ui">
            <div class="ui-box">
                <span id="health">❤️ 100</span>
                <p>ЗДОРОВЬЕ</p>
            </div>
            <div class="ui-box">
                <span id="wood">🪵 0</span>
                <p>ДРЕВЕСИНА</p>
            </div>
            <div class="ui-box">
                <span id="stone">🪨 0</span>
                <p>КАМЕНЬ</p>
            </div>
        </div>
        
        <div class="inventory">
            <div class="slot" data-tool="pickaxe">⛏️ КИРКА</div>
            <div class="slot" data-tool="axe">🪓 ТОПОР</div>
            <div class="slot" data-tool="sword">⚔️ МЕЧ</div>
            <div class="slot" data-tool="block">🧱 БЛОК</div>
        </div>
        
        <div class="start-screen" id="startScreen">
            <div class="game-title">🌍 ТЕРРАРИЯ 2D 🌍</div>
            <button class="start-btn" id="startBtn">▶ СТАРТ</button>
            <p style="color:#888; margin-top:20px; font-size:12px;">🔨 ДОБЫВАЙ РЕСУРСЫ | ⚔️ СРАЖАЙСЯ С МОНСТРАМИ | 🧱 СТРОЙ</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 800;
        const canvasHeight = 450;
        const groundY = 350;
        
        // Игрок
        let player = {
            x: 100,
            y: groundY - 35,
            width: 30,
            height: 35,
            vx: 0,
            vy: 0,
            onGround: true,
            facingRight: true,
            health: 100,
            invincible: 0,
            tool: 'pickaxe'
        };
        
        // Мир (блоки)
        let world = [];
        let worldWidth = 200;
        let cameraX = 0;
        
        // Ресурсы
        let wood = 0;
        let stone = 0;
        
        // Враги
        let enemies = [];
        
        // Частицы
        let particles = [];
        
        // Управление
        let leftPressed = false;
        let rightPressed = false;
        let jumpRequested = false;
        let attackRequested = false;
        let mouseX = 0, mouseY = 0;
        
        const healthElement = document.getElementById('health');
        const woodElement = document.getElementById('wood');
        const stoneElement = document.getElementById('stone');
        const startScreen = document.getElementById('startScreen');
        const startBtn = document.getElementById('startBtn');
        
        // Генерация мира
        function generateWorld() {
            world = [];
            let surfaceHeight = groundY - 50;
            
            for(let x = 0; x < worldWidth; x++) {
                let height = surfaceHeight + Math.sin(x * 0.05) * 15;
                height += Math.random() * 5;
                height = Math.floor(height);
                
                for(let y = height; y < canvasHeight; y += 30) {
                    let type = 'dirt';
                    if(y > height + 60) type = 'stone';
                    if(y === height) type = 'grass';
                    if(x > 50 && x < 70 && y > height - 60 && y < height) type = 'wood';
                    
                    world.push({
                        x: x * 30,
                        y: y,
                        width: 30,
                        height: 30,
                        type: type,
                        health: type === 'stone' ? 5 : type === 'wood' ? 3 : 2
                    });
                }
            }
        }
        
        // Класс врага
        class Enemy {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = 28;
                this.height = 28;
                this.health = 30;
                this.speed = 0.8;
                this.type = 'slime';
            }
            
            update() {
                let dx = player.x - this.x;
                if(Math.abs(dx) > 5) {
                    this.x += Math.sign(dx) * this.speed;
                }
                
                // Гравитация
                this.y += 3;
                for(let block of world) {
                    if(this.x < block.x + block.width &&
                        this.x + this.width > block.x &&
                        this.y + this.height > block.y &&
                        this.y < block.y + block.height) {
                        this.y = block.y - this.height;
                        break;
                    }
                }
            }
            
            draw() {
                ctx.fillStyle = '#44aa44';
                ctx.fillRect(this.x - cameraX, this.y, this.width, this.height);
                ctx.fillStyle = '#228822';
                ctx.fillRect(this.x - cameraX + 5, this.y + 5, 18, 8);
                ctx.fillStyle = 'white';
                ctx.fillRect(this.x - cameraX + 6, this.y + 12, 5, 5);
                ctx.fillRect(this.x - cameraX + 16, this.y + 12, 5, 5);
                ctx.fillStyle = 'black';
                ctx.fillRect(this.x - cameraX + 7, this.y + 13, 3, 3);
                ctx.fillRect(this.x - cameraX + 17, this.y + 13, 3, 3);
                
                // Полоска здоровья
                ctx.fillStyle = '#ff4444';
                ctx.fillRect(this.x - cameraX, this.y - 8, this.width, 4);
                ctx.fillStyle = '#44ff44';
                ctx.fillRect(this.x - cameraX, this.y - 8, this.width * (this.health / 30), 4);
            }
        }
        
        function spawnEnemy() {
            let x = player.x + 300 + Math.random() * 200;
            let y = 0;
            for(let block of world) {
                if(block.x < x && block.x + block.width > x) {
                    y = block.y - 30;
                    break;
                }
            }
            enemies.push(new Enemy(x, y));
        }
        
        function attack() {
            let toolDamage = {
                pickaxe: 15,
                axe: 20,
                sword: 25,
                block: 5
            };
            let damage = toolDamage[player.tool] || 10;
            
            // Добыча блоков
            let attackRange = 50;
            for(let i = 0; i < world.length; i++) {
                let block = world[i];
                let dx = (player.x + player.width/2) - (block.x + block.width/2);
                let dy = (player.y + player.height/2) - (block.y + block.height/2);
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < attackRange) {
                    block.health -= damage;
                    addParticle(block.x + block.width/2, block.y + block.height/2, '#ffffff');
                    
                    if(block.health <= 0) {
                        if(block.type === 'wood') wood++;
                        if(block.type === 'stone') stone++;
                        if(block.type === 'dirt' || block.type === 'grass') {}
                        woodElement.innerText = wood;
                        stoneElement.innerText = stone;
                        world.splice(i,1);
                    }
                    break;
                }
            }
            
            // Атака врагов
            for(let i = 0; i < enemies.length; i++) {
                let dx = (player.x + player.width/2) - (enemies[i].x + enemies[i].width/2);
                let dy = (player.y + player.height/2) - (enemies[i].y + enemies[i].height/2);
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < attackRange) {
                    enemies[i].health -= damage;
                    addParticle(enemies[i].x + enemies[i].width/2, enemies[i].y + enemies[i].height/2, '#ff4444');
                    
                    if(enemies[i].health <= 0) {
                        enemies.splice(i,1);
                    }
                    break;
                }
            }
        }
        
        function placeBlock() {
            if(wood < 5) return;
            
            let placeRange = 60;
            let mouseWorldX = mouseX + cameraX;
            
            for(let block of world) {
                let dx = (player.x + player.width/2) - (block.x + block.width/2);
                let dy = (player.y + player.height/2) - (block.y + block.height/2);
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < placeRange) {
                    let newX = Math.floor(mouseWorldX / 30) * 30;
                    let newY = Math.floor(mouseY / 30) * 30;
                    
                    let exists = world.some(b => b.x === newX && b.y === newY);
                    if(!exists && newY < groundY - 30) {
                        world.push({
                            x: newX,
                            y: newY,
                            width: 30,
                            height: 30,
                            type: 'wood',
                            health: 5
                        });
                        wood -= 5;
                        woodElement.innerText = wood;
                    }
                    break;
                }
            }
        }
        
        function addParticle(x, y, color) {
            for(let i=0;i<5;i++) {
                particles.push({
                    x: x, y: y, vx: (Math.random() - 0.5) * 4,
                    vy: (Math.random() - 0.5) * 4 - 2,
                    life: 20, color: color, size: Math.random() * 3 + 2
                });
            }
        }
        
        function updateGame() {
            if(!gameRunning) return;
            
            // Движение
            if(leftPressed) player.vx = -3;
            else if(rightPressed) player.vx = 3;
            else player.vx *= 0.8;
            
            player.x += player.vx;
            
            // Гравитация
            player.vy += 0.8;
            player.y += player.vy;
            player.onGround = false;
            
            for(let block of world) {
                if(player.x < block.x + block.width &&
                    player.x + player.width > block.x &&
                    player.y + player.height > block.y &&
                    player.y < block.y + block.height) {
                    
                    if(player.vy >= 0 && player.y + player.height - block.y < 15) {
                        player.y = block.y - player.height;
                        player.vy = 0;
                        player.onGround = true;
                    } else if(player.vy < 0) {
                        player.y = block.y + block.height;
                        player.vy = 0;
                    }
                }
            }
            
            if(jumpRequested && player.onGround) {
                player.vy = -11;
                player.onGround = false;
                jumpRequested = false;
            }
            
            if(attackRequested) {
                attack();
                attackRequested = false;
            }
            
            // Камера
            cameraX = player.x - 300;
            if(cameraX < 0) cameraX = 0;
            if(cameraX > worldWidth * 30 - canvasWidth) cameraX = worldWidth * 30 - canvasWidth;
            
            // Враги
            for(let i=0;i<enemies.length;i++) {
                enemies[i].update();
                
                let dx = Math.abs(player.x - enemies[i].x);
                let dy = Math.abs(player.y - enemies[i].y);
                if(dx < 35 && dy < 35) {
                    if(player.invincible <= 0) {
                        player.health -= 10;
                        healthElement.innerText = '❤️ ' + player.health;
                        player.invincible = 40;
                        
                        if(player.health <= 0) {
                            gameRunning = false;
                            startScreen.style.display = 'flex';
                        }
                    }
                }
            }
            
            // Спавн врагов
            if(enemies.length < 3 && Math.random() < 0.01) {
                spawnEnemy();
            }
            
            if(player.invincible > 0) player.invincible--;
            
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
        }
        
        function draw() {
            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            
            // Небо
            const grad = ctx.createLinearGradient(0, 0, 0, canvasHeight);
            grad.addColorStop(0, '#1a1a3a');
            grad.addColorStop(1, '#2a2a4a');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Блоки
            for(let block of world) {
                if(block.x + block.width > cameraX && block.x < cameraX + canvasWidth) {
                    if(block.type === 'grass') ctx.fillStyle = '#4a8a3a';
                    else if(block.type === 'dirt') ctx.fillStyle = '#8B5A2B';
                    else if(block.type === 'stone') ctx.fillStyle = '#888888';
                    else if(block.type === 'wood') ctx.fillStyle = '#8B6914';
                    else ctx.fillStyle = '#8B5A2B';
                    
                    ctx.fillRect(block.x - cameraX, block.y, block.width, block.height);
                    ctx.strokeStyle = '#000000';
                    ctx.strokeRect(block.x - cameraX, block.y, block.width, block.height);
                }
            }
            
            // Враги
            for(let enemy of enemies) {
                enemy.draw();
            }
            
            // Частицы
            for(let p of particles) {
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x - cameraX, p.y, p.size, p.size);
            }
            
            // Игрок
            ctx.fillStyle = player.invincible > 0 && Math.floor(Date.now()/50)%2===0 ? '#ffffff' : '#3366ff';
            ctx.fillRect(player.x - cameraX, player.y, player.width, player.height);
            ctx.fillStyle = '#ffcc99';
            ctx.fillRect(player.x - cameraX + 5, player.y - 8, 20, 10);
            ctx.fillStyle = 'white';
            ctx.fillRect(player.x - cameraX + 8, player.y - 5, 5, 5);
            ctx.fillRect(player.x - cameraX + 18, player.y - 5, 5, 5);
            ctx.fillStyle = 'black';
            ctx.fillRect(player.x - cameraX + 9, player.y - 4, 3, 3);
            ctx.fillRect(player.x - cameraX + 19, player.y - 4, 3, 3);
            
            // Инструмент в руке
            let toolIcon = player.tool === 'pickaxe' ? '⛏️' : player.tool === 'axe' ? '🪓' : player.tool === 'sword' ? '⚔️' : '🧱';
            ctx.font = '20px Arial';
            ctx.fillStyle = 'white';
            ctx.fillText(toolIcon, player.x - cameraX + 5, player.y + 25);
            
            // Интерфейс
            ctx.font = 'bold 12px monospace';
            ctx.fillStyle = 'white';
            ctx.fillText(`🔨 ${player.tool.toUpperCase()}`, canvasWidth - 100, 50);
        }
        
        function gameLoop() {
            updateGame();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Управление
        document.addEventListener('keydown', (e) => {
            if(!gameRunning && e.code === 'Space') {
                startBtn.click();
                return;
            }
            if(e.code === 'KeyA') leftPressed = true;
            if(e.code === 'KeyD') rightPressed = true;
            if(e.code === 'Space') { jumpRequested = true; e.preventDefault(); }
        });
        
        document.addEventListener('keyup', (e) => {
            if(e.code === 'KeyA') leftPressed = false;
            if(e.code === 'KeyD') rightPressed = false;
        });
        
        canvas.addEventListener('click', (e) => {
            if(!gameRunning) return;
            const rect = canvas.getBoundingClientRect();
            mouseX = (e.clientX - rect.left) * (canvasWidth / rect.width);
            mouseY = (e.clientY - rect.top) * (canvasHeight / rect.height);
            
            if(player.tool === 'block') placeBlock();
            else attackRequested = true;
        });
        
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = (e.clientX - rect.left) * (canvasWidth / rect.width);
            mouseY = (e.clientY - rect.top) * (canvasHeight / rect.height);
        });
        
        // Выбор инструмента
        document.querySelectorAll('.slot').forEach(slot => {
            slot.addEventListener('click', () => {
                document.querySelectorAll('.slot').forEach(s => s.classList.remove('active'));
                slot.classList.add('active');
                player.tool = slot.dataset.tool;
            });
        });
        
        function startGame() {
            generateWorld();
            enemies = [];
            player.health = 100;
            wood = 5;
            stone = 0;
            player.x = 100;
            healthElement.innerText = '❤️ 100';
            woodElement.innerText = '5';
            stoneElement.innerText = '0';
            gameRunning = true;
            startScreen.style.display = 'none';
            
            for(let i=0;i<2;i++) setTimeout(() => spawnEnemy(), i*2000);
        }
        
        startBtn.addEventListener('click', startGame);
        
        let gameRunning = false;
        generateWorld();
        gameLoop();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

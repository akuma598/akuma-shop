from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Террария | 2D Sandbox</title>
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
            cursor: crosshair;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
        }
        
        .ui {
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            display: flex;
            justify-content: space-between;
            padding: 8px 15px;
            background: rgba(0,0,0,0.7);
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
            font-size: 18px;
            font-weight: bold;
        }
        
        .ui-box p {
            color: #aaa;
            font-size: 9px;
        }
        
        .inventory {
            position: absolute;
            bottom: 10px;
            left: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
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
            padding: 6px 15px;
            color: white;
            font-size: 12px;
            text-align: center;
            cursor: pointer;
            pointer-events: auto;
            transition: 0.1s;
        }
        
        .slot.active {
            background: #ffcc00;
            color: #1a1a2e;
            border-color: #ffffff;
        }
        
        .slot:active {
            transform: scale(0.95);
        }
        
        .start-screen {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.95);
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
        
        .controls-hint {
            position: absolute;
            bottom: 80px;
            left: 0;
            right: 0;
            text-align: center;
            color: #888;
            font-size: 10px;
        }
        
        @media (max-width: 768px) {
            .game-title { font-size: 28px; }
            .slot { padding: 4px 10px; font-size: 10px; }
            .ui-box span { font-size: 14px; }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="900" height="500"></canvas>
        
        <div class="ui">
            <div class="ui-box">
                <span id="health">❤️ 100</span>
                <p>HP</p>
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
            <div class="slot active" data-tool="pickaxe">⛏️ КИРКА</div>
            <div class="slot" data-tool="axe">🪓 ТОПОР</div>
            <div class="slot" data-tool="sword">⚔️ МЕЧ</div>
            <div class="slot" data-tool="block">🧱 БЛОК</div>
        </div>
        
        <div class="controls-hint">🎮 A/D — ДВИЖЕНИЕ | ПРОБЕЛ — ПРЫЖОК | МЫШЬ — ПРИЦЕЛ | ЛКМ — ДЕЙСТВИЕ</div>
        
        <div class="start-screen" id="startScreen">
            <div class="game-title">🌍 ТЕРРАРИЯ 2D 🌍</div>
            <button class="start-btn" id="startBtn">▶ СТАРТ</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const canvasWidth = 900;
        const canvasHeight = 500;
        
        // ИГРОК
        let player = {
            x: 200,
            y: 300,
            width: 28,
            height: 32,
            vx: 0,
            vy: 0,
            onGround: true,
            facingRight: true,
            health: 100,
            invincible: 0,
            tool: 'pickaxe'
        };
        
        // МИР
        let world = [];
        let worldWidth = 250;
        let cameraX = 0;
        
        // РЕСУРСЫ
        let woodCount = 10;
        let stoneCount = 5;
        
        // ВРАГИ
        let enemies = [];
        
        // ЧАСТИЦЫ
        let particles = [];
        
        // ПРИЦЕЛ
        let mouseX = 0, mouseY = 0;
        
        // УПРАВЛЕНИЕ
        let leftPressed = false;
        let rightPressed = false;
        let jumpRequested = false;
        
        const healthElement = document.getElementById('health');
        const woodElement = document.getElementById('wood');
        const stoneElement = document.getElementById('stone');
        const startScreen = document.getElementById('startScreen');
        const startBtn = document.getElementById('startBtn');
        
        woodElement.innerText = woodCount;
        stoneElement.innerText = stoneCount;
        
        // ГЕНЕРАЦИЯ МИРА (как в Террарии)
        function generateWorld() {
            world = [];
            let surfaceHeight = 350;
            
            for(let x = 0; x < worldWidth; x++) {
                let height = surfaceHeight + Math.sin(x * 0.03) * 20;
                height += Math.sin(x * 0.1) * 8;
                height = Math.floor(height);
                
                // Трава на поверхности
                world.push({
                    x: x * 32,
                    y: height,
                    width: 32,
                    height: 32,
                    type: 'grass',
                    health: 2
                });
                
                // Земля под травой
                for(let y = height + 32; y < height + 96; y += 32) {
                    world.push({
                        x: x * 32,
                        y: y,
                        width: 32,
                        height: 32,
                        type: 'dirt',
                        health: 2
                    });
                }
                
                // Камень глубже
                for(let y = height + 128; y < canvasHeight + 100; y += 32) {
                    let type = Math.random() < 0.7 ? 'stone' : 'dirt';
                    world.push({
                        x: x * 32,
                        y: y,
                        width: 32,
                        height: 32,
                        type: type,
                        health: type === 'stone' ? 5 : 2
                    });
                }
                
                // Деревья
                if(Math.random() < 0.08 && height > 300 && height < 380) {
                    let treeX = x * 32;
                    let treeY = height - 32;
                    for(let t = 0; t < 3; t++) {
                        world.push({
                            x: treeX,
                            y: treeY - t * 32,
                            width: 32,
                            height: 32,
                            type: 'wood',
                            health: 3
                        });
                    }
                    // Листва
                    world.push({
                        x: treeX - 32,
                        y: treeY - 96,
                        width: 32,
                        height: 32,
                        type: 'leaf',
                        health: 1
                    });
                    world.push({
                        x: treeX + 32,
                        y: treeY - 96,
                        width: 32,
                        height: 32,
                        type: 'leaf',
                        health: 1
                    });
                    world.push({
                        x: treeX,
                        y: treeY - 128,
                        width: 32,
                        height: 32,
                        type: 'leaf',
                        health: 1
                    });
                }
            }
        }
        
        // ВРАГ (слизень)
        class Enemy {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = 28;
                this.height = 24;
                this.health = 25;
                this.maxHealth = 25;
                this.speed = 1;
                this.jumpTimer = 0;
            }
            
            update() {
                let dx = player.x - this.x;
                if(Math.abs(dx) > 10) {
                    this.x += Math.sign(dx) * this.speed;
                }
                
                this.jumpTimer++;
                if(this.jumpTimer > 40 && this.y > 300) {
                    this.jumpTimer = 0;
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
                // Тело слизня
                ctx.fillStyle = '#6ab04c';
                ctx.beginPath();
                ctx.ellipse(this.x - cameraX + this.width/2, this.y + this.height/2, 14, 12, 0, 0, Math.PI*2);
                ctx.fill();
                ctx.fillStyle = '#4a8a2c';
                ctx.beginPath();
                ctx.ellipse(this.x - cameraX + this.width/2, this.y + this.height/2 + 4, 10, 6, 0, 0, Math.PI*2);
                ctx.fill();
                
                // Глаза
                ctx.fillStyle = 'white';
                ctx.fillRect(this.x - cameraX + 6, this.y + 8, 6, 6);
                ctx.fillRect(this.x - cameraX + 16, this.y + 8, 6, 6);
                ctx.fillStyle = 'black';
                ctx.fillRect(this.x - cameraX + 7, this.y + 9, 3, 3);
                ctx.fillRect(this.x - cameraX + 17, this.y + 9, 3, 3);
                
                // Полоска здоровья
                ctx.fillStyle = '#ff4444';
                ctx.fillRect(this.x - cameraX, this.y - 8, this.width, 4);
                ctx.fillStyle = '#44ff44';
                ctx.fillRect(this.x - cameraX, this.y - 8, this.width * (this.health / this.maxHealth), 4);
            }
        }
        
        function spawnEnemy() {
            let x = player.x + 400 + Math.random() * 200;
            let y = 0;
            for(let block of world) {
                if(block.x < x && block.x + block.width > x) {
                    y = block.y - 28;
                    break;
                }
            }
            enemies.push(new Enemy(x, y));
        }
        
        function attack() {
            let damage = {
                pickaxe: 12,
                axe: 18,
                sword: 25,
                block: 5
            };
            let dmg = damage[player.tool] || 10;
            let range = 55;
            
            let centerX = player.x + player.width/2;
            let centerY = player.y + player.height/2;
            
            // Для мыши
            let mouseWorldX = mouseX + cameraX;
            let mouseWorldY = mouseY;
            
            // Добыча блоков
            for(let i = 0; i < world.length; i++) {
                let b = world[i];
                let dx = centerX - (b.x + b.width/2);
                let dy = centerY - (b.y + b.height/2);
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < range) {
                    b.health -= dmg;
                    addParticle(b.x + b.width/2, b.y + b.height/2, '#ffffff');
                    
                    if(b.health <= 0) {
                        if(b.type === 'wood') woodCount++;
                        if(b.type === 'stone') stoneCount++;
                        woodElement.innerText = woodCount;
                        stoneElement.innerText = stoneCount;
                        world.splice(i,1);
                    }
                    break;
                }
            }
            
            // Атака врагов
            for(let i = 0; i < enemies.length; i++) {
                let e = enemies[i];
                let dx = centerX - (e.x + e.width/2);
                let dy = centerY - (e.y + e.height/2);
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < range) {
                    e.health -= dmg;
                    addParticle(e.x + e.width/2, e.y + e.height/2, '#ff6666');
                    
                    if(e.health <= 0) {
                        enemies.splice(i,1);
                    }
                    break;
                }
            }
        }
        
        function placeBlock() {
            if(woodCount < 5) return;
            
            let range = 60;
            let centerX = player.x + player.width/2;
            let centerY = player.y + player.height/2;
            let mouseWorldX = mouseX + cameraX;
            let mouseWorldY = mouseY;
            
            // Находим ближайший блок для размещения
            let placeX = Math.floor(mouseWorldX / 32) * 32;
            let placeY = Math.floor(mouseWorldY / 32) * 32;
            
            let exists = world.some(b => b.x === placeX && b.y === placeY);
            if(!exists && Math.abs(centerX - placeX) < range && Math.abs(centerY - placeY) < range) {
                world.push({
                    x: placeX,
                    y: placeY,
                    width: 32,
                    height: 32,
                    type: 'wood',
                    health: 3
                });
                woodCount -= 5;
                woodElement.innerText = woodCount;
            }
        }
        
        function addParticle(x, y, color) {
            for(let i=0;i<6;i++) {
                particles.push({
                    x: x, y: y, vx: (Math.random() - 0.5) * 3,
                    vy: (Math.random() - 0.5) * 3 - 2,
                    life: 25, color: color, size: Math.random() * 3 + 2
                });
            }
        }
        
        function updateGame() {
            if(!gameRunning) return;
            
            // Движение
            if(leftPressed) player.vx = -3.5;
            else if(rightPressed) player.vx = 3.5;
            else player.vx *= 0.8;
            
            player.x += player.vx;
            
            // Гравитация
            player.vy += 0.7;
            player.y += player.vy;
            player.onGround = false;
            
            // Коллизия с блоками
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
                player.vy = -10;
                player.onGround = false;
                jumpRequested = false;
            }
            
            // Камера
            cameraX = player.x - 350;
            if(cameraX < 0) cameraX = 0;
            if(cameraX > worldWidth * 32 - canvasWidth) cameraX = worldWidth * 32 - canvasWidth;
            
            // Враги
            for(let i=0;i<enemies.length;i++) {
                enemies[i].update();
                
                let dx = Math.abs(player.x - enemies[i].x);
                let dy = Math.abs(player.y - enemies[i].y);
                if(dx < 35 && dy < 35) {
                    if(player.invincible <= 0) {
                        player.health -= 12;
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
            if(enemies.length < 3 && Math.random() < 0.008) {
                spawnEnemy();
            }
            
            if(player.invincible > 0) player.invincible--;
            
            // Частицы
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
            grad.addColorStop(0, '#0a0a2a');
            grad.addColorStop(1, '#1a1a3a');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Облака
            ctx.fillStyle = 'rgba(255,255,255,0.15)';
            ctx.beginPath();
            ctx.ellipse(200, 60, 50, 30, 0, 0, Math.PI*2);
            ctx.ellipse(250, 50, 40, 25, 0, 0, Math.PI*2);
            ctx.ellipse(160, 50, 40, 25, 0, 0, Math.PI*2);
            ctx.fill();
            
            // БЛОКИ МИРА
            for(let block of world) {
                if(block.x + block.width > cameraX && block.x < cameraX + canvasWidth) {
                    if(block.type === 'grass') {
                        ctx.fillStyle = '#5a9e3a';
                        ctx.fillRect(block.x - cameraX, block.y, block.width, block.height);
                        ctx.fillStyle = '#4a8e2a';
                        ctx.fillRect(block.x - cameraX, block.y + block.height - 8, block.width, 8);
                    } else if(block.type === 'dirt') {
                        ctx.fillStyle = '#8B5A2B';
                        ctx.fillRect(block.x - cameraX, block.y, block.width, block.height);
                        ctx.fillStyle = '#7B4A1B';
                        for(let i=0;i<3;i++) {
                            ctx.fillRect(block.x - cameraX + 5 + i*10, block.y + 10, 6, 4);
                        }
                    } else if(block.type === 'stone') {
                        ctx.fillStyle = '#888888';
                        ctx.fillRect(block.x - cameraX, block.y, block.width, block.height);
                        ctx.fillStyle = '#666666';
                        for(let i=0;i<4;i++) {
                            ctx.fillRect(block.x - cameraX + 4 + i*7, block.y + 8 + (i%2)*16, 4, 4);
                        }
                    } else if(block.type === 'wood') {
                        ctx.fillStyle = '#8B6914';
                        ctx.fillRect(block.x - cameraX, block.y, block.width, block.height);
                        ctx.fillStyle = '#6B4914';
                        ctx.fillRect(block.x - cameraX + 8, block.y, 4, block.height);
                        ctx.fillRect(block.x - cameraX + 20, block.y, 4, block.height);
                    } else if(block.type === 'leaf') {
                        ctx.fillStyle = '#4a8e3a';
                        ctx.fillRect(block.x - cameraX, block.y, block.width, block.height);
                        ctx.fillStyle = '#3a7e2a';
                        for(let i=0;i<4;i++) {
                            ctx.fillRect(block.x - cameraX + 4 + i*6, block.y + 8, 4, 4);
                        }
                    }
                    ctx.strokeStyle = 'rgba(0,0,0,0.2)';
                    ctx.strokeRect(block.x - cameraX, block.y, block.width, block.height);
                }
            }
            
            // ВРАГИ
            for(let enemy of enemies) {
                enemy.draw();
            }
            
            // ЧАСТИЦЫ
            for(let p of particles) {
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x - cameraX, p.y, p.size, p.size);
            }
            
            // ИГРОК (персонаж как в Террарии)
            ctx.save();
            if(player.invincible > 0 && Math.floor(Date.now()/50)%2===0) {
                ctx.fillStyle = '#ffffff';
            } else {
                const grad = ctx.createLinearGradient(player.x - cameraX, player.y, player.x - cameraX + player.width, player.y + player.height);
                grad.addColorStop(0, '#3366ff');
                grad.addColorStop(1, '#2255dd');
                ctx.fillStyle = grad;
            }
            ctx.fillRect(player.x - cameraX, player.y, player.width, player.height);
            
            // Голова
            ctx.fillStyle = '#ffcc99';
            ctx.fillRect(player.x - cameraX + 4, player.y - 10, 20, 12);
            
            // Волосы
            ctx.fillStyle = '#664422';
            ctx.fillRect(player.x - cameraX + 6, player.y - 14, 16, 6);
            
            // Глаза
            if(player.facingRight) {
                ctx.fillStyle = 'white';
                ctx.fillRect(player.x - cameraX + 18, player.y - 6, 5, 5);
                ctx.fillStyle = 'black';
                ctx.fillRect(player.x - cameraX + 19, player.y - 5, 3, 3);
            } else {
                ctx.fillStyle = 'white';
                ctx.fillRect(player.x - cameraX + 6, player.y - 6, 5, 5);
                ctx.fillStyle = 'black';
                ctx.fillRect(player.x - cameraX + 7, player.y - 5, 3, 3);
            }
            
            // Меч/инструмент в руке
            if(player.tool === 'sword') {
                ctx.fillStyle = '#cccccc';
                ctx.fillRect(player.x - cameraX + (player.facingRight ? 25 : -10), player.y + 10, 20, 4);
                ctx.fillStyle = '#aaaaaa';
                ctx.fillRect(player.x - cameraX + (player.facingRight ? 40 : -20), player.y + 8, 8, 8);
            } else if(player.tool === 'pickaxe') {
                ctx.fillStyle = '#8B6914';
                ctx.fillRect(player.x - cameraX + (player.facingRight ? 25 : -10), player.y + 10, 18, 4);
                ctx.fillRect(player.x - cameraX + (player.facingRight ? 38 : -15), player.y + 6, 6, 12);
            } else if(player.tool === 'axe') {
                ctx.fillStyle = '#8B6914';
                ctx.fillRect(player.x - cameraX + (player.facingRight ? 25 : -10), player.y + 10, 16, 4);
                ctx.fillStyle = '#aaaaaa';
                ctx.fillRect(player.x - cameraX + (player.facingRight ? 36 : -13), player.y + 4, 10, 10);
            }
            
            // Ноги
            ctx.fillStyle = '#2255dd';
            ctx.fillRect(player.x - cameraX + 5, player.y + player.height - 6, 8, 8);
            ctx.fillRect(player.x - cameraX + 16, player.y + player.height - 6, 8, 8);
            
            ctx.restore();
            
            // ПРИЦЕЛ
            ctx.beginPath();
            ctx.strokeStyle = '#ffcc00';
            ctx.lineWidth = 2;
            ctx.arc(mouseX, mouseY, 8, 0, Math.PI*2);
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
            
            // Информация об инструменте
            ctx.font = 'bold 12px monospace';
            ctx.fillStyle = '#ffcc00';
            ctx.shadowBlur = 3;
            let toolName = player.tool === 'pickaxe' ? 'КИРКА' : player.tool === 'axe' ? 'ТОПОР' : player.tool === 'sword' ? 'МЕЧ' : 'БЛОК';
            ctx.fillText(`🔨 ${toolName}`, canvasWidth - 100, 40);
            ctx.shadowBlur = 0;
        }
        
        function gameLoop() {
            updateGame();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // УПРАВЛЕНИЕ
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
        
        // МЫШЬ
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = (e.clientX - rect.left) * (canvasWidth / rect.width);
            mouseY = (e.clientY - rect.top) * (canvasHeight / rect.height);
            player.facingRight = mouseX > canvasWidth/2;
        });
        
        canvas.addEventListener('click', (e) => {
            if(!gameRunning) return;
            if(player.tool === 'block') placeBlock();
            else attack();
        });
        
        // ВЫБОР ИНСТРУМЕНТА
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
            particles = [];
            player.health = 100;
            woodCount = 10;
            stoneCount = 5;
            player.x = 200;
            player.y = 300;
            healthElement.innerText = '❤️ 100';
            woodElement.innerText = woodCount;
            stoneElement.innerText = stoneCount;
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

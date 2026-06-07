from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>3D Space Fighter | Akuma Game</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            overflow: hidden;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: #000;
        }
        
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            z-index: 100;
            background: rgba(0,0,0,0.6);
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 14px;
            pointer-events: none;
            font-family: monospace;
        }
        
        #score {
            position: absolute;
            top: 20px;
            right: 20px;
            color: #ffcc00;
            z-index: 100;
            font-size: 32px;
            font-weight: bold;
            background: rgba(0,0,0,0.6);
            padding: 10px 25px;
            border-radius: 10px;
            font-family: monospace;
            pointer-events: none;
        }
        
        #health {
            position: absolute;
            bottom: 30px;
            left: 20px;
            color: white;
            z-index: 100;
            font-size: 18px;
            background: rgba(0,0,0,0.6);
            padding: 8px 20px;
            border-radius: 10px;
            font-family: monospace;
            pointer-events: none;
        }
        
        #controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: #888;
            z-index: 100;
            font-size: 11px;
            background: rgba(0,0,0,0.5);
            padding: 8px 15px;
            border-radius: 10px;
            font-family: monospace;
            pointer-events: none;
        }
        
        .start-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            z-index: 200;
            font-family: monospace;
            transition: transform 0.2s;
            box-shadow: 0 0 20px rgba(255,204,0,0.5);
        }
        
        .start-btn:hover {
            transform: translate(-50%, -50%) scale(1.05);
        }
        
        .status {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -80%);
            color: white;
            font-size: 24px;
            text-align: center;
            z-index: 200;
            background: rgba(0,0,0,0.7);
            padding: 15px 30px;
            border-radius: 20px;
            white-space: nowrap;
            font-family: monospace;
            pointer-events: none;
            display: none;
        }
    </style>
</head>
<body>
    <div id="info">🎮 3D SPACE FIGHTER</div>
    <div id="score">0</div>
    <div id="health">❤️ 100</div>
    <div id="controls">🖱️ МЫШЬ — ДВИЖЕНИЕ | 🔫 ЛКМ — СТРЕЛЬБА</div>
    <button class="start-btn" id="startBtn">🚀 НАЧАТЬ ИГРУ</button>
    <div class="status" id="status"></div>
    
    <script type="importmap">
        {
            "imports": {
                "three": "https://unpkg.com/three@0.128.0/build/three.module.js"
            }
        }
    </script>
    
    <script type="module">
        import * as THREE from 'three';
        
        // Настройки
        let score = 0;
        let health = 100;
        let gameRunning = false;
        let gameOver = false;
        
        const scoreElement = document.getElementById('score');
        const healthElement = document.getElementById('health');
        const startBtn = document.getElementById('startBtn');
        const statusDiv = document.getElementById('status');
        
        // Сцена
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050b1a);
        scene.fog = new THREE.FogExp2(0x050b1a, 0.0005);
        
        // Камера
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3, 12);
        camera.lookAt(0, 0, 0);
        
        // Рендер
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);
        
        // Звёзды
        const starsGeometry = new THREE.BufferGeometry();
        const starsCount = 2000;
        const starsPositions = new Float32Array(starsCount * 3);
        for (let i = 0; i < starsCount; i++) {
            starsPositions[i*3] = (Math.random() - 0.5) * 2000;
            starsPositions[i*3+1] = (Math.random() - 0.5) * 1000;
            starsPositions[i*3+2] = (Math.random() - 0.5) * 500 - 200;
        }
        starsGeometry.setAttribute('position', new THREE.BufferAttribute(starsPositions, 3));
        const starsMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.5 });
        const stars = new THREE.Points(starsGeometry, starsMaterial);
        scene.add(stars);
        
        // Игрок (космический корабль)
        const playerGroup = new THREE.Group();
        
        // Корпус
        const bodyGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
        const bodyMat = new THREE.MeshStandardMaterial({ color: 0x3a86ff, metalness: 0.7, roughness: 0.3 });
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.rotation.x = Math.PI / 2;
        body.position.y = 0;
        playerGroup.add(body);
        
        // Крылья
        const wingGeo = new THREE.BoxGeometry(1.2, 0.1, 0.4);
        const wingMat = new THREE.MeshStandardMaterial({ color: 0x2a6eff });
        const leftWing = new THREE.Mesh(wingGeo, wingMat);
        leftWing.position.set(-0.7, 0.1, 0);
        const rightWing = new THREE.Mesh(wingGeo, wingMat);
        rightWing.position.set(0.7, 0.1, 0);
        playerGroup.add(leftWing);
        playerGroup.add(rightWing);
        
        // Хвост
        const tailGeo = new THREE.ConeGeometry(0.3, 0.6, 4);
        const tail = new THREE.Mesh(tailGeo, bodyMat);
        tail.position.set(0, -0.5, 0);
        tail.rotation.x = Math.PI / 2;
        playerGroup.add(tail);
        
        // Огонь из двигателя
        const fireGeo = new THREE.ConeGeometry(0.2, 0.4, 6);
        const fireMat = new THREE.MeshStandardMaterial({ color: 0xff6600, emissive: 0xff3300 });
        const fire = new THREE.Mesh(fireGeo, fireMat);
        fire.position.set(0, -0.7, 0);
        playerGroup.add(fire);
        
        scene.add(playerGroup);
        
        // Свет
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        scene.add(directionalLight);
        const backLight = new THREE.PointLight(0x4466ff, 0.5);
        backLight.position.set(0, 2, -5);
        scene.add(backLight);
        
        // Пули
        let bullets = [];
        let shootCooldown = 0;
        const bulletSpeed = 15;
        
        // Враги
        let enemies = [];
        let enemySpawnCounter = 0;
        let enemySpawnDelay = 60;
        let kills = 0;
        
        // Мышь
        let mouseX = 0;
        let mouseY = 0;
        let targetX = 0;
        let targetY = 0;
        
        // Класс врага
        class Enemy {
            constructor() {
                const group = new THREE.Group();
                
                const bodyGeo = new THREE.CylinderGeometry(0.4, 0.4, 0.6, 6);
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0xdc143c, metalness: 0.5 });
                const bodyMesh = new THREE.Mesh(bodyGeo, bodyMat);
                group.add(bodyMesh);
                
                const wingGeo = new THREE.BoxGeometry(1, 0.1, 0.3);
                const wingMat = new THREE.MeshStandardMaterial({ color: 0x8b0000 });
                const leftW = new THREE.Mesh(wingGeo, wingMat);
                leftW.position.set(-0.6, 0, 0);
                const rightW = new THREE.Mesh(wingGeo, wingMat);
                rightW.position.set(0.6, 0, 0);
                group.add(leftW);
                group.add(rightW);
                
                const spikeGeo = new THREE.ConeGeometry(0.2, 0.5, 4);
                const spike = new THREE.Mesh(spikeGeo, bodyMat);
                spike.position.set(0, 0.4, 0);
                group.add(spike);
                
                group.position.x = (Math.random() - 0.5) * 12;
                group.position.z = (Math.random() - 0.5) * 5 - 20;
                group.position.y = 0;
                
                scene.add(group);
                this.mesh = group;
                this.speed = 0.08 + Math.random() * 0.07;
            }
            
            update() {
                this.mesh.position.z += this.speed;
            }
            
            destroy() {
                scene.remove(this.mesh);
                // Взрыв
                for (let i = 0; i < 15; i++) {
                    const particle = new THREE.Mesh(
                        new THREE.SphereGeometry(0.05, 3, 3),
                        new THREE.MeshStandardMaterial({ color: 0xff6600, emissive: 0xff3300 })
                    );
                    particle.position.copy(this.mesh.position);
                    scene.add(particle);
                    setTimeout(() => scene.remove(particle), 300);
                }
            }
        }
        
        class Bullet {
            constructor(x, y, z) {
                const geometry = new THREE.SphereGeometry(0.08, 6, 6);
                const material = new THREE.MeshStandardMaterial({ color: 0xffcc00, emissive: 0xff6600 });
                this.mesh = new THREE.Mesh(geometry, material);
                this.mesh.position.set(x, y, z);
                scene.add(this.mesh);
                this.vz = -bulletSpeed;
            }
            
            update() {
                this.mesh.position.z += this.vz;
            }
            
            destroy() {
                scene.remove(this.mesh);
            }
        }
        
        function shoot() {
            if (!gameRunning) return;
            const bullet = new Bullet(
                playerGroup.position.x,
                playerGroup.position.y + 0.2,
                playerGroup.position.z - 0.8
            );
            bullets.push(bullet);
        }
        
        function spawnEnemy() {
            if (enemies.length < 10) {
                enemies.push(new Enemy());
            }
        }
        
        function updateGame() {
            if (!gameRunning) return;
            
            // Движение игрока за мышкой
            targetX = (mouseX / window.innerWidth) * 12 - 6;
            targetY = -(mouseY / window.innerHeight) * 5 + 2.5;
            playerGroup.position.x += (targetX - playerGroup.position.x) * 0.1;
            playerGroup.position.y += (targetY - playerGroup.position.y) * 0.1;
            playerGroup.position.x = Math.min(Math.max(playerGroup.position.x, -5.5), 5.5);
            playerGroup.position.y = Math.min(Math.max(playerGroup.position.y, -2), 3);
            
            // Вращение
            playerGroup.rotation.z = playerGroup.position.x * -0.1;
            playerGroup.rotation.x = playerGroup.position.y * 0.1;
            
            // Огонь
            fire.scale.z = 0.8 + Math.random() * 0.5;
            
            // Перезарядка
            if (shootCooldown > 0) shootCooldown--;
            
            // Пули
            for (let i = 0; i < bullets.length; i++) {
                bullets[i].update();
                if (bullets[i].mesh.position.z < -15) {
                    bullets[i].destroy();
                    bullets.splice(i, 1);
                    i--;
                }
            }
            
            // Враги
            for (let i = 0; i < enemies.length; i++) {
                enemies[i].update();
                
                // Столкновение с игроком
                const dx = enemies[i].mesh.position.x - playerGroup.position.x;
                const dz = enemies[i].mesh.position.z - playerGroup.position.z;
                const dist = Math.sqrt(dx*dx + dz*dz);
                if (dist < 1.0) {
                    health -= 15;
                    healthElement.innerText = '❤️ ' + Math.max(0, health);
                    enemies[i].destroy();
                    enemies.splice(i, 1);
                    i--;
                    
                    if (health <= 0) {
                        gameRunning = false;
                        gameOver = true;
                        statusDiv.style.display = 'block';
                        statusDiv.innerHTML = '💀 ИГРА ОКОНЧЕНА 💀<br>Счёт: ' + score;
                        startBtn.style.display = 'block';
                    }
                    continue;
                }
                
                // Попадание пуль
                for (let j = 0; j < bullets.length; j++) {
                    const bdx = bullets[j].mesh.position.x - enemies[i].mesh.position.x;
                    const bdz = bullets[j].mesh.position.z - enemies[i].mesh.position.z;
                    const bdist = Math.sqrt(bdx*bdx + bdz*bdz);
                    if (bdist < 0.8) {
                        bullets[j].destroy();
                        bullets.splice(j, 1);
                        enemies[i].destroy();
                        enemies.splice(i, 1);
                        kills++;
                        score += 10;
                        scoreElement.innerText = score;
                        i--;
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
                    enemySpawnDelay = Math.max(40, 70 - Math.floor(kills / 15));
                }
            }
            
            // Звёзды двигаются
            stars.rotation.y += 0.001;
            stars.rotation.x += 0.0005;
            
            // Камера
            camera.position.x += (playerGroup.position.x * 0.3 - camera.position.x) * 0.05;
            camera.position.y += (playerGroup.position.y * 0.2 - camera.position.y) * 0.05;
            camera.lookAt(playerGroup.position.x * 0.5, playerGroup.position.y * 0.5, 0);
        }
        
        function animate() {
            requestAnimationFrame(animate);
            updateGame();
            renderer.render(scene, camera);
        }
        
        // Управление мышью
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        document.addEventListener('click', (e) => {
            if (!gameRunning) return;
            if (shootCooldown <= 0) {
                shoot();
                shootCooldown = 12;
            }
        });
        
        function startGame() {
            // Очистка
            bullets.forEach(b => b.destroy());
            enemies.forEach(e => e.destroy());
            bullets = [];
            enemies = [];
            score = 0;
            health = 100;
            kills = 0;
            scoreElement.innerText = '0';
            healthElement.innerText = '❤️ 100';
            playerGroup.position.set(0, 0, 0);
            gameRunning = true;
            gameOver = false;
            startBtn.style.display = 'none';
            statusDiv.style.display = 'none';
            
            // Первые враги
            for(let i = 0; i < 3; i++) {
                setTimeout(() => spawnEnemy(), i * 500);
            }
        }
        
        startBtn.addEventListener('click', startGame);
        
        // Запуск анимации
        animate();
        
        // Адаптация размера
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

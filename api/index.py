from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Space Fighter | 3D Game</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            overflow: hidden;
            touch-action: none;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: #000;
        }
        
        #ui {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            z-index: 100;
            pointer-events: none;
            background: linear-gradient(180deg, rgba(0,0,0,0.6) 0%, transparent 100%);
        }
        
        .ui-box {
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(5px);
            padding: 8px 20px;
            border-radius: 30px;
            border: 1px solid rgba(255,204,0,0.3);
        }
        
        .ui-box span {
            color: #ffcc00;
            font-size: 28px;
            font-weight: bold;
            font-family: monospace;
        }
        
        .ui-box p {
            color: #aaa;
            font-size: 10px;
            margin-top: 2px;
        }
        
        #health-bar-container {
            position: absolute;
            bottom: 30px;
            left: 20px;
            right: 20px;
            height: 8px;
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            z-index: 100;
            overflow: hidden;
        }
        
        #health-bar {
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ff4444, #ffcc00);
            border-radius: 10px;
            transition: width 0.3s;
        }
        
        .controls-hint {
            position: absolute;
            bottom: 50px;
            right: 20px;
            color: #888;
            font-size: 10px;
            background: rgba(0,0,0,0.5);
            padding: 5px 12px;
            border-radius: 20px;
            z-index: 100;
            pointer-events: none;
        }
        
        .start-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 18px 50px;
            border-radius: 60px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 22px;
            cursor: pointer;
            z-index: 200;
            font-family: monospace;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 0 30px rgba(255,204,0,0.5);
        }
        
        .start-btn:active {
            transform: translate(-50%, -50%) scale(0.97);
        }
        
        .status {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -80%);
            color: white;
            font-size: 20px;
            text-align: center;
            z-index: 200;
            background: rgba(0,0,0,0.8);
            padding: 15px 30px;
            border-radius: 20px;
            font-family: monospace;
            pointer-events: none;
            display: none;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,204,0,0.5);
        }
        
        @media (max-width: 768px) {
            .ui-box span { font-size: 22px; }
            .ui-box { padding: 5px 15px; }
            .start-btn { padding: 14px 35px; font-size: 18px; }
        }
    </style>
</head>
<body>
    <div id="ui">
        <div class="ui-box">
            <span id="score">0</span>
            <p>ОЧКИ</p>
        </div>
        <div class="ui-box">
            <span id="kills">0</span>
            <p>УНИЧТОЖЕНО</p>
        </div>
    </div>
    <div id="health-bar-container">
        <div id="health-bar" style="width: 100%"></div>
    </div>
    <div class="controls-hint">🖱️ ВЕДИ ПАЛЬЦЕМ / МЫШКОЙ | 🔫 ТАПАЙ — СТРЕЛЬБА</div>
    <button class="start-btn" id="startBtn">🚀 СТАРТ</button>
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
        let kills = 0;
        let health = 100;
        let gameRunning = false;
        
        const scoreElement = document.getElementById('score');
        const killsElement = document.getElementById('kills');
        const healthBar = document.getElementById('health-bar');
        const startBtn = document.getElementById('startBtn');
        const statusDiv = document.getElementById('status');
        
        // Сцена
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x020210);
        scene.fog = new THREE.FogExp2(0x020210, 0.0008);
        
        // Камера
        const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2, 14);
        camera.lookAt(0, 0, 0);
        
        // Рендер
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);
        
        // Планеты на заднем плане
        const planetGeo = new THREE.SphereGeometry(1.5, 64, 64);
        const planetMat = new THREE.MeshStandardMaterial({ color: 0xaa66ff, emissive: 0x220044, roughness: 0.4, metalness: 0.7 });
        const planet = new THREE.Mesh(planetGeo, planetMat);
        planet.position.set(-8, -2, -25);
        scene.add(planet);
        
        const planet2Geo = new THREE.SphereGeometry(1, 64, 64);
        const planet2Mat = new THREE.MeshStandardMaterial({ color: 0xff6644, emissive: 0x442200, roughness: 0.5 });
        const planet2 = new THREE.Mesh(planet2Geo, planet2Mat);
        planet2.position.set(6, 3, -30);
        scene.add(planet2);
        
        // Звёздное поле (мерцающее)
        const starsGeometry = new THREE.BufferGeometry();
        const starsCount = 3000;
        const starsPositions = new Float32Array(starsCount * 3);
        const starsColors = new Float32Array(starsCount * 3);
        for (let i = 0; i < starsCount; i++) {
            starsPositions[i*3] = (Math.random() - 0.5) * 800;
            starsPositions[i*3+1] = (Math.random() - 0.5) * 600;
            starsPositions[i*3+2] = (Math.random() - 0.5) * 300 - 100;
            const brightness = 0.5 + Math.random() * 0.5;
            starsColors[i*3] = brightness;
            starsColors[i*3+1] = brightness * 0.8;
            starsColors[i*3+2] = brightness;
        }
        starsGeometry.setAttribute('position', new THREE.BufferAttribute(starsPositions, 3));
        starsGeometry.setAttribute('color', new THREE.BufferAttribute(starsColors, 3));
        const starsMaterial = new THREE.PointsMaterial({ size: 0.3, vertexColors: true, transparent: true, opacity: 0.8 });
        const stars = new THREE.Points(starsGeometry, starsMaterial);
        scene.add(stars);
        
        // Туманность (частицы)
        const nebulaCount = 800;
        const nebulaGeometry = new THREE.BufferGeometry();
        const nebulaPositions = new Float32Array(nebulaCount * 3);
        for (let i = 0; i < nebulaCount; i++) {
            nebulaPositions[i*3] = (Math.random() - 0.5) * 60;
            nebulaPositions[i*3+1] = (Math.random() - 0.5) * 30;
            nebulaPositions[i*3+2] = (Math.random() - 0.5) * 40 - 20;
        }
        nebulaGeometry.setAttribute('position', new THREE.BufferAttribute(nebulaPositions, 3));
        const nebulaMat = new THREE.PointsMaterial({ color: 0x8844ff, size: 0.08, transparent: true, opacity: 0.4 });
        const nebula = new THREE.Points(nebulaGeometry, nebulaMat);
        scene.add(nebula);
        
        // Игрок
        const playerGroup = new THREE.Group();
        
        // Корпус
        const bodyGeo = new THREE.ConeGeometry(0.55, 1.4, 16);
        const bodyMat = new THREE.MeshStandardMaterial({ color: 0x3a86ff, metalness: 0.85, roughness: 0.2, emissive: 0x001133 });
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.rotation.x = Math.PI / 2;
        playerGroup.add(body);
        
        // Крылья
        const wingGeo = new THREE.BoxGeometry(1.4, 0.08, 0.5);
        const wingMat = new THREE.MeshStandardMaterial({ color: 0x2a6eff, metalness: 0.8 });
        const leftWing = new THREE.Mesh(wingGeo, wingMat);
        leftWing.position.set(-0.8, 0.05, 0);
        const rightWing = new THREE.Mesh(wingGeo, wingMat);
        rightWing.position.set(0.8, 0.05, 0);
        playerGroup.add(leftWing);
        playerGroup.add(rightWing);
        
        // Крылья верхние
        const topWingGeo = new THREE.BoxGeometry(0.4, 0.5, 0.3);
        const topWing = new THREE.Mesh(topWingGeo, wingMat);
        topWing.position.set(0, 0.35, -0.2);
        playerGroup.add(topWing);
        
        // Двигатели
        const engineGeo = new THREE.CylinderGeometry(0.2, 0.25, 0.5, 8);
        const engineMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.9 });
        const leftEngine = new THREE.Mesh(engineGeo, engineMat);
        leftEngine.position.set(-0.5, -0.2, -0.7);
        const rightEngine = new THREE.Mesh(engineGeo, engineMat);
        rightEngine.position.set(0.5, -0.2, -0.7);
        playerGroup.add(leftEngine);
        playerGroup.add(rightEngine);
        
        // Огонь
        const fireGeo = new THREE.ConeGeometry(0.15, 0.5, 6);
        const fireMat = new THREE.MeshStandardMaterial({ color: 0xff6600, emissive: 0xff3300 });
        const leftFire = new THREE.Mesh(fireGeo, fireMat);
        leftFire.position.set(-0.5, -0.25, -1.0);
        const rightFire = new THREE.Mesh(fireGeo, fireMat);
        rightFire.position.set(0.5, -0.25, -1.0);
        playerGroup.add(leftFire);
        playerGroup.add(rightFire);
        
        // Светящийся эффект вокруг корабля
        const glowGeo = new THREE.SphereGeometry(0.8, 16, 16);
        const glowMat = new THREE.MeshBasicMaterial({ color: 0x3a86ff, transparent: true, opacity: 0.15 });
        const glow = new THREE.Mesh(glowGeo, glowMat);
        playerGroup.add(glow);
        
        scene.add(playerGroup);
        
        // Освещение
        const ambientLight = new THREE.AmbientLight(0x222222);
        scene.add(ambientLight);
        const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
        mainLight.position.set(5, 10, 7);
        mainLight.castShadow = true;
        mainLight.receiveShadow = false;
        scene.add(mainLight);
        const fillLight = new THREE.PointLight(0x4466ff, 0.5);
        fillLight.position.set(0, 2, -3);
        scene.add(fillLight);
        const backLight = new THREE.PointLight(0xff6644, 0.4);
        backLight.position.set(0, 1, 5);
        scene.add(backLight);
        
        // Частицы для эффектов
        let particles = [];
        
        function addExplosion(x, y, z) {
            for (let i = 0; i < 25; i++) {
                const particleGeo = new THREE.SphereGeometry(0.05 + Math.random() * 0.08, 4, 4);
                const particleMat = new THREE.MeshStandardMaterial({ color: 0xff6600, emissive: 0xff3300 });
                const particle = new THREE.Mesh(particleGeo, particleMat);
                particle.position.set(x, y, z);
                scene.add(particle);
                particles.push({
                    mesh: particle,
                    life: 40,
                    vx: (Math.random() - 0.5) * 0.3,
                    vy: (Math.random() - 0.5) * 0.3,
                    vz: (Math.random() - 0.5) * 0.3
                });
            }
        }
        
        // Пули
        let bullets = [];
        let shootCooldown = 0;
        
        // Враги
        let enemies = [];
        let enemySpawnCounter = 0;
        
        // Управление (мышь/тач)
        let touchX = 0;
        let touchY = 0;
        let targetX = 0;
        let targetY = 0;
        
        class Enemy {
            constructor() {
                const group = new THREE.Group();
                
                // Корпус
                const bodyGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.7, 8);
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0xdc143c, metalness: 0.6, roughness: 0.4 });
                const bodyMesh = new THREE.Mesh(bodyGeo, bodyMat);
                group.add(bodyMesh);
                
                // Крылья
                const wingGeo = new THREE.BoxGeometry(1.1, 0.08, 0.35);
                const wingMat = new THREE.MeshStandardMaterial({ color: 0x8b0000 });
                const leftW = new THREE.Mesh(wingGeo, wingMat);
                leftW.position.set(-0.65, 0, 0);
                const rightW = new THREE.Mesh(wingGeo, wingMat);
                rightW.position.set(0.65, 0, 0);
                group.add(leftW);
                group.add(rightW);
                
                // Шипы
                const spikeGeo = new THREE.ConeGeometry(0.15, 0.5, 4);
                const spikeMat = new THREE.MeshStandardMaterial({ color: 0xff4444 });
                const topSpike = new THREE.Mesh(spikeGeo, spikeMat);
                topSpike.position.set(0, 0.4, 0);
                group.add(topSpike);
                
                // Свечение
                const glowEnemyGeo = new THREE.SphereGeometry(0.6, 8, 8);
                const glowEnemyMat = new THREE.MeshBasicMaterial({ color: 0xff4444, transparent: true, opacity: 0.2 });
                const glowEnemy = new THREE.Mesh(glowEnemyGeo, glowEnemyMat);
                group.add(glowEnemy);
                
                group.position.x = (Math.random() - 0.5) * 14;
                group.position.z = (Math.random() - 0.5) * 8 - 25;
                group.position.y = 0;
                
                scene.add(group);
                this.mesh = group;
                this.speed = 0.06 + Math.random() * 0.06;
                this.health = 1;
                this.rotationSpeed = (Math.random() - 0.5) * 0.03;
            }
            
            update() {
                this.mesh.position.z += this.speed;
                this.mesh.rotation.z += this.rotationSpeed;
                this.mesh.rotation.y += 0.02;
            }
            
            destroy() {
                addExplosion(this.mesh.position.x, this.mesh.position.y, this.mesh.position.z);
                scene.remove(this.mesh);
            }
        }
        
        class Bullet {
            constructor(x, y, z) {
                const geometry = new THREE.SphereGeometry(0.1, 8, 8);
                const material = new THREE.MeshStandardMaterial({ color: 0xffcc00, emissive: 0xff6600 });
                this.mesh = new THREE.Mesh(geometry, material);
                this.mesh.position.set(x, y, z);
                scene.add(this.mesh);
                this.speed = -14;
            }
            
            update() {
                this.mesh.position.z += this.speed;
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
                playerGroup.position.z - 1
            );
            bullets.push(bullet);
        }
        
        function spawnEnemy() {
            if (enemies.length < 8) {
                enemies.push(new Enemy());
            }
        }
        
        function updateGame() {
            if (!gameRunning) return;
            
            // Движение за пальцем/мышкой
            let moveX = (touchX / window.innerWidth) * 12 - 6;
            let moveY = -(touchY / window.innerHeight) * 6 + 3;
            moveX = Math.min(Math.max(moveX, -5.5), 5.5);
            moveY = Math.min(Math.max(moveY, -2.5), 3);
            
            playerGroup.position.x += (moveX - playerGroup.position.x) * 0.12;
            playerGroup.position.y += (moveY - playerGroup.position.y) * 0.12;
            
            // Вращение
            playerGroup.rotation.z = playerGroup.position.x * -0.1;
            playerGroup.rotation.x = playerGroup.position.y * 0.08;
            
            // Анимация огня
            const time = Date.now() * 0.01;
            leftFire.scale.z = 0.8 + Math.sin(time) * 0.3;
            rightFire.scale.z = 0.8 + Math.cos(time) * 0.3;
            glow.scale.setScalar(1 + Math.sin(time * 5) * 0.05);
            
            // Перезарядка
            if (shootCooldown > 0) shootCooldown--;
            
            // Пули
            for (let i = 0; i < bullets.length; i++) {
                bullets[i].update();
                if (bullets[i].mesh.position.z < -20) {
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
                    healthBar.style.width = Math.max(0, health) + '%';
                    addExplosion(enemies[i].mesh.position.x, enemies[i].mesh.position.y, enemies[i].mesh.position.z);
                    enemies[i].destroy();
                    enemies.splice(i, 1);
                    i--;
                    
                    if (health <= 0) {
                        gameRunning = false;
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
                        addExplosion(enemies[i].mesh.position.x, enemies[i].mesh.position.y, enemies[i].mesh.position.z);
                        enemies[i].destroy();
                        enemies.splice(i, 1);
                        kills++;
                        score += 10;
                        scoreElement.innerText = score;
                        killsElement.innerText = kills;
                        i--;
                        break;
                    }
                }
            }
            
            // Спавн врагов
            if (enemies.length < 4) {
                enemySpawnCounter++;
                if (enemySpawnCounter > 50) {
                    spawnEnemy();
                    enemySpawnCounter = 0;
                }
            }
            
            // Анимация звёзд и планет
            stars.rotation.y += 0.0005;
            stars.rotation.x += 0.0003;
            nebula.rotation.y += 0.0003;
            planet.rotation.y += 0.002;
            planet2.rotation.x += 0.001;
            
            // Частицы
            for (let i = 0; i < particles.length; i++) {
                particles[i].mesh.position.x += particles[i].vx;
                particles[i].mesh.position.y += particles[i].vy;
                particles[i].mesh.position.z += particles[i].vz;
                particles[i].life--;
                particles[i].mesh.scale.setScalar(particles[i].life / 40);
                if (particles[i].life <= 0) {
                    scene.remove(particles[i].mesh);
                    particles.splice(i, 1);
                    i--;
                }
            }
            
            // Камера
            camera.position.x += (playerGroup.position.x * 0.25 - camera.position.x) * 0.05;
            camera.position.y += (playerGroup.position.y * 0.2 - camera.position.y) * 0.05;
            camera.lookAt(playerGroup.position.x * 0.5, playerGroup.position.y * 0.3, 0);
        }
        
        function animate() {
            requestAnimationFrame(animate);
            updateGame();
            renderer.render(scene, camera);
        }
        
        // Управление (мышь и тач)
        function handleMove(clientX, clientY) {
            touchX = clientX;
            touchY = clientY;
        }
        
        function handleShoot() {
            if (!gameRunning) return;
            if (shootCooldown <= 0) {
                shoot();
                shootCooldown = 10;
            }
        }
        
        document.addEventListener('mousemove', (e) => handleMove(e.clientX, e.clientY));
        document.addEventListener('click', (e) => handleShoot());
        
        // Тач-управление для телефона
        document.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            handleMove(touch.clientX, touch.clientY);
        }, { passive: false });
        
        document.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            handleMove(touch.clientX, touch.clientY);
            handleShoot();
        }, { passive: false });
        
        function startGame() {
            bullets.forEach(b => b.destroy());
            enemies.forEach(e => e.destroy());
            bullets = [];
            enemies = [];
            score = 0;
            kills = 0;
            health = 100;
            scoreElement.innerText = '0';
            killsElement.innerText = '0';
            healthBar.style.width = '100%';
            playerGroup.position.set(0, 0, 0);
            gameRunning = true;
            startBtn.style.display = 'none';
            statusDiv.style.display = 'none';
            
            for(let i = 0; i < 3; i++) {
                setTimeout(() => spawnEnemy(), i * 600);
            }
        }
        
        startBtn.addEventListener('click', startGame);
        
        animate();
        
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

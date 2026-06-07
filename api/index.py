from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Counter-Strike | 3D Shooter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            overflow: hidden;
            touch-action: none;
        }
        
        body {
            font-family: 'Courier New', monospace;
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
            background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, transparent 100%);
        }
        
        .ui-box {
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
            padding: 8px 20px;
            border-radius: 8px;
            border-left: 3px solid #ffcc00;
            font-family: monospace;
        }
        
        .ui-box span {
            color: #ffcc00;
            font-size: 28px;
            font-weight: bold;
        }
        
        .ui-box p {
            color: #aaa;
            font-size: 10px;
            margin-top: 2px;
        }
        
        #health-container {
            position: absolute;
            bottom: 30px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            padding: 8px 15px;
            border-radius: 8px;
            border-left: 3px solid #ff4444;
            z-index: 100;
        }
        
        #health {
            color: #ff4444;
            font-size: 24px;
            font-weight: bold;
            font-family: monospace;
        }
        
        #ammo {
            position: absolute;
            bottom: 30px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            padding: 8px 20px;
            border-radius: 8px;
            border-right: 3px solid #ffcc00;
            z-index: 100;
            font-family: monospace;
            text-align: right;
        }
        
        #ammo span {
            color: #ffcc00;
            font-size: 24px;
            font-weight: bold;
        }
        
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            transform: translate(-50%, -50%);
            z-index: 200;
            pointer-events: none;
        }
        
        #crosshair::before, #crosshair::after {
            content: '';
            position: absolute;
            background: white;
            box-shadow: 0 0 5px rgba(0,0,0,0.5);
        }
        
        #crosshair::before {
            top: 50%;
            left: 0;
            right: 0;
            height: 2px;
            transform: translateY(-50%);
        }
        
        #crosshair::after {
            left: 50%;
            top: 0;
            bottom: 0;
            width: 2px;
            transform: translateX(-50%);
        }
        
        .start-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #ffcc00, #ff9900);
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            z-index: 300;
            font-family: monospace;
            transition: transform 0.2s;
            box-shadow: 0 0 20px rgba(255,204,0,0.5);
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
            z-index: 300;
            background: rgba(0,0,0,0.8);
            padding: 15px 30px;
            border-radius: 8px;
            font-family: monospace;
            pointer-events: none;
            display: none;
            backdrop-filter: blur(10px);
            border: 1px solid #ffcc00;
        }
        
        .controls-hint {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: #888;
            font-size: 10px;
            background: rgba(0,0,0,0.5);
            padding: 5px 12px;
            border-radius: 20px;
            z-index: 100;
            pointer-events: none;
            white-space: nowrap;
        }
        
        @media (max-width: 768px) {
            .ui-box span { font-size: 20px; }
            .ui-box { padding: 5px 15px; }
            #health { font-size: 18px; }
            #ammo span { font-size: 18px; }
        }
    </style>
</head>
<body>
    <div id="ui">
        <div class="ui-box">
            <span id="score">0</span>
            <p>УНИЧТОЖЕНО</p>
        </div>
        <div class="ui-box">
            <span id="kills">0</span>
            <p>УБИЙСТВ</p>
        </div>
    </div>
    <div id="health-container">
        <div id="health">❤️ 100</div>
    </div>
    <div id="ammo">
        <span id="ammo-count">30</span>
        <p>ПАТРОНЫ</p>
    </div>
    <div id="crosshair"></div>
    <div class="controls-hint">🖱️ ПРИЦЕЛ МЫШЬЮ | 🔫 ЛКМ / ТАП — СТРЕЛЬБА | R — ПЕРЕЗАРЯДКА</div>
    <button class="start-btn" id="startBtn">🎯 СТАРТ</button>
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
        
        let score = 0;
        let kills = 0;
        let health = 100;
        let ammo = 30;
        let maxAmmo = 30;
        let gameRunning = false;
        
        const scoreElement = document.getElementById('score');
        const killsElement = document.getElementById('kills');
        const healthElement = document.getElementById('health');
        const ammoElement = document.getElementById('ammo-count');
        const startBtn = document.getElementById('startBtn');
        const statusDiv = document.getElementById('status');
        
        // Сцена
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a1a);
        scene.fog = new THREE.FogExp2(0x0a0a1a, 0.003);
        
        // Камера (от первого лица)
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.01, 1000);
        camera.position.set(0, 1.6, 0);
        
        // Рендер
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // Текстуры пола и стен
        const textureLoader = new THREE.TextureLoader();
        
        // Пол (сетка)
        const gridHelper = new THREE.GridHelper(50, 20, 0x88aaff, 0x335588);
        gridHelper.position.y = -0.5;
        scene.add(gridHelper);
        
        // Прозрачный пол под сеткой
        const groundPlane = new THREE.Mesh(
            new THREE.PlaneGeometry(30, 30),
            new THREE.MeshStandardMaterial({ color: 0x1a1a2e, roughness: 0.8, metalness: 0.1, transparent: true, opacity: 0.5 })
        );
        groundPlane.rotation.x = -Math.PI / 2;
        groundPlane.position.y = -0.5;
        scene.add(groundPlane);
        
        // Стены (простые блоки)
        const wallMaterial = new THREE.MeshStandardMaterial({ color: 0x2a2a3a, roughness: 0.6 });
        
        const walls = [
            { w: 20, h: 3, d: 0.5, x: 0, z: -12, color: 0x3a3a4a },
            { w: 20, h: 3, d: 0.5, x: 0, z: 12, color: 0x3a3a4a },
            { w: 0.5, h: 3, d: 25, x: -12, z: 0, color: 0x3a3a4a },
            { w: 0.5, h: 3, d: 25, x: 12, z: 0, color: 0x3a3a4a }
        ];
        
        walls.forEach(w => {
            const wallGeo = new THREE.BoxGeometry(w.w, w.h, w.d);
            const wallMesh = new THREE.Mesh(wallGeo, new THREE.MeshStandardMaterial({ color: w.color, roughness: 0.5 }));
            wallMesh.position.set(w.x, 1, w.z);
            scene.add(wallMesh);
        });
        
        // Освещение
        const ambientLight = new THREE.AmbientLight(0x333333);
        scene.add(ambientLight);
        const mainLight = new THREE.DirectionalLight(0xffffff, 1);
        mainLight.position.set(5, 10, 7);
        scene.add(mainLight);
        const fillLight = new THREE.PointLight(0x4466ff, 0.3);
        fillLight.position.set(0, 3, 5);
        scene.add(fillLight);
        
        // Враги
        let enemies = [];
        let enemySpawnCounter = 0;
        
        // Пули (raycaster)
        let shootCooldown = 0;
        let reloading = false;
        
        // Частицы
        let particles = [];
        
        // Мышь
        let mouseX = 0;
        let mouseY = 0;
        
        // Эффект отдачи
        let recoil = 0;
        
        class Enemy {
            constructor(x, z) {
                const group = new THREE.Group();
                
                // Тело
                const bodyGeo = new THREE.BoxGeometry(0.7, 1.5, 0.7);
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0x8b0000, metalness: 0.3 });
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = 0.75;
                group.add(body);
                
                // Голова
                const headGeo = new THREE.SphereGeometry(0.45, 16, 16);
                const headMat = new THREE.MeshStandardMaterial({ color: 0xcc8866 });
                const head = new THREE.Mesh(headGeo, headMat);
                head.position.y = 1.45;
                group.add(head);
                
                // Глаза
                const eyeMat = new THREE.MeshStandardMaterial({ color: 0xff0000 });
                const leftEye = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), eyeMat);
                leftEye.position.set(-0.2, 1.55, 0.45);
                const rightEye = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), eyeMat);
                rightEye.position.set(0.2, 1.55, 0.45);
                group.add(leftEye);
                group.add(rightEye);
                
                group.position.set(x, 0, z);
                scene.add(group);
                this.mesh = group;
                this.health = 3;
                this.speed = 0.03;
                this.direction = 1;
            }
            
            update() {
                // Движение к центру
                const dx = -this.mesh.position.x;
                const dz = -this.mesh.position.z;
                const len = Math.sqrt(dx*dx + dz*dz);
                if (len > 0.1) {
                    this.mesh.position.x += (dx / len) * this.speed;
                    this.mesh.position.z += (dz / len) * this.speed;
                }
                // Поворот к игроку
                this.mesh.lookAt(0, 0, 0);
            }
            
            hit() {
                this.health--;
                if (this.health <= 0) {
                    this.destroy();
                    return true;
                }
                return false;
            }
            
            destroy() {
                addExplosion(this.mesh.position.x, this.mesh.position.y + 1, this.mesh.position.z);
                scene.remove(this.mesh);
            }
        }
        
        function addExplosion(x, y, z) {
            for (let i = 0; i < 15; i++) {
                const particleGeo = new THREE.SphereGeometry(0.05 + Math.random() * 0.1, 4, 4);
                const particleMat = new THREE.MeshStandardMaterial({ color: 0xff6600, emissive: 0xff3300 });
                const particle = new THREE.Mesh(particleGeo, particleMat);
                particle.position.set(x, y, z);
                scene.add(particle);
                particles.push({
                    mesh: particle,
                    life: 30,
                    vx: (Math.random() - 0.5) * 0.2,
                    vy: (Math.random() - 0.5) * 0.2 + 0.1,
                    vz: (Math.random() - 0.5) * 0.2
                });
            }
        }
        
        function spawnEnemy() {
            const side = Math.floor(Math.random() * 4);
            let x, z;
            if (side === 0) { x = -8 + Math.random() * 16; z = -15; }
            else if (side === 1) { x = -8 + Math.random() * 16; z = 15; }
            else if (side === 2) { x = -15; z = -8 + Math.random() * 16; }
            else { x = 15; z = -8 + Math.random() * 16; }
            x = Math.min(Math.max(x, -12), 12);
            z = Math.min(Math.max(z, -12), 12);
            enemies.push(new Enemy(x, z));
        }
        
        function shoot() {
            if (!gameRunning) return;
            if (reloading) return;
            if (ammo <= 0) {
                reload();
                return;
            }
            
            ammo--;
            ammoElement.innerText = ammo;
            shootCooldown = 8;
            recoil = 5;
            
            // Raycaster для стрельбы
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            const intersects = raycaster.intersectObjects(enemies.map(e => e.mesh), true);
            
            if (intersects.length > 0) {
                let hit = false;
                for (let obj of intersects) {
                    let enemy = enemies.find(e => e.mesh === obj.object.parent || e.mesh.children.includes(obj.object));
                    if (enemy) {
                        if (enemy.hit()) {
                            const index = enemies.indexOf(enemy);
                            if (index !== -1) enemies.splice(index, 1);
                            kills++;
                            score += 10;
                            scoreElement.innerText = score;
                            killsElement.innerText = kills;
                            addExplosion(enemy.mesh.position.x, enemy.mesh.position.y + 1, enemy.mesh.position.z);
                        }
                        hit = true;
                        break;
                    }
                }
                if (hit) {
                    // Эффект попадания
                    const hitPoint = intersects[0].point;
                    addExplosion(hitPoint.x, hitPoint.y, hitPoint.z);
                }
            }
            
            // Визуальный эффект выстрела
            if (navigator.vibrate) navigator.vibrate(30);
        }
        
        function reload() {
            if (reloading) return;
            if (ammo === maxAmmo) return;
            reloading = true;
            setTimeout(() => {
                ammo = maxAmmo;
                ammoElement.innerText = ammo;
                reloading = false;
            }, 1500);
        }
        
        function updateGame() {
            if (!gameRunning) return;
            
            // Отдача
            if (recoil > 0) {
                recoil--;
            }
            
            // Перезарядка
            if (shootCooldown > 0) shootCooldown--;
            
            // Враги
            for (let i = 0; i < enemies.length; i++) {
                enemies[i].update();
                
                // Столкновение с игроком
                const dist = Math.sqrt(enemies[i].mesh.position.x * enemies[i].mesh.position.x + enemies[i].mesh.position.z * enemies[i].mesh.position.z);
                if (dist < 1.2) {
                    health -= 10;
                    healthElement.innerText = '❤️ ' + Math.max(0, health);
                    enemies[i].destroy();
                    enemies.splice(i, 1);
                    i--;
                    
                    if (health <= 0) {
                        gameRunning = false;
                        statusDiv.style.display = 'block';
                        statusDiv.innerHTML = '💀 ВЫ УБИТЫ 💀<br>Убийств: ' + kills;
                        startBtn.style.display = 'block';
                    }
                }
            }
            
            // Спавн врагов
            if (enemies.length < 5) {
                enemySpawnCounter++;
                if (enemySpawnCounter > 70) {
                    spawnEnemy();
                    enemySpawnCounter = 0;
                }
            }
            
            // Частицы
            for (let i = 0; i < particles.length; i++) {
                particles[i].mesh.position.x += particles[i].vx;
                particles[i].mesh.position.y += particles[i].vy;
                particles[i].mesh.position.z += particles[i].vz;
                particles[i].life--;
                particles[i].mesh.scale.setScalar(particles[i].life / 30);
                if (particles[i].life <= 0) {
                    scene.remove(particles[i].mesh);
                    particles.splice(i, 1);
                    i--;
                }
            }
            
            // Камера от первого лица (вращение от мыши)
            camera.rotation.order = 'YXZ';
            camera.rotation.y = -mouseX * 0.002;
            camera.rotation.x = Math.min(Math.max(-mouseY * 0.0015 + recoil * 0.02, -0.5), 0.5);
        }
        
        function animate() {
            requestAnimationFrame(animate);
            updateGame();
            renderer.render(scene, camera);
        }
        
        // Управление мышью
        document.addEventListener('mousemove', (e) => {
            if (!gameRunning) return;
            mouseX += e.movementX;
            mouseY += e.movementY;
            mouseY = Math.min(Math.max(mouseY, -300), 300);
        });
        
        document.addEventListener('click', (e) => {
            if (!gameRunning) return;
            if (shootCooldown <= 0) {
                shoot();
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') {
                reload();
                e.preventDefault();
            }
        });
        
        // Тач-управление для телефона
        let lastTouchX = 0;
        document.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (!gameRunning) return;
            const touch = e.touches[0];
            lastTouchX = touch.clientX;
            if (shootCooldown <= 0) shoot();
        });
        
        document.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!gameRunning) return;
            const touch = e.touches[0];
            const deltaX = touch.clientX - lastTouchX;
            mouseX += deltaX;
            lastTouchX = touch.clientX;
        }, { passive: false });
        
        function startGame() {
            enemies.forEach(e => e.destroy());
            enemies = [];
            particles.forEach(p => scene.remove(p.mesh));
            particles = [];
            score = 0;
            kills = 0;
            health = 100;
            ammo = 30;
            scoreElement.innerText = '0';
            killsElement.innerText = '0';
            healthElement.innerText = '❤️ 100';
            ammoElement.innerText = '30';
            gameRunning = true;
            startBtn.style.display = 'none';
            statusDiv.style.display = 'none';
            mouseX = 0;
            mouseY = 0;
            camera.rotation.set(0, 0, 0);
            
            for(let i = 0; i < 3; i++) {
                setTimeout(() => spawnEnemy(), i * 800);
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

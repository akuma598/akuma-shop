from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>CS 1.6 STYLE | DE_DUST2</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            overflow: hidden;
            user-select: none;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: #000;
        }
        
        #hud {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            z-index: 100;
            pointer-events: none;
            background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%);
        }
        
        .hud-box {
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(5px);
            padding: 8px 20px;
            border-radius: 4px;
            border-left: 3px solid #ffcc00;
            font-family: monospace;
        }
        
        .hud-box span {
            color: #ffcc00;
            font-size: 24px;
            font-weight: bold;
        }
        
        .hud-box p {
            color: #aaa;
            font-size: 9px;
            margin-top: 2px;
        }
        
        #health-bar {
            position: absolute;
            bottom: 30px;
            left: 20px;
            width: 250px;
            height: 12px;
            background: rgba(0,0,0,0.7);
            border-radius: 6px;
            z-index: 100;
            overflow: hidden;
        }
        
        #health-fill {
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ff4444, #ff8888);
            border-radius: 6px;
            transition: width 0.2s;
        }
        
        #armor-bar {
            position: absolute;
            bottom: 48px;
            left: 20px;
            width: 250px;
            height: 6px;
            background: rgba(0,0,0,0.7);
            border-radius: 3px;
            z-index: 100;
            overflow: hidden;
        }
        
        #armor-fill {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #4488ff, #88aaff);
            border-radius: 3px;
            transition: width 0.2s;
        }
        
        #ammo-panel {
            position: absolute;
            bottom: 30px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            padding: 10px 25px;
            border-radius: 4px;
            border-right: 3px solid #ffcc00;
            text-align: right;
            z-index: 100;
            font-family: monospace;
        }
        
        #ammo-text {
            color: #ffcc00;
            font-size: 28px;
            font-weight: bold;
        }
        
        #weapon-name {
            font-size: 12px;
            color: #aaa;
            margin-top: 5px;
        }
        
        #money {
            position: absolute;
            top: 80px;
            right: 20px;
            background: rgba(0,0,0,0.6);
            padding: 5px 15px;
            border-radius: 4px;
            font-family: monospace;
            text-align: right;
            z-index: 100;
        }
        
        #money span {
            color: #ffcc00;
            font-size: 18px;
            font-weight: bold;
        }
        
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 22px;
            height: 22px;
            transform: translate(-50%, -50%);
            z-index: 200;
            pointer-events: none;
        }
        
        #crosshair::before, #crosshair::after {
            content: '';
            position: absolute;
            background: rgba(255,255,255,0.8);
            box-shadow: 0 0 3px rgba(0,0,0,0.5);
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
            border-radius: 4px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 22px;
            cursor: pointer;
            z-index: 300;
            font-family: monospace;
            transition: 0.2s;
        }
        
        .start-btn:active {
            transform: translate(-50%, -50%) scale(0.97);
        }
        
        .shop-panel {
            position: absolute;
            bottom: 120px;
            left: 20px;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(10px);
            padding: 12px;
            border-radius: 6px;
            z-index: 150;
            border: 1px solid #ffcc00;
            display: none;
            min-width: 160px;
        }
        
        .shop-panel h4 {
            color: #ffcc00;
            margin-bottom: 8px;
            font-size: 12px;
        }
        
        .shop-btn {
            background: #333;
            border: none;
            padding: 6px 12px;
            margin: 4px 0;
            width: 100%;
            color: white;
            cursor: pointer;
            border-radius: 4px;
            font-family: monospace;
            font-size: 11px;
            transition: 0.2s;
        }
        
        .shop-btn:hover {
            background: #ffcc00;
            color: #1a1a2e;
        }
        
        .controls {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            color: #888;
            font-size: 10px;
            background: rgba(0,0,0,0.5);
            padding: 5px 15px;
            border-radius: 20px;
            z-index: 100;
            white-space: nowrap;
        }
        
        .status {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -100%);
            background: rgba(0,0,0,0.8);
            padding: 15px 30px;
            border-radius: 8px;
            color: white;
            font-size: 18px;
            text-align: center;
            z-index: 250;
            display: none;
            font-family: monospace;
            border: 1px solid #ffcc00;
            white-space: nowrap;
        }
        
        @media (max-width: 768px) {
            .hud-box span { font-size: 18px; }
            .hud-box { padding: 5px 12px; }
            #ammo-text { font-size: 22px; }
            #health-bar, #armor-bar { width: 180px; }
            .shop-panel { bottom: 100px; left: 10px; min-width: 140px; }
            .shop-btn { padding: 5px 10px; font-size: 10px; }
        }
    </style>
</head>
<body>
    <div id="hud">
        <div class="hud-box">
            <span id="kills">0</span>
            <p>УБИЙСТВ</p>
        </div>
        <div class="hud-box">
            <span id="wave">1</span>
            <p>РАУНД</p>
        </div>
    </div>
    
    <div id="health-bar">
        <div id="health-fill" style="width: 100%"></div>
    </div>
    <div id="armor-bar">
        <div id="armor-fill" style="width: 0%"></div>
    </div>
    
    <div id="ammo-panel">
        <div id="ammo-text">30/90</div>
        <div id="weapon-name">M4A1</div>
    </div>
    
    <div id="money">
        <span id="money-amount">800</span> $
        <p style="font-size: 9px; color:#aaa;">НАЖМИ B ДЛЯ МАГАЗИНА</p>
    </div>
    
    <div id="crosshair"></div>
    
    <div class="shop-panel" id="shop-panel">
        <h4>🔫 ОРУЖЕЙНЫЙ МАГАЗИН</h4>
        <button class="shop-btn" data-weapon="pistol">🔫 USP (пистолет) - 500$</button>
        <button class="shop-btn" data-weapon="m4">🔫 M4A1 - 3100$</button>
        <button class="shop-btn" data-weapon="ak47">🔫 AK-47 - 2700$</button>
        <button class="shop-btn" data-weapon="awp">🎯 AWP (снайперка) - 4750$</button>
        <button class="shop-btn" data-weapon="armor">🛡️ Бронежилет + шлем - 1000$</button>
        <button class="shop-btn" data-weapon="health">💊 Аптечка (восстановить HP) - 400$</button>
        <button class="shop-btn" onclick="document.getElementById('shop-panel').style.display='none'">❌ ЗАКРЫТЬ</button>
    </div>
    
    <button class="start-btn" id="startBtn">🎮 START GAME</button>
    <div class="status" id="status">СТАРТУЕМ...</div>
    <div class="controls">WASD / СТРЕЛКИ — ДВИЖЕНИЕ | МЫШЬ — ПРИЦЕЛ | ЛКМ — СТРЕЛЬБА | R — ПЕРЕЗАРЯДКА | B — МАГАЗИН</div>

    <script type="importmap">
        {
            "imports": {
                "three": "https://unpkg.com/three@0.128.0/build/three.module.js"
            }
        }
    </script>

    <script type="module">
        import * as THREE from 'three';
        
        // Состояние игры
        let kills = 0;
        let wave = 1;
        let health = 100;
        let armor = 0;
        let money = 800;
        let gameRunning = false;
        
        // Оружие
        let weapons = {
            pistol: { name: "USP", damage: 25, ammo: 12, maxAmmo: 12, reserve: 36, price: 500, color: 0x888888 },
            m4: { name: "M4A1", damage: 33, ammo: 30, maxAmmo: 30, reserve: 90, price: 3100, color: 0x6a8a3a },
            ak47: { name: "AK-47", damage: 36, ammo: 30, maxAmmo: 30, reserve: 90, price: 2700, color: 0x8b5a2b },
            awp: { name: "AWP", damage: 100, ammo: 10, maxAmmo: 10, reserve: 30, price: 4750, color: 0x4a6a8a }
        };
        
        let currentWeapon = "m4";
        let ammo = weapons.m4.ammo;
        let reserveAmmo = weapons.m4.reserve;
        let reloading = false;
        let shootCooldown = 0;
        
        // DOM элементы
        const killsElement = document.getElementById('kills');
        const waveElement = document.getElementById('wave');
        const healthFill = document.getElementById('health-fill');
        const armorFill = document.getElementById('armor-fill');
        const ammoText = document.getElementById('ammo-text');
        const weaponNameElem = document.getElementById('weapon-name');
        const moneyAmount = document.getElementById('money-amount');
        const startBtn = document.getElementById('startBtn');
        const statusDiv = document.getElementById('status');
        const shopPanel = document.getElementById('shop-panel');
        
        // 3D СЦЕНА
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.FogExp2(0x87CEEB, 0.008);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.01, 1000);
        camera.position.set(0, 1.6, 0);
        
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // ОСВЕЩЕНИЕ
        const ambientLight = new THREE.AmbientLight(0x444444);
        scene.add(ambientLight);
        const sunLight = new THREE.DirectionalLight(0xffffff, 1);
        sunLight.position.set(10, 20, 5);
        scene.add(sunLight);
        const fillLight = new THREE.PointLight(0x88aaff, 0.3);
        fillLight.position.set(0, 5, 0);
        scene.add(fillLight);
        
        // КАРТА (DE_DUST2 стиль)
        // Земля (песок)
        const groundMat = new THREE.MeshStandardMaterial({ color: 0xc2a15b, roughness: 0.8 });
        const ground = new THREE.Mesh(new THREE.PlaneGeometry(50, 50), groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.1;
        ground.receiveShadow = true;
        scene.add(ground);
        
        // Стены и здания
        const wallMat = new THREE.MeshStandardMaterial({ color: 0x8b7355, roughness: 0.6 });
        
        const createWall = (x, z, w, h, d) => {
            const wall = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), wallMat);
            wall.position.set(x, h/2, z);
            wall.castShadow = true;
            wall.receiveShadow = true;
            scene.add(wall);
        };
        
        // Центральная площадь
        createWall(0, -8, 15, 3, 1);
        createWall(0, 8, 15, 3, 1);
        createWall(-8, 0, 1, 3, 15);
        createWall(8, 0, 1, 3, 15);
        
        // Длинная стена (A long)
        createWall(-12, -5, 2, 3, 8);
        createWall(-12, 5, 2, 3, 8);
        
        // Коробки
        const boxMat = new THREE.MeshStandardMaterial({ color: 0xaa8866, roughness: 0.5 });
        const boxes = [
            { x: -3, z: -2, w: 2, h: 1.5, d: 2 },
            { x: 3, z: 2, w: 2, h: 1.5, d: 2 },
            { x: -4, z: 4, w: 1.5, h: 1, d: 1.5 },
            { x: 5, z: -3, w: 1.5, h: 1, d: 1.5 },
            { x: -5, z: -4, w: 1.5, h: 1, d: 1.5 },
            { x: 4, z: 4, w: 2, h: 1, d: 2 }
        ];
        boxes.forEach(b => {
            const box = new THREE.Mesh(new THREE.BoxGeometry(b.w, b.h, b.d), boxMat);
            box.position.set(b.x, b.h/2, b.z);
            box.castShadow = true;
            scene.add(box);
        });
        
        // Текстуры для украшения
        const decoMat = new THREE.MeshStandardMaterial({ color: 0xaa8833 });
        for (let i = -12; i <= 12; i+=4) {
            const pillar = new THREE.Mesh(new THREE.BoxGeometry(0.5, 2, 0.5), decoMat);
            pillar.position.set(i, 1, -9);
            scene.add(pillar);
            const pillar2 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 2, 0.5), decoMat);
            pillar2.position.set(i, 1, 9);
            scene.add(pillar2);
        }
        
        // ВРАГИ
        let enemies = [];
        let enemySpawnCounter = 0;
        
        class Enemy {
            constructor(x, z) {
                const group = new THREE.Group();
                
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0x8b3a3a, metalness: 0.2 });
                const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.4, 0.6), bodyMat);
                body.position.y = 0.7;
                group.add(body);
                
                const headMat = new THREE.MeshStandardMaterial({ color: 0xccaa88 });
                const head = new THREE.Mesh(new THREE.SphereGeometry(0.4, 16, 16), headMat);
                head.position.y = 1.45;
                group.add(head);
                
                const eyeMat = new THREE.MeshStandardMaterial({ color: 0xff0000 });
                const leftEye = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), eyeMat);
                leftEye.position.set(-0.15, 1.55, 0.4);
                const rightEye = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), eyeMat);
                rightEye.position.set(0.15, 1.55, 0.4);
                group.add(leftEye);
                group.add(rightEye);
                
                group.position.set(x, 0, z);
                scene.add(group);
                this.mesh = group;
                this.health = 30;
                this.speed = 0.035;
                this.damage = 10;
            }
            
            update() {
                // Движение к игроку
                const dx = -this.mesh.position.x;
                const dz = -this.mesh.position.z;
                const len = Math.sqrt(dx*dx + dz*dz);
                if (len > 0.3) {
                    this.mesh.position.x += (dx / len) * this.speed;
                    this.mesh.position.z += (dz / len) * this.speed;
                }
                this.mesh.lookAt(0, 0, 0);
            }
            
            hit(damage) {
                this.health -= damage;
                if (this.health <= 0) {
                    this.destroy();
                    return true;
                }
                return false;
            }
            
            destroy() {
                scene.remove(this.mesh);
            }
        }
        
        function spawnEnemy() {
            const side = Math.floor(Math.random() * 4);
            let x, z;
            if (side === 0) { x = -8 + Math.random() * 16; z = -14; }
            else if (side === 1) { x = -8 + Math.random() * 16; z = 14; }
            else if (side === 2) { x = -14; z = -8 + Math.random() * 16; }
            else { x = 14; z = -8 + Math.random() * 16; }
            enemies.push(new Enemy(x, z));
        }
        
        // ВЫСТРЕЛ (Raycaster)
        function shoot() {
            if (!gameRunning) return;
            if (reloading) return;
            if (ammo <= 0) {
                reload();
                return;
            }
            
            ammo--;
            updateAmmoDisplay();
            shootCooldown = 10;
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            const intersects = raycaster.intersectObjects(enemies.map(e => e.mesh), true);
            
            if (intersects.length > 0) {
                for (let obj of intersects) {
                    let enemy = enemies.find(e => e.mesh === obj.object.parent);
                    if (enemy) {
                        const damage = weapons[currentWeapon].damage;
                        if (enemy.hit(damage)) {
                            const index = enemies.indexOf(enemy);
                            if (index !== -1) enemies.splice(index, 1);
                            kills++;
                            money += 300;
                            updateMoney();
                            killsElement.innerText = kills;
                            
                            if (kills % 5 === 0) {
                                wave++;
                                waveElement.innerText = wave;
                                statusDiv.style.display = 'block';
                                statusDiv.innerHTML = `🔥 РАУНД ${wave} 🔥`;
                                setTimeout(() => { if (gameRunning) statusDiv.style.display = 'none'; }, 2000);
                            }
                        }
                        break;
                    }
                }
            }
            
            if (navigator.vibrate) navigator.vibrate(30);
        }
        
        function reload() {
            if (reloading) return;
            if (ammo === weapons[currentWeapon].maxAmmo) return;
            if (reserveAmmo <= 0) return;
            
            const needed = weapons[currentWeapon].maxAmmo - ammo;
            const take = Math.min(needed, reserveAmmo);
            ammo += take;
            reserveAmmo -= take;
            reloading = true;
            updateAmmoDisplay();
            
            setTimeout(() => {
                reloading = false;
                updateAmmoDisplay();
            }, 1500);
        }
        
        function buyWeapon(weaponId) {
            const weapon = weapons[weaponId];
            if (!weapon) return false;
            if (money < weapon.price) {
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = `❌ НЕДОСТАТОЧНО ДЕНЕГ! НУЖНО ${weapon.price}$`;
                setTimeout(() => statusDiv.style.display = 'none', 1500);
                return false;
            }
            
            money -= weapon.price;
            currentWeapon = weaponId;
            ammo = weapon.ammo;
            reserveAmmo = weapon.reserve;
            updateMoney();
            updateAmmoDisplay();
            weaponNameElem.innerText = weapon.name;
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = `✅ КУПЛЕНО: ${weapon.name}`;
            setTimeout(() => statusDiv.style.display = 'none', 1000);
            return true;
        }
        
        function buyArmor() {
            if (money < 1000) {
                statusDiv.innerHTML = `❌ НУЖНО 1000$`;
                statusDiv.style.display = 'block';
                setTimeout(() => statusDiv.style.display = 'none', 1000);
                return;
            }
            money -= 1000;
            armor = 100;
            armorFill.style.width = '100%';
            updateMoney();
        }
        
        function buyHealth() {
            if (money < 400) {
                statusDiv.innerHTML = `❌ НУЖНО 400$`;
                statusDiv.style.display = 'block';
                setTimeout(() => statusDiv.style.display = 'none', 1000);
                return;
            }
            if (health >= 100) {
                statusDiv.innerHTML = `❌ HP УЖЕ ПОЛНОЕ`;
                statusDiv.style.display = 'block';
                setTimeout(() => statusDiv.style.display = 'none', 1000);
                return;
            }
            money -= 400;
            health = Math.min(100, health + 50);
            healthFill.style.width = health + '%';
            updateMoney();
        }
        
        function updateMoney() {
            moneyAmount.innerText = money;
        }
        
        function updateAmmoDisplay() {
            ammoText.innerHTML = `${ammo}/${reserveAmmo}`;
        }
        
        function updateGame() {
            if (!gameRunning) return;
            
            if (shootCooldown > 0) shootCooldown--;
            
            // Враги атакуют
            for (let i = 0; i < enemies.length; i++) {
                const dist = Math.sqrt(enemies[i].mesh.position.x**2 + enemies[i].mesh.position.z**2);
                if (dist < 1.2) {
                    let damage = enemies[i].damage;
                    if (armor > 0) {
                        const armorReduce = Math.min(damage * 0.5, armor);
                        damage -= armorReduce;
                        armor -= armorReduce;
                        armorFill.style.width = Math.max(0, armor) + '%';
                    }
                    health -= damage;
                    healthFill.style.width = Math.max(0, health) + '%';
                    enemies[i].destroy();
                    enemies.splice(i, 1);
                    i--;
                    
                    if (health <= 0) {
                        gameRunning = false;
                        statusDiv.style.display = 'block';
                        statusDiv.innerHTML = '💀 ВЫ ПОГИБЛИ! НАЧНИТЕ ЗАНОВО 💀';
                        startBtn.style.display = 'block';
                    }
                }
            }
            
            // Спавн врагов
            if (enemies.length < 4 + Math.floor(wave / 3)) {
                enemySpawnCounter++;
                if (enemySpawnCounter > 40) {
                    spawnEnemy();
                    enemySpawnCounter = 0;
                }
            }
            
            // Движение врагов
            enemies.forEach(e => e.update());
        }
        
        // УПРАВЛЕНИЕ (WASD + мышь)
        let moveForward = false, moveBack = false, moveLeft = false, moveRight = false;
        let mouseX = 0, mouseY = 0;
        let playerX = 0, playerZ = 0;
        let playerSpeed = 4;
        
        document.addEventListener('keydown', (e) => {
            if (!gameRunning) return;
            switch(e.key) {
                case 'w': case 'W': case 'ArrowUp': moveForward = true; break;
                case 's': case 'S': case 'ArrowDown': moveBack = true; break;
                case 'a': case 'A': case 'ArrowLeft': moveLeft = true; break;
                case 'd': case 'D': case 'ArrowRight': moveRight = true; break;
                case 'r': case 'R': reload(); e.preventDefault(); break;
                case 'b': case 'B': shopPanel.style.display = 'block'; break;
                case 'Escape': shopPanel.style.display = 'none'; break;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            switch(e.key) {
                case 'w': case 'W': case 'ArrowUp': moveForward = false; break;
                case 's': case 'S': case 'ArrowDown': moveBack = false; break;
                case 'a': case 'A': case 'ArrowLeft': moveLeft = false; break;
                case 'd': case 'D': case 'ArrowRight': moveRight = false; break;
            }
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!gameRunning) return;
            mouseX += e.movementX;
            mouseY += e.movementY;
            mouseY = Math.min(Math.max(mouseY, -200), 200);
            camera.rotation.order = 'YXZ';
            camera.rotation.y = -mouseX * 0.002;
            camera.rotation.x = -mouseY * 0.0015;
        });
        
        document.addEventListener('click', () => {
            if (!gameRunning) return;
            if (shootCooldown <= 0) shoot();
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
            mouseX += deltaX * 1.5;
            lastTouchX = touch.clientX;
            camera.rotation.y = -mouseX * 0.002;
        }, { passive: false });
        
        function updateMovement() {
            if (!gameRunning) return;
            let dx = 0, dz = 0;
            if (moveForward) dz -= 1;
            if (moveBack) dz += 1;
            if (moveLeft) dx -= 1;
            if (moveRight) dx += 1;
            if (dx !== 0 || dz !== 0) {
                const len = Math.hypot(dx, dz);
                dx /= len;
                dz /= len;
                const angle = camera.rotation.y;
                const newX = playerX + (dx * Math.cos(angle) - dz * Math.sin(angle)) * playerSpeed * 0.016;
                const newZ = playerZ + (dx * Math.sin(angle) + dz * Math.cos(angle)) * playerSpeed * 0.016;
                if (Math.abs(newX) < 13 && Math.abs(newZ) < 13) {
                    playerX = newX;
                    playerZ = newZ;
                }
            }
            camera.position.x = playerX;
            camera.position.z = playerZ;
        }
        
        function startGame() {
            enemies.forEach(e => e.destroy());
            enemies = [];
            kills = 0;
            wave = 1;
            health = 100;
            armor = 0;
            money = 800;
            playerX = 0;
            playerZ = 0;
            camera.position.set(0, 1.6, 0);
            camera.rotation.set(0, 0, 0);
            mouseX = 0;
            mouseY = 0;
            currentWeapon = "m4";
            ammo = weapons.m4.ammo;
            reserveAmmo = weapons.m4.reserve;
            updateMoney();
            updateAmmoDisplay();
            weaponNameElem.innerText = weapons.m4.name;
            healthFill.style.width = '100%';
            armorFill.style.width = '0%';
            killsElement.innerText = '0';
            waveElement.innerText = '1';
            gameRunning = true;
            startBtn.style.display = 'none';
            statusDiv.style.display = 'none';
            shopPanel.style.display = 'none';
            
            for(let i = 0; i < 3; i++) setTimeout(() => spawnEnemy(), i * 800);
        }
        
        startBtn.addEventListener('click', startGame);
        
        document.querySelectorAll('.shop-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const weapon = btn.dataset.weapon;
                if (weapon === 'armor') buyArmor();
                else if (weapon === 'health') buyHealth();
                else if (weapon) buyWeapon(weapon);
                shopPanel.style.display = 'none';
            });
        });
        
        function animate() {
            requestAnimationFrame(animate);
            updateMovement();
            updateGame();
            renderer.render(scene, camera);
        }
        
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

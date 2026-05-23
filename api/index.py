<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Case Opener — Standoff 2 стиль</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            font-family: 'Segoe UI', system-ui, -apple-system, 'Roboto', sans-serif;
            min-height: 100vh;
            padding: 16px;
            color: white;
        }

        /* Контейнер */
        .container {
            max-width: 500px;
            margin: 0 auto;
        }

        /* Верхняя панель с балансом */
        .header {
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .logo {
            font-size: 18px;
            font-weight: bold;
            background: linear-gradient(45deg, #ff6b6b, #ff8e53);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .balance {
            background: #2c2c3e;
            padding: 6px 14px;
            border-radius: 40px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .balance-icon {
            font-size: 18px;
        }

        /* Карточка кейса */
        .case-card {
            background: linear-gradient(145deg, #1e1e2e, #151520);
            border-radius: 32px;
            padding: 24px;
            text-align: center;
            margin-bottom: 24px;
            border: 1px solid rgba(255,215,0,0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .case-image {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            border-radius: 24px;
            margin: 0 auto 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            box-shadow: 0 0 20px rgba(255,215,0,0.3);
        }

        .case-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .case-price {
            color: #ffd700;
            font-size: 14px;
            margin-bottom: 16px;
        }

        /* Кнопка открытия */
        .open-btn {
            background: linear-gradient(90deg, #ff6b6b, #ff8e53);
            border: none;
            padding: 16px 32px;
            border-radius: 60px;
            font-size: 20px;
            font-weight: bold;
            color: white;
            width: 100%;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 5px 15px rgba(255,107,107,0.3);
        }

        .open-btn:active {
            transform: scale(0.96);
        }

        .open-btn:disabled {
            opacity: 0.6;
            transform: none;
        }

        /* Анимация открытия */
        .case-opening {
            background: rgba(0,0,0,0.9);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(8px);
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .case-animation {
            text-align: center;
            animation: spin 0.5s ease-out;
        }

        @keyframes spin {
            0% { transform: scale(0) rotate(0deg); opacity: 0; }
            50% { transform: scale(1.2) rotate(180deg); }
            100% { transform: scale(1) rotate(360deg); opacity: 1; }
        }

        /* Результат */
        .result-card {
            background: rgba(0,0,0,0.8);
            border-radius: 28px;
            padding: 24px;
            text-align: center;
            margin-top: 20px;
            border: 1px solid rgba(255,215,0,0.5);
        }

        .result-name {
            font-size: 18px;
            font-weight: bold;
            margin: 12px 0;
        }

        .rarity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 40px;
            font-size: 12px;
            background: rgba(255,255,255,0.1);
        }

        /* История */
        .history {
            margin-top: 24px;
            background: rgba(0,0,0,0.4);
            border-radius: 20px;
            padding: 16px;
        }

        .history-title {
            font-size: 14px;
            margin-bottom: 12px;
            color: #aaa;
        }

        .history-item {
            background: rgba(255,255,255,0.05);
            padding: 8px 12px;
            border-radius: 12px;
            margin-bottom: 8px;
            font-size: 13px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">🔥 CASE MASTER</div>
        <div class="balance">
            <span class="balance-icon">💎</span>
            <span id="points">100</span>
        </div>
    </div>

    <div class="case-card">
        <div class="case-image">📦</div>
        <div class="case-title">STRIKE CASE</div>
        <div class="case-price">Стоимость: 10 💎</div>
        <button class="open-btn" id="openBtn">🔓 ОТКРЫТЬ</button>
    </div>

    <div id="resultArea"></div>

    <div class="history">
        <div class="history-title">📜 ПОСЛЕДНИЕ ВЫПАДЕНИЯ</div>
        <div id="historyList">
            <div class="history-item">✨ Начни открывать кейсы!</div>
        </div>
    </div>
</div>

<script>
    // База скинов (как в Standoff 2 стиле)
    const items = [
        { name: "★ М9 Bayonet | Doppler", rarity: "Легендарный", chance: 1, icon: "🔪", color: "#ff6b6b" },
        { name: "AK-47 | Fire Serpent", rarity: "Тайный", chance: 4, icon: "🔥", color: "#ff8e53" },
        { name: "AWP | Dragon Lore", rarity: "Тайный", chance: 5, icon: "🐉", color: "#ff8e53" },
        { name: "M4A4 | Howl", rarity: "Запретный", chance: 3, icon: "🐺", color: "#c44569" },
        { name: "USP-S | Kill Confirmed", rarity: "Засекреченный", chance: 15, icon: "💀", color: "#a55eea" },
        { name: "P250 | Asiimov", rarity: "Промышленный", chance: 20, icon: "🤖", color: "#4a69bd" },
        { name: "MP9 | Rose Iron", rarity: "Армейский", chance: 52, icon: "🌹", color: "#78e08f" }
    ];

    // Функция получения случайного предмета с учетом шансов
    function getRandomItem() {
        const rand = Math.random() * 100;
        let sum = 0;
        for (const item of items) {
            sum += item.chance;
            if (rand <= sum) return item;
        }
        return items[items.length - 1];
    }

    // Состояние
    let points = 100;
    let history = [];

    // DOM элементы
    const pointsSpan = document.getElementById('points');
    const openBtn = document.getElementById('openBtn');
    const resultArea = document.getElementById('resultArea');
    const historyList = document.getElementById('historyList');

    // Обновление UI
    function updateUI() {
        pointsSpan.textContent = points;
    }

    // Добавление в историю
    function addToHistory(itemName, rarity) {
        history.unshift({ name: itemName, rarity: rarity, time: new Date().toLocaleTimeString() });
        if (history.length > 10) history.pop();
        
        historyList.innerHTML = history.map(h => `
            <div class="history-item">
                ${h.name} — ${h.rarity} (${h.time})
            </div>
        `).join('');
    }

    // Открытие кейса
    async function openCase() {
        if (points < 10) {
            alert("❌ Не хватает монет! Заработай их просмотром рекламы или заданиями.");
            return;
        }

        // Списываем монеты
        points -= 10;
        updateUI();

        // Показываем анимацию
        openBtn.disabled = true;
        openBtn.textContent = "🎲 ОТКРЫВАЮ...";

        // Создаем модалку с анимацией
        const modal = document.createElement('div');
        modal.className = 'case-opening';
        modal.innerHTML = `
            <div class="case-animation">
                <div style="font-size: 80px;">📦</div>
                <div style="margin-top: 20px; font-size: 18px;">Прокрутка...</div>
            </div>
        `;
        document.body.appendChild(modal);

        // Имитация задержки (как настоящий сервер)
        await new Promise(resolve => setTimeout(resolve, 1200));

        // Получаем предмет
        const wonItem = getRandomItem();
        
        // Добавляем небольшой бонус (1 монета за открытие)
        points += 1;
        updateUI();

        // Закрываем анимацию
        modal.remove();

        // Показываем результат
        resultArea.innerHTML = `
            <div class="result-card" style="border-color: ${wonItem.color}">
                <div style="font-size: 48px;">${wonItem.icon}</div>
                <div class="result-name" style="color: ${wonItem.color}">${wonItem.name}</div>
                <div class="rarity-badge" style="background: ${wonItem.color}20; border-color: ${wonItem.color}">
                    ${wonItem.rarity}
                </div>
                <div style="margin-top: 12px; font-size: 12px; color: #aaa;">
                    +1 💎 за открытие
                </div>
            </div>
        `;

        // Добавляем в историю
        addToHistory(wonItem.name, wonItem.rarity);

        // Возвращаем кнопку
        openBtn.disabled = false;
        openBtn.textContent = "🔓 ОТКРЫТЬ";

        // Автоматически скрываем результат через 5 секунд
        setTimeout(() => {
            if (resultArea.innerHTML.includes(wonItem.name)) {
                resultArea.innerHTML = '';
            }
        }, 5000);
    }

    // Вешаем обработчик
    openBtn.addEventListener('click', openCase);
</script>
</body>
</html>

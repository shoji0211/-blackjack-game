let gameState = null;

async function placeBet(amount) {
    if (amount > parseInt(document.getElementById('balance').textContent.replace('$', ''))) {
        alert('残高が足りません');
        return;
    }
    await startGame(amount);
}

async function placeBetCustom() {
    const customBet = document.getElementById('custom-bet').value;
    if (!customBet || customBet < 1) {
        alert('有効な金額を入力してください');
        return;
    }
    await placeBet(parseInt(customBet));
}

async function startGame(bet) {
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ bet: bet })
        });

        if (!response.ok) {
            alert('ベット額が無効です');
            return;
        }

        gameState = await response.json();
        updateUI();
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
}

async function hit() {
    try {
        const response = await fetch('/api/hit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        gameState = await response.json();
        updateUI();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function stand() {
    try {
        const response = await fetch('/api/stand', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        gameState = await response.json();
        updateUI();
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateUI() {
    // 残高と現在のベットを更新
    document.getElementById('balance').textContent = '$' + gameState.balance;
    document.getElementById('current-bet').textContent = '$' + gameState.current_bet;

    // セクションの表示/非表示を切り替え
    const bettingSection = document.getElementById('betting-section');
    const gameSection = document.getElementById('game-section');
    const gameOverSection = document.getElementById('game-over');

    if (gameState.game_state === 'betting' || gameState.balance === 0) {
        bettingSection.style.display = 'block';
        gameSection.style.display = 'none';
        if (gameState.balance === 0) {
            gameOverSection.style.display = 'block';
            bettingSection.style.display = 'none';
        } else {
            gameOverSection.style.display = 'none';
        }
    } else {
        bettingSection.style.display = 'none';
        gameSection.style.display = 'block';
        gameOverSection.style.display = 'none';
    }

    // カード表示を更新
    displayCards('dealer-cards', gameState.dealer_cards);
    displayCards('player-cards', gameState.player_cards);

    // 値を表示
    document.getElementById('player-value').textContent = '値: ' + gameState.player_value;
    if (gameState.dealer_value !== null) {
        document.getElementById('dealer-value').textContent = '値: ' + gameState.dealer_value;
    } else {
        document.getElementById('dealer-value').textContent = '値: ?';
    }

    // メッセージを表示
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = gameState.message;

    // ゲーム状態に応じてボタンを制御
    const actionButtons = document.getElementById('action-buttons');
    const nextButtons = document.getElementById('next-buttons');

    if (gameState.game_state === 'playing') {
        actionButtons.style.display = 'flex';
        nextButtons.style.display = 'none';
        document.getElementById('hit-btn').disabled = false;
        document.getElementById('stand-btn').disabled = false;
        messageDiv.textContent = '';
        messageDiv.className = '';
    } else if (gameState.game_state === 'finished') {
        actionButtons.style.display = 'none';
        nextButtons.style.display = 'flex';

        // メッセージの色を変更
        messageDiv.className = '';
        if (gameState.message.includes('勝ち')) {
            messageDiv.classList.add('win');
        } else if (gameState.message.includes('バスト')) {
            messageDiv.classList.add('lose');
        } else if (gameState.message.includes('引き分け')) {
            messageDiv.classList.add('draw');
        } else {
            messageDiv.classList.add('lose');
        }

        // ディーラーの全カードを表示
        displayCards('dealer-cards', gameState.dealer_cards, false);
    }
}

function displayCards(elementId, cards, hideFirst = true) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';

    cards.forEach((card, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';

        if (card.rank === '?' && hideFirst && index === 0) {
            cardDiv.classList.add('hidden');
            cardDiv.textContent = '?';
        } else {
            cardDiv.textContent = card.rank + card.suit;
        }

        container.appendChild(cardDiv);
    });
}

function nextRound() {
    const balance = parseInt(document.getElementById('balance').textContent.replace('$', ''));
    if (balance > 0) {
        document.getElementById('betting-section').style.display = 'block';
        document.getElementById('game-section').style.display = 'none';
        document.getElementById('custom-bet').value = '';
    }
}

function resetGame() {
    location.reload();
}

// ページ読み込み時
document.addEventListener('DOMContentLoaded', function() {
    console.log('ゲーム準備完了');
});

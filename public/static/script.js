(() => {
  const suits = ['♠', '♥', '♦', '♣'];
  const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

  let deck = [];
  let player = [];
  let dealer = [];
  let balance = 1000;
  let currentBet = 0;

  // Selectors
  const $ = (id) => document.getElementById(id);
  const betScreen = $('betScreen');
  const gameScreen = $('gameScreen');
  const balanceDisplay = $('balance-display');
  const betDisplay = $('bet-display');
  const customBetInput = $('customBet');
  const betBtn = $('betBtn');
  const presetBtns = document.querySelectorAll('.preset-btn');
  const gameBalance = $('game-balance');
  const gameBet = $('game-bet');
  const hitBtn = $('hitBtn');
  const standBtn = $('standBtn');
  const nextBtn = $('nextBtn');

  // Card game functions
  function buildDeck() {
    deck = [];
    for (const s of suits) {
      for (const r of ranks) {
        deck.push({ suit: s, rank: r });
      }
    }
  }

  function shuffle() {
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
  }

  function draw() {
    return deck.pop();
  }

  function valueOf(hand) {
    let total = 0;
    let aces = 0;
    for (const c of hand) {
      if (c.rank === 'A') {
        aces++;
        total += 11;
      } else if (['J', 'Q', 'K'].includes(c.rank)) {
        total += 10;
      } else {
        total += Number(c.rank);
      }
    }
    while (total > 21 && aces > 0) {
      total -= 10;
      aces--;
    }
    return total;
  }

  function renderCards(el, hand, hideFirst = false) {
    el.innerHTML = '';
    hand.forEach((c, i) => {
      const div = document.createElement('div');
      div.className = 'card';
      div.textContent = hideFirst && i === 0 ? '🂠' : `${c.rank}${c.suit}`;
      el.appendChild(div);
    });
  }

  function updateGameUI(hideDealerFirst = false) {
    gameBalance.textContent = balance;
    gameBet.textContent = currentBet;
    $('player-total').textContent = valueOf(player);
    $('dealer-total').textContent = hideDealerFirst ? '?' : valueOf(dealer);
    renderCards($('player-cards'), player);
    renderCards($('dealer-cards'), dealer, hideDealerFirst);
  }

  function endRound(message) {
    $('message').textContent = message;
    hitBtn.disabled = true;
    standBtn.disabled = true;
    nextBtn.disabled = false;
  }

  function switchToGame() {
    betScreen.classList.remove('active');
    gameScreen.classList.add('active');
  }

  function switchToBet() {
    gameScreen.classList.remove('active');
    betScreen.classList.add('active');
    player = [];
    dealer = [];
    $('player-cards').innerHTML = '';
    $('dealer-cards').innerHTML = '';
    $('player-total').textContent = '0';
    $('dealer-total').textContent = '0';
    $('message').textContent = '';
  }

  // Bet Screen Events
  presetBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      currentBet = Number(btn.getAttribute('data-bet'));
      betDisplay.textContent = currentBet;
    });
  });

  customBetInput.addEventListener('change', () => {
    const val = Number(customBetInput.value);
    if (val > 0) {
      currentBet = val;
      betDisplay.textContent = currentBet;
    }
  });

  betBtn.addEventListener('click', () => {
    if (currentBet <= 0) {
      $('message').textContent = 'ベット額を選択してください';
      return;
    }
    if (currentBet > balance) {
      alert('残高不足です');
      return;
    }
    balance -= currentBet;
    balanceDisplay.textContent = balance;

    // Start game
    buildDeck();
    shuffle();
    player = [draw(), draw()];
    dealer = [draw(), draw()];

    switchToGame();
    updateGameUI(true);

    // Check for blackjack immediately
    const pv = valueOf(player);
    const dv = valueOf(dealer);
    if (pv === 21) {
      hitBtn.disabled = true;
      standBtn.disabled = true;
      nextBtn.disabled = false;
      if (dv === 21) {
        balance += currentBet;
        balance += currentBet / 2;
        endRound('両者ブラックジャック: 引き分け');
      } else {
        balance += Math.floor(currentBet * 2.5);
        endRound('プレイヤーブラックジャック: 勝ち!');
      }
      updateGameUI(false);
    } else {
      hitBtn.disabled = false;
      standBtn.disabled = false;
    }
  });

  // Game Screen Events
  hitBtn.addEventListener('click', () => {
    player.push(draw());
    if (valueOf(player) > 21) {
      updateGameUI(false);
      endRound('バースト! 負け');
    } else {
      updateGameUI(true);
    }
  });

  standBtn.addEventListener('click', () => {
    while (valueOf(dealer) < 17) {
      dealer.push(draw());
    }
    const pv = valueOf(player);
    const dv = valueOf(dealer);
    if (dv > 21 || pv > dv) {
      balance += currentBet * 2;
      endRound('プレイヤーの勝ち!');
    } else if (pv === dv) {
      balance += currentBet;
      endRound('引き分け');
    } else {
      endRound('ディーラーの勝ち');
    }
    updateGameUI(false);
    balanceDisplay.textContent = balance;
  });

  nextBtn.addEventListener('click', () => {
    currentBet = 0;
    betDisplay.textContent = '0';
    customBetInput.value = '';
    switchToBet();
  });

  // Initialize
  balanceDisplay.textContent = balance;
})();

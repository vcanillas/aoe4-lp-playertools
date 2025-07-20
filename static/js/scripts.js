// Fetch all players on page load
fetch('/get_players')
    .then(res => res.json())
    .then(data => {
        players = data;
        // Populate dropdown and list box
        updatePlayerUI();
    });

function updatePlayerUI() {

    const sortedPlayers = Object.entries(players)
        .sort(([, nameA], [, nameB]) => nameA.localeCompare(nameB)); // Sort by name

    const playerSelect = document.getElementById("playerSelect");
    playerSelect.innerHTML = ""; // Clear existing options

    sortedPlayers.forEach(([playerId, playerName]) => {
        const option = document.createElement('option');
        option.value = playerId;
        option.text = playerName;
        playerSelect.appendChild(option);
    });
}

function updateGameUI() {
    if (!maps) return;  // Check if maps data exists

    Object.keys(maps).forEach(mapKey => {
        const map = maps[mapKey];

        const listItem = document.createElement('option');
        listItem.textContent = map.summary; // Display the map name in the list
        listItem.addEventListener('click', function () {
            handleMapClick(map);
        });
        gamesSelect.appendChild(listItem);
    });

    let player_id = maps[0].teams[0].players[0].profile_id;
    console.log(player_id);
    document.getElementById("playerSelect").value = player_id;

}

function clearScreen() {
    document.getElementById("playerTextBox").value = "";
    document.getElementById('gamesSelect').innerHTML = "";
    document.getElementById('lpOpponent1').innerHTML = "";
    document.getElementById('lpOpponent2').innerHTML = "";
    document.getElementById('lpDateTime').innerHTML = "";
    document.getElementById('mapTextArea').value = "";
    document.getElementById('mapDetails').value = "";
}

function handleMapClick(selectedMap) {
    currentMap = selectedMap;

    document.getElementById('mapTextArea').value = selectedMap.lp;
    document.getElementById('mapDetails').value = JSON.stringify(selectedMap, null, 2);

    document.getElementById('lpDateTime').innerHTML = selectedMap.date_lp;
    document.getElementById('lpOpponent1').innerHTML = selectedMap.teams[0].players[0].name_lp;
    document.getElementById('lpOpponent2').innerHTML = selectedMap.teams[1].players[0].name_lp;
}

function onClickGamesBtn() {

    fetch('/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            player_id: document.getElementById("playerSelect").value,
            player_id2: document.getElementById("playerTextBox").value
        }),
    })
        .then(response => response.json())
        .then(data => {
            clearScreen();

            players = data.players;
            maps = data.maps;
            updatePlayerUI();
            updateGameUI();
        })
        .catch(error => console.error("Error fetching game data:", error));
}

function onClickCopyLpDateTime() {
    const text = document.getElementById('lpDateTime').innerHTML;
    navigator.clipboard.writeText(text);
}

function onClickCopyToClipboard() {
    const text = document.getElementById('mapTextArea').value;
    navigator.clipboard.writeText(text).then(() => {
        // Optional: add success feedback
    }).catch(() => {
        // fallback method
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        try {
            document.execCommand('copy');
            alert('Copied to clipboard!');
        } catch (err) {
            alert('Failed to copy.');
        }
        document.body.removeChild(textarea);
    });
}

function onClickReverseLP() {
    const textarea = document.getElementById('mapTextArea');
    let text = textarea.value;

    // Parse lines
    const lines = text.split(/[\n|]/).map(line => line.trim()).filter(line => line);
    const keyValues = {};
    lines.forEach(line => {
        line = line.replace(/^\|/, '').trim();
        const [key, ...rest] = line.split('=');
        const value = rest.join('=').trim();
        keyValues[key.trim()] = value;
    });

    // Swap winner
    const winner = keyValues['winner'];
    keyValues['winner'] = winner === '1' ? '2' : '1';

    // Swap civs
    const civs1 = keyValues['civs1'];
    const civs2 = keyValues['civs2'];
    keyValues['civs1'] = civs2;
    keyValues['civs2'] = civs1;

    // Rebuild template
    const newTemplate = `{{Map
        |map=${keyValues['map']}|winner=${keyValues['winner']}
        |civs1=${keyValues['civs1']}
        |civs2=${keyValues['civs2']}
    }}`;

    textarea.value = newTemplate;

    // Swap opponent names in UI
    const opponent1 = document.getElementById('lpOpponent1').innerHTML;
    const opponent2 = document.getElementById('lpOpponent2').innerHTML;
    document.getElementById('lpOpponent1').innerHTML = opponent2;
    document.getElementById('lpOpponent2').innerHTML = opponent1;
}

function onClickViewGames() {
    document.getElementById("playerTextBox").value = currentMap.teams[1].players[0].profile_id;
    onClickGamesBtn();
}
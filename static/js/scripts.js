if (!library)
    var library = {};

library.json = {
    replacer: function (match, pIndent, pKey, pVal, pEnd) {
        var key = '<span class=json-key>';
        var val = '<span class=json-value>';
        var str = '<span class=json-string>';
        var r = pIndent || '';
        if (pKey)
            r = r + key + pKey.replace(/[": ]/g, '') + '</span>: ';
        if (pVal)
            r = r + (pVal[0] == '"' ? str : val) + pVal + '</span>';
        return r + (pEnd || '');
    },
    prettyPrint: function (obj) {
        var jsonLine = /^( *)("[\w]+": )?("[^"]*"|[\w.+-]*)?([,[{])?$/mg;
        return JSON.stringify(obj, null, 2)
            .replace(/&/g, '&amp;').replace(/\\"/g, '&quot;')
            .replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(jsonLine, library.json.replacer);
    },
    // New method to create a table from JSON data
    createTable: function (jsonData, containerId) {
        if (!Array.isArray(jsonData) || jsonData.length === 0) {
            console.error("Invalid or empty JSON data"); return;
        }

        var container = document.getElementById(containerId);
        if (!container) { console.error("Container element not found"); return; }

        // Create table element
        var table = document.createElement("table");
        table.className = "jsonTable"

        // Extract keys (titles) from the first object
        var keys = Object.keys(jsonData[0]);

        // Create header row
        var thead = document.createElement("thead");
        var headerRow = document.createElement("tr");
        keys.forEach(function (key) {
            var th = document.createElement("th");
            th.textContent = key;
            th.className = "jsonTable"
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create body rows
        var tbody = document.createElement("tbody");
        jsonData.forEach(function (item) {
            var row = document.createElement("tr");
            keys.forEach(function (key) {
                var td = document.createElement("td");
                td.className = "jsonTable"
                td.textContent = item[key] !== undefined ? item[key] : "";
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        table.appendChild(tbody);

        // Clear previous content and append new table
        container.innerHTML = "";
        container.appendChild(table);
    }
};

// Fetch all players on page load
fetch('/players')
    .then(res => res.json())
    .then(data => {
        players = data;
        // Populate dropdown and list box
        updatePlayerUI();
    });

refreshDrafts();

function onClickThemeToggle() {
    document.body.classList.toggle('dark-theme');
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
}

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

function updateGamesSelectUI() {
    if (!maps) return;  // Check if maps data exists

    gamesSelect = document.getElementById('gamesSelect');

    Object.keys(maps).forEach(mapKey => {
        const map = maps[mapKey];

        const listItem = document.createElement('option');
        listItem.textContent = map.summary; // Display the map name in the list
        listItem._mapData = map;
        gamesSelect.appendChild(listItem);
    });

    gamesSelect.addEventListener('change', onChangeGamesSelect);

    let player_id = maps[0].teams[0].players[0].profile_id;
    document.getElementById("playerSelect").value = player_id; // Auto-selected on the listbox
}

function clearScreen() {
    document.getElementById("playerTextBox").value = "";
    document.getElementById('gamesSelect').innerHTML = "";
    document.getElementById('gamesSelect').removeEventListener("change", onChangeGamesSelect)
    document.getElementById('lpOpponent1').innerHTML = "";
    document.getElementById('lpOpponent2').innerHTML = "";
    document.getElementById('lpDateTime').innerHTML = "";
    document.getElementById('mapTextArea').value = "";
    document.getElementById('jsonArea').innerHTML = "";
}

function getIcons(civ, winner) {
    var output = `<img src="${staticUrl}icons/${civ}.png" alt="${civ}" style="width: 30px" /> - `;
    if (winner.result_type == 1) { output += "👑 " }
    return output
}

function onChangeGamesSelect() {
    const selectedIndex = gamesSelect.selectedIndex;
    const selectedOption = gamesSelect.options[selectedIndex];

    const selectedMap = selectedOption._mapData;
    if (selectedMap) {
        currentMap = selectedMap; // Store for onClickViewGames()

        document.getElementById('mapTextArea').value = selectedMap.lp.content;
        document.getElementById('jsonArea').innerHTML = library.json.prettyPrint(selectedMap);
        document.getElementById('lpDateTime').innerHTML = selectedMap.lp.date;
        document.getElementById('lpOpponent1').innerHTML = getIcons(selectedMap.teams[0].players[0].civilization_lp, selectedMap.teams[0]) + selectedMap.teams[0].players[0].name;
        document.getElementById('lpOpponent2').innerHTML = getIcons(selectedMap.teams[1].players[0].civilization_lp, selectedMap.teams[1]) + selectedMap.teams[1].players[0].name;
    }
}


function onClickGamesBtn(button) {

    addIsInfo(button);

    fetch('/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            player_id: document.getElementById("playerSelect").value,
            player_id2: document.getElementById("playerTextBox").value,
            live_game: document.getElementById("playerCheckbox").checked
        }),
    })
        .then(response => response.json())
        .then(data => {
            clearScreen();

            players = data.players;
            maps = data.maps;

            if (maps.length == 0) { alert("No Games"); return; }
            updatePlayerUI();
            updateGamesSelectUI();
        })
        .catch(error => console.error("Error fetching game data:", error))
        .finally(() => removeIsInfo(button));
}

function onClickCopyLpDateTime(button) {
    addIsInfo(button);
    const text = document.getElementById('lpDateTime').innerHTML;
    navigator.clipboard.writeText(text);
    setTimeout(() => {
        removeIsInfo(button);
    }, 500);
}

function onClickCopyToClipboard() {
    const text = document.getElementById('mapTextArea').value;
    navigator.clipboard.writeText(text).then(() => {
        const messageDiv = document.getElementById('validCopy');
        messageDiv.style.display = 'block';
        setTimeout(() => { messageDiv.style.display = 'none'; }, 2000);
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
    keyValues['winner'] = winner === '1' ? '2' : winner === '2' ? '1' : '';

    // Swap civs
    const civs1 = keyValues['civs1'];
    const civs2 = keyValues['civs2'];
    keyValues['civs1'] = civs2;
    keyValues['civs2'] = civs1;

    // Swap players if available
    if ('players1' in keyValues) {
        const players1 = keyValues['players1'];
        const players2 = keyValues['players2'];
        keyValues['players1'] = players2;
        keyValues['players2'] = players1;
    }

    // Rebuild template
    const newTemplate = `{{Map
        |map=${keyValues['map']}|winner=${keyValues['winner']}
${'players1' in keyValues ? `        |players1=${keyValues['players1']}\n` : ''}        |civs1=${keyValues['civs1']}
${'players2' in keyValues ? `        |players2=${keyValues['players2']}\n` : ''}        |civs2=${keyValues['civs2']}
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
    onClickGamesBtn(document.getElementById('gamesBtn'));
}

function onClickTabs(button) {
    // Select all tab buttons and contents
    const buttons = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    // Remove 'active' class from all buttons
    buttons.forEach(btn => btn.classList.remove('is-active'));

    // Add 'is-active' class to the clicked button
    button.classList.add('is-active');

    // Get the target tab ID from data attribute
    const tabId = button.getAttribute('data-tab');

    // Remove 'is-active' class from all tab contents
    contents.forEach(content => content.classList.remove('active'));

    // Add 'is-active' class to the selected tab content
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

function addIsInfo(button) {
    button.classList.add('is-info');
}

function removeIsInfo(button) {
    button.classList.remove('is-info');
}

// Events Admin

function onSubmitMapsForm(e) {
    e.preventDefault();
    const key = document.getElementById('mapKey').value;
    const value = document.getElementById('mapValue').value;
    fetch('/map', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: key, value: value })
    })
        .then(response => response.text())
        .then(data => alert(data))
        .catch(error => alert('Error: ' + error));
}

function onSubmitPlayersForm(e) {
    e.preventDefault();
    const key = document.getElementById('playerKey').value;
    const value = document.getElementById('playerValue').value;
    fetch('/player', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=UTF-8'
        },
        body: JSON.stringify({ id: key, value: value })
    })
        .then(response => response.text())
        .then(data => alert(data))
        .catch(error => alert('Error: ' + error));
}

function onSubmitSearchPlayersForm(e) {
    e.preventDefault();
    const button = e.target.querySelector('button');
    addIsInfo(button);

    const value = document.getElementById('searchPlayerValue').value;
    fetch('/search_player', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: value })
    })
        .then(response => response.text())
        .then(data => {
            const players = JSON.parse(data);
            let htmlContent = '';
            players.forEach(player => {
                htmlContent += `<p>${player.name} 
                -- <a href="#" onclick="onClickSelectPlayer('${player.profile_id}'); return false;">${player.profile_id}</a>
                -- ${player.country || 'N/A'} 
                - <a href="https://steamcommunity.com/profiles/${player.steam_id}" target="_blank">Steam</a>
                - ${player.lp_name || ''} 
                </p>`;
            });

            document.getElementById('searchPlayerResult').innerHTML = htmlContent;
        })
        .catch(error => alert('Error: ' + error))
        .finally(() => removeIsInfo(button));
}

function onSubmitParticipantsListForm(e) {
    e.preventDefault();
    const button = e.target.querySelector('button');
    addIsInfo(button);

    const value = document.getElementById('eventIdValue').value;
    const withFlag = document.getElementById('participantFlag').checked ? 1 : 0;

    fetch(`/participants?id=${value}&with_flag=${withFlag}`, {
        method: 'GET'
    })
        .then(response => response.text())
        .then(data => {
            document.getElementById('participantListResult').innerHTML = data;
        })
        .catch(error => alert('Error: ' + error))
        .finally(() => removeIsInfo(button));
}

function onClickSelectPlayer(profileId) {
    document.getElementById('playerTextBox').value = profileId; // or profileId if needed

    const tab1Button = document.querySelector('.tab-btn[data-tab="tab1"]');
    if (tab1Button) { tab1Button.click(); }

    return onClickGamesBtn(document.getElementById('gamesBtn'));
}

// Events Drafts

function refreshDrafts() {
    fetch('/drafts')
        .then(res => res.json())
        .then(data => {
            drafts = data;
            updateDraftUI();
        });
}

function updateDraftUI() {
    const draftSelect = document.getElementById("draftSelect");
    draftSelect.innerHTML = ""; // Clear existing options

    Object.entries(drafts).forEach(([draftId, draftPreset]) => {
        const option = document.createElement('option');
        option.value = draftPreset;
        option.text = draftId;
        draftSelect.appendChild(option);
    });
}

function onSubmitDraftForm(e) {
    e.preventDefault();

    const button = e.target.querySelector('button');
    addIsInfo(button);

    const selectElement = document.getElementById('draftSelect');
    const preset = selectElement.value;
    const key = selectElement.options[selectElement.selectedIndex].text;

    document.getElementById('draftLink').innerHTML = `
    ${key} - <br />
    <a href="https://aoe4world.com/api/v0/esports/drafts?preset=${preset}" target="_blank">https://aoe4world.com/api/v0/esports/drafts?preset=${preset}</a></p>
    `;

    fetch(`/draft?preset=${preset}`, {
        method: 'GET'
    })
        .then(response => response.text())
        .then(data => {
            var jsonData = JSON.parse(data);
            library.json.createTable(jsonData, "draftListResult");

            // document.getElementById('draftListResult').innerHTML = data;
        })
        .catch(error => alert('Error: ' + error))
        .finally(() => removeIsInfo(button));
}

function onSubmitAddDraftForm(e) {
    e.preventDefault();
    const key = document.getElementById('draftKey').value;
    const value = document.getElementById('draftValue').value;
    fetch('/draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: key, value: value })
    })
        .then(response => response.text())
        .then(data => alert(data))
        .then(() => refreshDrafts())
        .catch(error => alert('Error: ' + error));
}
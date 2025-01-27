import { html } from "./utils.js";

async function searchUsers() {
    const search = document.getElementById('search-users').value;
    const response = await fetch(`/api/users/search?user=${search}`);
    const users = await response.json();

    const usersList = document.getElementById('user-list');
    usersList.innerHTML = '';
    if (users.users.length) usersList.innerHTML = users.users.map(user => html`
        <a href="/profile?handle=${user.handle}">
            <div class="p-4 bg-gray-700 hover:bg-gray-500 rounded-md">
                <p class="text-white">${user.username}</p>
            </div>
        </a>
    `).join('');
}

searchUsers();
window.searchUsers = searchUsers;
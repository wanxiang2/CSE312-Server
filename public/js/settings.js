async function fetchUserSettings() {
  const response = await fetch("/api/users/settings");
  const userSettings = (await response.json())?.user;

    if (userSettings.avatar) {
        document.getElementById('avatar').src = userSettings.avatar;
    }
    if (userSettings.username) {
        document.getElementById('username').value = userSettings.username;
    }
    if (userSettings.handle) {
        document.getElementById('handle').value = userSettings.handle;
    }
}

fetchUserSettings();

document.getElementById("avatar").addEventListener("change", function (event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById("avatar-preview").src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
});

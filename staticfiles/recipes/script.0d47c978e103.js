// JavaScript Document
document.addEventListener('DOMContentLoaded', function () {
    const messages = JSON.parse(document.getElementById('django-messages').textContent);
    messages.forEach(message => {
        alert(message.message);
    });
});
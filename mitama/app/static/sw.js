self.addEventListener('push', function(event) {
    if (event.data) {
        let data = event.data.json();
        let title = data.title;
        event.waitUntil(self.registration.showNotification(title, data))
    }
})

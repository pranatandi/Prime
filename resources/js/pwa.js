/**
 * PWA Service Worker Registration and Management
 */

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('Service Worker registered successfully:', registration.scope);
                
                // Check for updates every hour
                setInterval(() => {
                    registration.update();
                }, 3600000);
            })
            .catch((error) => {
                console.error('Service Worker registration failed:', error);
            });
    });
}

// Handle service worker updates
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
    });
}

// PWA Install Prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing
    e.preventDefault();
    deferredPrompt = e;
    
    // Show custom install button/banner
    const installButton = document.getElementById('install-pwa-button');
    if (installButton) {
        installButton.style.display = 'block';
        
        installButton.addEventListener('click', () => {
            installButton.style.display = 'none';
            deferredPrompt.prompt();
            
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                } else {
                    console.log('User dismissed the install prompt');
                }
                deferredPrompt = null;
            });
        });
    }
});

// Track PWA install
window.addEventListener('appinstalled', () => {
    console.log('PWA was installed successfully');
    deferredPrompt = null;
});

// Online/Offline Detection
window.addEventListener('online', () => {
    console.log('Back online');
    document.body.classList.remove('offline');
    document.body.classList.add('online');
    
    // Show notification
    showNotification('You are back online', 'success');
    
    // Trigger background sync if available
    if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
        navigator.serviceWorker.ready.then((registration) => {
            return registration.sync.register('sync-weighing-data');
        });
    }
});

window.addEventListener('offline', () => {
    console.log('Gone offline');
    document.body.classList.remove('online');
    document.body.classList.add('offline');
    
    // Show notification
    showNotification('You are offline. Data will be synced when connection is restored.', 'warning');
});

// Push Notifications
function initPushNotifications() {
    if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return;
    }

    if (Notification.permission === 'granted') {
        subscribeToPushNotifications();
    } else if (Notification.permission !== 'denied') {
        const enableNotifButton = document.getElementById('enable-notifications');
        if (enableNotifButton) {
            enableNotifButton.addEventListener('click', () => {
                Notification.requestPermission().then((permission) => {
                    if (permission === 'granted') {
                        subscribeToPushNotifications();
                    }
                });
            });
        }
    }
}

async function subscribeToPushNotifications() {
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY || '')
        });
        
        // Send subscription to backend
        await fetch('/api/push-subscriptions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify(subscription)
        });
        
        console.log('Push notification subscription successful');
    } catch (error) {
        console.error('Failed to subscribe to push notifications:', error);
    }
}

// Helper function to convert VAPID key
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Helper function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initPushNotifications();
    
    // Set initial online/offline state
    if (navigator.onLine) {
        document.body.classList.add('online');
    } else {
        document.body.classList.add('offline');
    }
});

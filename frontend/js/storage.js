const Storage = {
    get(key) {
        try { return localStorage.getItem(key); } catch { return null; }
    },
    set(key, val) {
        try { localStorage.setItem(key, val); } catch {}
    },
    remove(key) {
        try { localStorage.removeItem(key); } catch {}
    }
};

window.Storage = Storage;

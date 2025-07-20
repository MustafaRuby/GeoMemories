<script>
import { onMount } from 'svelte';
import { goto } from '$app/navigation';
let email = '';
let password = '';
let error = '';

onMount(() => {
    // Se già autenticato, vai alla home
    if (localStorage.getItem('token')) {
        goto('/');
    }
});

async function login() {
    error = '';
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({ email: data.email, name: data.name }));
        goto('/');
    } else {
        error = data.error || 'Errore di autenticazione';
    }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;500;700&display=swap');
:global(body) {
    background: linear-gradient(120deg, #23272f 0%, #181c24 100%);
    color: #e0e6ed;
    font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    margin: 0;
}
.login-container {
    background: #23272f;
    border-radius: 18px;
    box-shadow: 0 8px 32px 0 rgba(20, 20, 40, 0.45);
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    min-width: 340px;
    max-width: 400px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 3rem auto;
}
@media (max-width: 500px) {
    .login-container {
        max-width: 98vw;
        padding: 1.2rem 0.5rem 1.2rem 0.5rem;
    }
}
h2 {
    color: #ffb86b;
    margin-bottom: 1.5rem;
    font-size: 2rem;
    font-family: 'Fira Mono', monospace;
}
form {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: stretch;
}
.input-beauty {
    padding: 0.7rem 1.2rem;
    border-radius: 10px;
    border: 1.5px solid #2d3a4a;
    background: #181c24;
    color: #e0e6ed;
    font-size: 1.1rem;
    margin-bottom: 1.1rem;
    width: 100%;
    transition: border 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.13);
    box-sizing: border-box;
    font-family: 'Fira Mono', monospace;
}
.input-beauty:focus {
    border: 2px solid #ffb86b;
    outline: none;
    box-shadow: 0 4px 16px rgba(255,184,107,0.13);
}
.btn-dark {
    background: linear-gradient(90deg, #23272f 0%, #2d3a4a 100%);
    color: #7ddaff;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.13);
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
    margin-top: 0.5rem;
    font-family: 'Fira Mono', monospace;
}
.btn-dark:hover {
    background: linear-gradient(90deg, #2d3a4a 0%, #23272f 100%);
    color: #fff;
    transform: translateY(-2px) scale(1.04);
}
.switch-link {
    color: #ffb86b;
    margin-top: 1.2rem;
    font-size: 1rem;
    text-decoration: underline;
    cursor: pointer;
    font-family: 'Fira Mono', monospace;
}
.error-message {
    color: #ff7eb3;
    margin-bottom: 1rem;
    font-size: 1.05rem;
    font-family: 'Fira Mono', monospace;
}
</style>

<div class="login-container">
    <h2>GeoMemories</h2>
    {#if error}
        <div class="error-message">{error}</div>
    {/if}
    <form on:submit|preventDefault={login}>
        <input type="email" class="input-beauty" placeholder="Email" bind:value={email} required autocomplete="username" />
        <input type="password" class="input-beauty" placeholder="Password" bind:value={password} required autocomplete="current-password" />
        <button type="submit" class="btn-dark">Accedi</button>
    </form>
    <a href="/register" class="switch-link">Non hai un account? Registrati</a>
</div>

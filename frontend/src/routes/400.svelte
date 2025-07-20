<script>
    import { goto } from '$app/navigation';

    function goHome() {
        goto('/');
    }
</script>

<style>
    :global(body) {
        background: linear-gradient(120deg, #23272f 0%, #181c24 100%) !important;
    }
    .error-bg {
        font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
        background: linear-gradient(120deg, #23272f 0%, #181c24 100%);
        color: #ffb86b;
        text-align: center;
        padding-top: 12vh;
        min-height: 100vh;
        margin: 0;
    }
    .error-container {
        background: #23272f;
        border-radius: 18px;
        box-shadow: 0 8px 32px 0 rgba(20, 20, 40, 0.45);
        display: inline-block;
        padding: 2.5rem 3.5rem 2.5rem 3.5rem;
    }
    h1 {
        font-size: 5em;
        color: #f4a261;
        margin-bottom: 0.2em;
        letter-spacing: 2px;
    }
    p {
        font-size: 1.5em;
        color: #e0e6ed;
        margin-top: 0.5em;
    }
    a {
        color: #7ddaff;
        text-decoration: underline;
        font-size: 1.1em;
        cursor: pointer;
    }
    a:hover {
        color: #ffb86b;
    }
</style>

<div class="error-bg">
    <div class="error-container">
        <h1>400</h1>
        <p>Richiesta non valida.</p>
        <p><a on:click={goHome}>Torna alla Home</a></p>
    </div>
</div>

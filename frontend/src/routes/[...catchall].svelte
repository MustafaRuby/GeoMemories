<script>
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    
    onMount(() => {
        // Redirect to the 404 page handled by SvelteKit
        goto('/404', { replaceState: true });
    });
</script>

<!-- Fallback content while redirecting -->
<div style="display: flex; justify-content: center; align-items: center; height: 100vh; color: #fff; background: #23272f;">
    <p>Redirecting...</p>
</div>

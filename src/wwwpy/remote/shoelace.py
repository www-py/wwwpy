from js import document
import js

def setup_shoelace():
    document.documentElement.className = 'sl-theme-dark'
    document.head.append(document.createRange().createContextualFragment(_head_style))



# language=html
_head_style = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
<style>@import 'https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.1/cdn/themes/dark.css';</style>
<style>
    body {
        font: 16px sans-serif;
        background-color: var(--sl-color-neutral-0);
        color: var(--sl-color-neutral-900);
        padding: 1rem;
    }
</style>
<script type="module" src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.1/cdn/shoelace.js"></script>
"""

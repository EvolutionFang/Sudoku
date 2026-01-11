<script>
	import { userGrid } from '@sudoku/stores/grid';
	import { cursor } from '@sudoku/stores/cursor';
	import { notes } from '@sudoku/stores/notes';
	import { candidates as candidatesStore } from '@sudoku/stores/candidates';
	import { 
		keyboardDisabled, isHintActive, hintCandidates, triedCandidates, 
		handleKeyButton as processKey 
	} from '@sudoku/stores/keyboard';
	import { historyTree } from '@sudoku/stores/treeHistoryManager';

	$: isInBacktrackMode = $historyTree.isInBacktrackMode;

	/**
	 * Encapsulates store values and instances to pass to the domain logic.
	 */
	function onKeyClick(num) {
		processKey(num, {
			$keyboardDisabled, $isHintActive, $hintCandidates, $notes, $cursor, $userGrid,
			userGrid, candidatesStore, historyTree, isInBacktrackMode
		});
	}

	function handleKey(e) {
		const key = e.key || e.keyCode;
		if (['ArrowUp', 38, 'w', 87].includes(key)) cursor.move(0, -1);
		else if (['ArrowDown', 40, 's', 83].includes(key)) cursor.move(0, 1);
		else if (['ArrowLeft', 37, 'a', 65].includes(key)) cursor.move(-1);
		else if (['ArrowRight', 39, 'd', 68].includes(key)) cursor.move(1);
		else if (['Backspace', 8, 'Delete', 46].includes(key)) onKeyClick(0);
		else {
			const num = parseInt(e.key);
			if (!isNaN(num) && num >= 0 && num <= 9) onKeyClick(num);
		}
	}
</script>

<svelte:window on:keydown={handleKey} />

<div class="keyboard-grid">
	{#each Array(10) as _, i}
		{@const num = i + 1}
		{#if i === 9}
			<!-- Erase Button -->
			<button class="btn btn-key" disabled={$keyboardDisabled} on:click={() => onKeyClick(0)}>
				<svg class="icon-outline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			</button>
		{:else}
			<!-- Digit Button -->
			<button class="btn btn-key" 
					class:tried={$isHintActive && $triedCandidates.includes(num)}
					class:dimmed={$isHintActive && !$hintCandidates.includes(num)}
					disabled={$keyboardDisabled || ($isHintActive && !$hintCandidates.includes(num))}
					on:click={() => onKeyClick(num)}>
				{num}
			</button>
		{/if}
	{/each}
</div>

<style>
	.keyboard-grid { @apply grid grid-rows-2 grid-cols-5 gap-3; }
	.btn-key { @apply py-4 px-0 transition-all duration-200; }
	.dimmed { opacity: 0.1; pointer-events: none; }
	.tried { @apply font-bold; background-color: #fef9c3; color: #a16207; border: 2px solid #facc15; }
</style>
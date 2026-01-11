<script>
	import { userGrid } from '@sudoku/stores/grid';
	import { cursor } from '@sudoku/stores/cursor';
	import { hints } from '@sudoku/stores/hints';
	import { notes } from '@sudoku/stores/notes';
	import { settings } from '@sudoku/stores/settings';
	import { keyboardDisabled, isHintActive, setKeyboardHints } from '@sudoku/stores/keyboard';
	import { gamePaused } from '@sudoku/stores/game';
	import { undo, redo, historyStatus } from '@sudoku/stores/history';
	import { performBacktrack, historyTree } from '@sudoku/stores/treeHistoryManager';

	$: canBacktrack = $historyTree.canBacktrack;
	$: canUndo = $historyStatus.canUndo;
	$: canRedo = $historyStatus.canRedo;
	$: hintsAvailable = $hints > 0;
	$: isCellEmpty = $userGrid[$cursor.y] && $userGrid[$cursor.y][$cursor.x] === 0;

	let hintText = '';

	/**
	 * Triggers the intelligent hint calculation.
	 * Passes setKeyboardHints to break the circular dependency chain.
	 */
	function handleSmartHint() {
		if (!hintsAvailable || !isCellEmpty || $gamePaused) return;
		// Inject the keyboard update function as a dependency
		hintText = hints.handleSmartHint($userGrid, $cursor, historyTree, setKeyboardHints);
	}

	/**
	 * Manages the smart backtrack operation.
	 */
	function handleBacktrack() {
		if (performBacktrack()) {
			const currentNode = historyTree.getCurrentNodeInfo();
			if (currentNode?.infos) {
				hintText = "Backtracked → Decision Point";
				setKeyboardHints(currentNode.infos.candidates, currentNode.infos.tried);
			}
		}
	}
</script>

<div class="flex flex-col w-full">
	<div class="action-buttons space-x-3">
		<!-- Backtrack -->
		<button class="btn btn-round btn-badge" disabled={$gamePaused || !canBacktrack} on:click={handleBacktrack} title="Backtrack">
			{#if $historyTree.isInBacktrackMode}
				<span class="absolute top-0 right-0 -mt-1 -mr-1 flex h-3 w-3">
					<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
					<span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
				</span>
			{/if}
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
			</svg>
		</button>

		<!-- History Controls -->
		<button class="btn btn-round" disabled={$gamePaused || !canUndo} on:click={undo} title="Undo">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
			</svg>
		</button>
		<button class="btn btn-round" disabled={$gamePaused || !canRedo} on:click={redo} title="Redo">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10h-10a8 8 90 00-8 8v2M21 10l-6 6m6-6l-6-6" />
			</svg>
		</button>

		<!-- Hint -->
		<button class="btn btn-round btn-badge" class:ring-4={$isHintActive} class:ring-yellow-300={$isHintActive}
				disabled={$keyboardDisabled || !hintsAvailable || !isCellEmpty} on:click={handleSmartHint} title="Hint">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
			</svg>
			{#if $settings.hintsLimited}
				<span class="badge" class:badge-primary={hintsAvailable}>{$hints}</span>
			{/if}
		</button>

		<!-- Notes -->
		<button class="btn btn-round btn-badge" on:click={notes.toggle} title="Notes">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
			</svg>
			<span class="badge tracking-tighter" class:badge-primary={$notes}>{$notes ? 'ON' : 'OFF'}</span>
		</button>
	</div>

	<!-- Information Area -->
	<div class="h-6 mb-2 w-full text-center">
		{#if $isHintActive && hintText}
			<span class="text-sm font-semibold text-gray-500 tracking-wide fade-in">
				{hintText}
			</span>
		{/if}
	</div>
</div>

<style>
	.action-buttons { @apply flex flex-wrap justify-evenly self-end; }
	.btn-badge { @apply relative; }
	.badge { 
		@apply p-1 rounded-full leading-none text-center text-xs text-white bg-gray-600 inline-block absolute top-0 left-0;
		min-width: 20px;
		min-height: 20px;
	}
	.badge-primary { @apply bg-primary; }
	.fade-in { animation: fadeIn 0.3s ease-in-out; }
	@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
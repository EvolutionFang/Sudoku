<script>
	import { userGrid } from '@sudoku/stores/grid';
	import { cursor } from '@sudoku/stores/cursor';
	import { notes } from '@sudoku/stores/notes';
	import { candidates } from '@sudoku/stores/candidates';
	// Removed dependency on difficulty store
	import { getCandidateSet } from '@sudoku/strategies'; // Removed getStrategiesByDifficulty import
	
	import { 
		keyboardDisabled, 
		isHintActive, 
		hintCandidates, 
		triedCandidates, 
		resetKeyboardHints 
	} from '@sudoku/stores/keyboard';

	import {
		saveUserAction,
		historyTree
	} from '@sudoku/stores/treeHistoryManager';
	
	$: isInBacktrackMode = $historyTree.isInBacktrackMode;

	function handleKeyButton(num) {
		// Check if hint mode is active
		if ($isHintActive && num !== 0) {
			if (!$hintCandidates.includes(num)) {
				return;
			}
		}

		if (!$keyboardDisabled) {
			if ($notes) {
				if (num === 0) {
					candidates.clear($cursor);
				} else {
					candidates.add($cursor, num);
				}
				userGrid.set($cursor, 0); 
			} else {
				if ($candidates.hasOwnProperty($cursor.x + ',' + $cursor.y)) {
					candidates.clear($cursor);
				}
				
				// --- Core Logic Modification Start ---
				// Requirement update: Decouple from difficulty settings. 
				// Use basic strategies to calculate candidates. 
				// This ensures identified "Decision Points" represent genuine branching needs (guessing) 
				// rather than missing logic due to strategy restrictions.
				// Calculate basic candidates
				const basicStrategies = []; 
				const total_candidates = getCandidateSet($userGrid, basicStrategies);
				let cellCandidates = total_candidates[$cursor.y][$cursor.x];
				
				// --- Backtracking Logic Fix Start ---
                
                // 1. Retrieve the current node from the history tree
                const currentNode = historyTree.getCurrentNodeInfo();
                
                // 2. Determine if the operation targets the same cell
                // If in backtrack mode and the current node's coordinates match the cursor's coordinates,
                // it indicates modifying the current decision branch (overwriting).
                let isSameCellDecision = false;
                if (isInBacktrackMode && currentNode && currentNode.infos && currentNode.infos.cell) {
                    if (currentNode.infos.cell.x === $cursor.x && currentNode.infos.cell.y === $cursor.y) {
                        isSameCellDecision = true;
                    }
                }

				// 3. Determine instantiation of a new Decision Point
                // Condition A: Ambiguous cell requiring a guess (candidates > 1)
                // Condition B: 
                //    - Either not in backtrack mode (standard play flow)
                //    - Or in backtrack mode but operating on a different cell (initiating nested speculation)
                // If isSameCellDecision is true, simply modifying the current decision branch; no new parent node required.
				if(cellCandidates && cellCandidates.length > 1 && (!isInBacktrackMode || !isSameCellDecision)) {
					saveUserAction($cursor, num, cellCandidates, true);
				}
				// --- Backtracking Logic Fix End ---
				
				userGrid.set($cursor, num);
				saveUserAction($cursor, num, cellCandidates, false);
			}

			resetKeyboardHints();
		}
	}

	function handleKey(e) {
		switch (e.key || e.keyCode) {
			case 'ArrowUp': case 38: case 'w': case 87: cursor.move(0, -1); break;
			case 'ArrowDown': case 40: case 's': case 83: cursor.move(0, 1); break;
			case 'ArrowLeft': case 37: case 'a': case 65: cursor.move(-1); break;
			case 'ArrowRight': case 39: case 'd': case 68: cursor.move(1); break;
			
			case 'Backspace': case 8: case 'Delete': case 46:
				handleKeyButton(0);
				break;

			default:
				if (e.key && e.key * 1 >= 0 && e.key * 1 < 10) {
					handleKeyButton(e.key * 1);
				} else if (e.keyCode - 48 >= 0 && e.keyCode - 48 < 10) {
					handleKeyButton(e.keyCode - 48);
				}
				break;
		}
	}
</script>

<svelte:window on:keydown={handleKey} />

<div class="keyboard-grid">

	{#each Array(10) as _, keyNum}
		{#if keyNum === 9}
			<!-- Clear/Delete Button -->
			<button class="btn btn-key" disabled={$keyboardDisabled} title="Erase Field" on:click={() => handleKeyButton(0)}>
				<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			</button>
		{:else}
			{@const num = keyNum + 1}
			{@const isCandidate = $hintCandidates.includes(num)}
			{@const isTried = $triedCandidates.includes(num)}
			
			<!-- Number Button -->
			<button class="btn btn-key" 
					class:tried={$isHintActive && isTried}
					class:dimmed={$isHintActive && !isCandidate}
					disabled={$keyboardDisabled || ($isHintActive && !isCandidate)}
					title="Insert {num}" 
					on:click={() => handleKeyButton(num)}>
				{num}
			</button>
		{/if}
	{/each}

</div>

<style>
	.keyboard-grid {
		@apply grid grid-rows-2 grid-cols-5 gap-3;
	}

	.btn-key {
		@apply py-4 px-0 transition-all duration-200;
	}

	/* Digits logically invalid: Dimmed */
	.dimmed {
		opacity: 0.1;
		pointer-events: none;
	}

	/* 
       Digits attempted leading to failure: Highlighted Yellow/Orange
    */
	.tried {
		background-color: #fef9c3; 
		color: #a16207;           
		border: 2px solid #facc15; 
		font-weight: bold;
	}
</style>
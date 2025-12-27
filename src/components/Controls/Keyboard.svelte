<script>
	import { userGrid } from '@sudoku/stores/grid';
	import { cursor } from '@sudoku/stores/cursor';
	import { notes } from '@sudoku/stores/notes';
	import { candidates } from '@sudoku/stores/candidates';
	// TODO: Improve keyboardDisabled
	import { keyboardDisabled } from '@sudoku/stores/keyboard';
	
	import { 
		saveUserAction 
	} from '@sudoku/history/actionHelpers';

	async function handleKeyButton(num) {
		if (!$keyboardDisabled && $cursor.x !== null && $cursor.y !== null) {
			const currentCell = { x: $cursor.x, y: $cursor.y };
			const isErasing = num === 0;
			
			if ($notes) {
				// --- 笔记模式 (Pencil Marks) ---
				if (isErasing) {
					candidates.clear($cursor);
				} else {
					candidates.add($cursor, num);
				}
				// 注意：笔记模式下通常不 set userGrid，保持格子为 0
				// 如果你的业务逻辑要求笔记模式也要填数，请保留下面这行：
				// userGrid.set($cursor, 0); 

				// 笔记操作一般不需要回溯，第三个参数传 null
				saveUserAction(currentCell, num, null);
			} else {
				// --- 普通填数模式 ---
				
				// 填数前，如果该位置有笔记，先清空笔记
				candidates.clear($cursor);

				let cellCandidates = null;
				// 如果不是擦除操作，计算当前的合法选项，用于后续“自动回溯”
				if (!isErasing) {
					cellCandidates = calculateCellCandidates($userGrid, currentCell.x, currentCell.y);
				}
				
				// 先更新界面数据
				userGrid.set($cursor, num);
				
				// 核心：保存动作。此时 saveUserAction 会记录：
				// 1. 填入后的棋盘 2. 刚才计算的可选数字（如果 >2 个，回溯按钮就会亮起）
				saveUserAction(currentCell, num, cellCandidates);
			}
			
			return true;
		}
		
		return false;
	}

	function handleKey(e) {
		switch (e.key || e.keyCode) {
			case 'ArrowUp':
			case 38:
			case 'w':
			case 87:
				cursor.move(0, -1);
				break;

			case 'ArrowDown':
			case 40:
			case 's':
			case 83:
				cursor.move(0, 1);
				break;

			case 'ArrowLeft':
			case 37:
			case 'a':
			case 65:
				cursor.move(-1);
				break;

			case 'ArrowRight':
			case 39:
			case 'd':
			case 68:
				cursor.move(1);
				break;

			case 'Backspace':
			case 8:
			case 'Delete':
			case 46:
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

	function calculateCellCandidates(grid, x, y) {
		
		const candidates = [];
		for (let num = 1; num <= 9; num++) {
			let valid = true;
	
			for (let col = 0; col < 9; col++) {
				if (grid[y][col] === num) valid = false;
			}
			
			for (let row = 0; row < 9; row++) {
				if (grid[row][x] === num) valid = false;
			}
			
			const startRow = Math.floor(y / 3) * 3;
			const startCol = Math.floor(x / 3) * 3;
			for (let row = startRow; row < startRow + 3; row++) {
				for (let col = startCol; col < startCol + 3; col++) {
					if (grid[row][col] === num) valid = false;
				}
			}
			
			if (valid) candidates.push(num);
		}
		
		return candidates;
	}
</script>

<svelte:window on:keydown={handleKey} /><!--on:beforeunload|preventDefault={e => e.returnValue = ''} />-->

<div class="keyboard-grid">

	{#each Array(10) as _, keyNum}
		{#if keyNum === 9}
			<button class="btn btn-key" disabled={$keyboardDisabled} title="Erase Field" on:click={() => handleKeyButton(0)}>
				<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			</button>
		{:else}
			<button class="btn btn-key" disabled={$keyboardDisabled} title="Insert {keyNum + 1}" on:click={() => handleKeyButton(keyNum + 1)}>
				{keyNum + 1}
			</button>
		{/if}
	{/each}

</div>

<style>
	.keyboard-grid {
		@apply grid grid-rows-2 grid-cols-5 gap-3;
	}

	.btn-key {
		@apply py-4 px-0;
	}
</style>
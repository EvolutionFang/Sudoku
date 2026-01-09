<script>
	import { userGrid } from '@sudoku/stores/grid';
	import { cursor } from '@sudoku/stores/cursor';
	import { notes } from '@sudoku/stores/notes';
	import { candidates } from '@sudoku/stores/candidates';
	import { difficulty } from '@sudoku/stores/difficulty'; // 引入难度
	import { getCandidateSet, getStrategiesByDifficulty } from '@sudoku/strategies'; // 引入映射函数
	// 引入新的 store 和方法
	// 引入 triedCandidates
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
		// 如果处于提示模式
		if ($isHintActive && num !== 0) {
			// 修改逻辑：只有当数字"不在"候选列表中时才拦截。
			// 即使数字在 triedCandidates (已尝试) 中，因为它肯定也在 hintCandidates 中，所以允许点击。
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
				// 笔记模式通常不填入 UserGrid，但也视具体逻辑而定
				userGrid.set($cursor, 0); 
			} else {
				// 填入数字前，先处理候选数逻辑用于历史记录
				if ($candidates.hasOwnProperty($cursor.x + ',' + $cursor.y)) {
					candidates.clear($cursor);
				}
				
				// --- 严格保留你的核心逻辑 Start ---
				// 获取当前难度对应的策略列表
				const strategies = getStrategiesByDifficulty($difficulty);
				// 传入策略列表进行计算
				const total_candidates = getCandidateSet($userGrid, strategies);
				console.log('Total Candidates before inserting number:', total_candidates);
				let cellCandidates = total_candidates[$cursor.y][$cursor.x]; // 注意行列顺序
				console.log(`Candidates for cell (${$cursor.x}, ${$cursor.y}):`, cellCandidates);

				// 智能回溯的核心记录点：
				if(cellCandidates.length > 1 && !isInBacktrackMode) {
					saveUserAction($cursor, num, cellCandidates, true);
				}
				
				userGrid.set($cursor, num);
				saveUserAction($cursor, num, cellCandidates, false);
				// --- 严格保留你的核心逻辑 End ---
			}

			// 核心逻辑：填入数字后，自动重置提示状态
			resetKeyboardHints();
		}
	}

	// 键盘事件处理保持不变
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
			<!-- 清除/删除按钮 -->
			<button class="btn btn-key" disabled={$keyboardDisabled} title="Erase Field" on:click={() => handleKeyButton(0)}>
				<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			</button>
		{:else}
			{@const num = keyNum + 1}
			{@const isCandidate = $hintCandidates.includes(num)}
			{@const isTried = $triedCandidates.includes(num)}
			
			<!-- 数字按钮 -->
			<!-- 
				class逻辑:
				tried: 提示激活 且 已尝试 -> 黄色 (允许点击)
				dimmed: 提示激活 且 不在候选集中 -> 变暗 (不可点击)
				
				disabled逻辑:
				只在以下情况禁用：
				1. 整个键盘被禁用
				2. 提示激活 且 该数字根本不在候选集中 (排除了 isTried 的判断，所以已尝试的数字可以点)
			-->
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

	/* 不符合逻辑的数字：变暗 */
	.dimmed {
		opacity: 0.1; /* 为了明显的视觉效果，建议设低一点，原先0.4也可以 */
		pointer-events: none;
	}

	/* 
	   已经尝试过导致失败的数字：标蓝
	   注意：移除了 pointer-events: none，所以可以点击
	*/
	.tried {
		background-color: #fef9c3; /* bg-yellow-100 */
		color: #a16207;           /* text-yellow-700 (为了对比度使用深黄色/琥珀色) */
		border: 2px solid #facc15; /* border-yellow-400 */
		font-weight: bold;
	}
</style>
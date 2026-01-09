<script>
	import { candidates } from '@sudoku/stores/candidates';
	import { userGrid } from '@sudoku/stores/grid';
	import { cursor } from '@sudoku/stores/cursor';
	import { hints } from '@sudoku/stores/hints';
	import { notes } from '@sudoku/stores/notes';
	import { settings } from '@sudoku/stores/settings';
	import { difficulty } from '@sudoku/stores/difficulty'; // 1. 引入难度 store
	import { keyboardDisabled, setKeyboardHints, isHintActive } from '@sudoku/stores/keyboard';
	import { gamePaused } from '@sudoku/stores/game';
	
	// 引入历史和回溯逻辑
	import { undo, redo, historyStatus } from '@sudoku/stores/history';
	import { performBacktrack, historyTree } from '@sudoku/stores/treeHistoryManager';
	
	// 引入策略算法
	import { getCandidateSet, getStrategiesByDifficulty } from '@sudoku/strategies'; // 2. 引入策略映射
	import { SUDOKU_SIZE, BOX_SIZE } from '@sudoku/constants';

	$: canBacktrack = $historyTree.canBacktrack;
	$: canUndo = $historyStatus.canUndo;
	$: canRedo = $historyStatus.canRedo;
	$: hintsAvailable = $hints > 0;
	
	$: isCellEmpty = $userGrid[$cursor.y] && $userGrid[$cursor.y][$cursor.x] === 0;

	// 用于存储生成的提示文本
	let hintText = '';

	// --- 辅助函数：检测隐性唯一数 ---
	function checkHiddenSingle(x, y, currentCandidates, candidatesMap) {
		for (const num of currentCandidates) {
			let uniqueInRow = true;
			let uniqueInCol = true;
			let uniqueInBox = true;

			// 1. 检查行
			for (let c = 0; c < SUDOKU_SIZE; c++) {
				if (c !== x && candidatesMap[y][c].includes(num)) {
					uniqueInRow = false;
					break;
				}
			}
			if (uniqueInRow) return 'Hidden Single (Row)';

			// 2. 检查列
			for (let r = 0; r < SUDOKU_SIZE; r++) {
				if (r !== y && candidatesMap[r][x].includes(num)) {
					uniqueInCol = false;
					break;
				}
			}
			if (uniqueInCol) return 'Hidden Single (Col)';

			// 3. 检查宫
			const startRow = Math.floor(y / BOX_SIZE) * BOX_SIZE;
			const startCol = Math.floor(x / BOX_SIZE) * BOX_SIZE;
			for (let r = startRow; r < startRow + BOX_SIZE; r++) {
				for (let c = startCol; c < startCol + BOX_SIZE; c++) {
					if ((r !== y || c !== x) && candidatesMap[r][c].includes(num)) {
						uniqueInBox = false;
						break;
					}
				}
			}
			if (uniqueInBox) return 'Hidden Single (Box)';
		}
		return null;
	}

	// --- 辅助函数：比较两个候选数数组是否相等 ---
	function areCandidatesEqual(arr1, arr2) {
		if (arr1.length !== arr2.length) return false;
		return arr1.every(v => arr2.includes(v));
	}

	/**
	 * 智能提示处理函数
	 */
	function handleSmartHint() {
		if (!hintsAvailable || !isCellEmpty || $gamePaused) return;

		const cx = $cursor.x;
		const cy = $cursor.y;

		// 1. 消耗提示
		hints.useHint();

		// 2. 获取当前难度允许使用的策略
		// Very Easy: ['HiddenSingle', 'NakedPair', 'HiddenPair']
		// Hard: []
		const allowedStrategies = getStrategiesByDifficulty($difficulty);

		// 3. 渐进式策略检测
		
		// Level 0: 基础排除 (Naked Single) - 这是所有难度的基础，永远执行
		const candidatesBaseMap = getCandidateSet($userGrid, []); 
		const candidatesBase = candidatesBaseMap[cy][cx];
		
		let strategyName = '';
		let finalCandidates = candidatesBase;

		if (candidatesBase.length === 1) {
			strategyName = 'Naked Single';
		} else {
			// Level 1: 手动检测隐性唯一 (Hidden Single)
			// 【关键修改】：只有当难度允许 'HiddenSingle' 时才检测
			if (allowedStrategies.includes('HiddenSingle')) {
				const hiddenType = checkHiddenSingle(cx, cy, candidatesBase, candidatesBaseMap);
				if (hiddenType) {
					strategyName = hiddenType;
				}
			}

			// 如果还没找到策略名（或者找到了HiddenSingle但也想继续优化候选数），继续尝试削减候选数
			// 注意：HiddenSingle 是一种逻辑判断，不直接改变 candidatesBase 的数组内容（除非填入）。
			// 而 NakedPair/HiddenPair 会直接减少候选数。

			// Level 2: 尝试显性数对 (Naked Pair)
			// 【关键修改】：只有当难度允许 'NakedPair' 且前面没定死策略时检测
			if (!strategyName && allowedStrategies.includes('NakedPair')) {
				const candidatesMediumMap = getCandidateSet($userGrid, ['NakedPair']);
				const candidatesMedium = candidatesMediumMap[cy][cx];

				if (!areCandidatesEqual(candidatesBase, candidatesMedium)) {
					strategyName = 'Naked Pair';
					finalCandidates = candidatesMedium;
				}
			}

			// Level 3: 尝试隐性数对 (Hidden Pair)
			// 【关键修改】：只有当难度允许 'HiddenPair' 时检测
			// 注意：我们需要基于 Level 2 的结果继续算，或者直接算全量。
			// 这里直接算全量 ['NakedPair', 'HiddenPair']，因为 HiddenPair 往往依赖 NakedPair 清理后的盘面
			if (!strategyName && allowedStrategies.includes('HiddenPair')) {
				// 获取一个使用了所有允许策略的集合
				const candidatesHardMap = getCandidateSet($userGrid, ['NakedPair', 'HiddenPair']);
				const candidatesHard = candidatesHardMap[cy][cx];
				
				// 比较它与基础候选数（或Medium候选数）的区别
				// 如果比当前最“优”的候选数还少，说明 HiddenPair 发挥了作用
				if (!areCandidatesEqual(finalCandidates, candidatesHard)) {
					strategyName = 'Hidden Pair';
					finalCandidates = candidatesHard;
				}
			}
		}

		// 4. 生成显示文本
		if (strategyName) {
			hintText = `Possible Number${finalCandidates.length>1?'s':''} → ${strategyName}`;
		} else {
			// Hard 难度下，因为策略列表为空，大概率会落到这里
			hintText = `Possible Numbers`;
		}

		// 5. 获取该格子在当前回溯节点中已经尝试过的数字 (用于标黄)
		const triedNumbers = historyTree.getTriedForCell(cx, cy);

		// 6. 设置键盘高亮
		setKeyboardHints(finalCandidates, triedNumbers);
	}

	function handleBacktrack() {
		const success = performBacktrack();
		
		if (success) {
			const currentNode = historyTree.getCurrentNodeInfo();
			if (currentNode && currentNode.infos) {
				const { candidates, tried } = currentNode.infos;
				
				// 回溯时显示提示文本
				hintText = "Backtracked → Decision Point";
				
				setKeyboardHints(candidates, tried);
			}
		}
	}
</script>

<div class="flex flex-col w-full">
	
	<!-- 提示文本区域：只在提示激活时显示 -->
	<div class="h-6 mb-2 w-full text-center">
		{#if $isHintActive && hintText}
			<span class="text-sm font-semibold text-gray-500 tracking-wide fade-in">
				{hintText}
			</span>
		{/if}
	</div>

	<div class="action-buttons space-x-3">

		<!-- 智能回溯按钮 -->
		<button class="btn btn-round btn-badge"
				disabled={$gamePaused || !canBacktrack}
				on:click={handleBacktrack}
				title="Smart Backtrack (Return to last guess)">
			
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

		<!-- Undo -->
		<button class="btn btn-round" disabled={$gamePaused || !canUndo} on:click={undo} title="Undo">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
			</svg>
		</button>

		<!-- Redo -->
		<button class="btn btn-round" disabled={$gamePaused || !canRedo} on:click={redo} title="Redo">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10h-10a8 8 90 00-8 8v2M21 10l-6 6m6-6l-6-6" />
			</svg>
		</button>

		<!-- 智能提示按钮 -->
		<button class="btn btn-round btn-badge" 
				class:ring-4={$isHintActive} class:ring-yellow-300={$isHintActive}
				disabled={$keyboardDisabled || !hintsAvailable || !isCellEmpty} 
				on:click={handleSmartHint} 
				title="Intelligent Hint ({$hints})">
			
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
			</svg>

			{#if $settings.hintsLimited}
				<span class="badge" class:badge-primary={hintsAvailable}>{$hints}</span>
			{/if}
		</button>

		<!-- 笔记按钮 -->
		<button class="btn btn-round btn-badge" on:click={notes.toggle} title="Notes ({$notes ? 'ON' : 'OFF'})">
			<svg class="icon-outline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
			</svg>
			<span class="badge tracking-tighter" class:badge-primary={$notes}>{$notes ? 'ON' : 'OFF'}</span>
		</button>

	</div>
</div>

<style>
	.action-buttons {
		@apply flex flex-wrap justify-evenly self-end;
	}

	.btn-badge {
		@apply relative;
	}

	.badge {
		min-height: 20px;
		min-width:  20px;
		@apply p-1 rounded-full leading-none text-center text-xs text-white bg-gray-600 inline-block absolute top-0 left-0;
	}

	.badge-primary {
		@apply bg-primary;
	}
	
	.fade-in {
		animation: fadeIn 0.3s ease-in-out;
	}
	
	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(5px); }
		to { opacity: 1; transform: translateY(0); }
	}
</style>
<!-- src/components/HistoryControls.svelte -->
<script>
  import { history, performUndo, performRedo, performBacktrack } from '@sudoku/history/actionHelpers';
  // 订阅组员写的 history store 来获取按钮的禁用/启用状态
  $: stats = $history; 
</script>

<div class="flex justify-center items-center space-x-4 my-6">
  <!-- 撤销 -->
  <button 
    class="btn btn-small flex items-center" 
    disabled={!stats.canUndo} 
    on:click={performUndo}
  >
    <span class="mr-1">↺</span> 撤销
  </button>

  <!-- 回溯 (组员做的特色功能) -->
  <button 
    class="btn btn-small bg-yellow-100 border-yellow-400 text-yellow-800 flex flex-col items-center" 
    disabled={!stats.canBacktrack} 
    on:click={performBacktrack}
  >
    <div class="flex items-center">
      <span class="mr-1">🔙</span> 自动回溯
    </div>
    {#if stats.canBacktrack && stats.backtrackInfo.available}
      <span class="text-[10px] opacity-70">
        剩 {stats.backtrackInfo.remainingCandidates} 个选项
      </span>
    {/if}
  </button>

  <!-- 重做 -->
  <button 
    class="btn btn-small flex items-center" 
    disabled={!stats.canRedo} 
    on:click={performRedo}
  >
    重做 <span class="ml-1">↻</span>
  </button>
</div>

<style>
  /* 可以在这里微调样式 */
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
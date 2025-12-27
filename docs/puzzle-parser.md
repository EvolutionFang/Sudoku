# PuzzleParser 对象（类）定义说明

## 1. 对象名称
- `PuzzleParser`

## 2. 对接方
- Member D：用于“导入题目/粘贴分享内容”的输入处理（UI 层调用 `parse`）。
- Member B：将 `parse` 的结果写入棋盘 Store（数据层使用返回的 grid）。

## 3. 简要描述
`PuzzleParser` 是一个输入解析器，用于把“用户提供的题目字符串”统一转换为标准 9x9 棋盘数据结构。

当前支持两种输入格式（按优先级顺序匹配）：
1. SudokuWiki URL：形如 `https://www.sudokuwiki.org/sudoku.htm?bd=...`（通过 `validateURL` 判断，使用 `decodeURL` 解析）。
2. 自定义 Sencode 字符串：通过 `validateSencode` 判断，使用 `decodeSencode` 解析。

若两者都不匹配，则抛出异常。

## 4. 调用方式
JavaScript

```js
import PuzzleParser from '@sudoku/sencode/puzzleParser';

const grid = PuzzleParser.parse(input);
```

> 说明：`PuzzleParser` 通过 `export default` 导出，按默认导入使用。

## 5. 接口：`PuzzleParser.parse(input)`

### 5.1 输入参数
#### a. input
- 来源：用户粘贴/输入的题目内容（URL 或 Sencode）
- 数据类型：`String`
- 是否必填：Required
- 说明：
  - 若 `validateURL(input) === true`，则当作 SudokuWiki URL 解析。
  - 否则若 `validateSencode(input) === true`，则当作 Sencode 解析。
  - 两者都不是则判为非法输入。

### 5.2 返回值
- 数据类型：`Array<Array<Number>>`（9x9 二维数组）
- 含义说明：
  - `grid[row][col]` 为该格数字
  - `0` 表示空格
  - `1-9` 表示已填数字

### 5.3 异常/错误
- `Error('Invalid custom Sudoku puzzle')`
  - 触发条件：`validateURL(input)` 与 `validateSencode(input)` 均返回 `false`
- 由底层解析函数抛出的异常也会向上透传（例如 URL 内容不合法导致的解析错误）。

### 5.4 规则与优先级
- 优先级：URL 优先于 Sencode。
- 这意味着：如果某个字符串同时“看起来像 URL 且也能通过 Sencode 校验”（理论上很少见），最终会按 URL 处理。

## 6. 使用示例

### 6.1 解析 SudokuWiki URL
```js
const url = 'https://www.sudokuwiki.org/sudoku.htm?bd=...';
const grid = PuzzleParser.parse(url);
// grid 是 9x9 的数字二维数组
```

### 6.2 解析 Sencode
```js
const sencode = '...';
const grid = PuzzleParser.parse(sencode);
```

## 7. 无副作用说明
- `PuzzleParser.parse` 为纯解析逻辑：不读写全局状态、不修改 Store。
- Store 写入应由调用方（通常是 Member B 的 Store 层）完成。

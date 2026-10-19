// 已拆分，见 js/main.js
// 原 app.js 的单文件逻辑已重构为多个职责单一的 ES Module：
//   js/main.js    入口 / 模块装配
//   js/state.js   共享可变状态与常量
//   js/util.js    通用纯函数
//   js/api.js     API 基址 / fetch 封装 / 配置加载
//   js/render.js  渲染与 UI
//   js/stream.js  SSE / 增量解析 / 答题流程
//   js/preload.js 预载编排 / 选项提交 / restart
//   js/session.js 断点续测
// index.html 已改为通过 <script type="module" src="js/main.js"></script> 加载，
// 本文件不再被引用，保留仅作说明。

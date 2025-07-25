/* 主入口文件 - 初始化所有功能模块 */

// 页面加载完成后初始化所有功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化表单验证
    initUploadFormValidation();
    initQuizFormValidation();
    initLoginFormValidation();
    
    // 初始化UI交互功能
    initUIInteractions();
});
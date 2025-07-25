/* 表单验证功能 */

// 文件上传表单验证
function initUploadFormValidation() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            const fileInput = document.querySelector('input[type=file]');
            if (!fileInput.files.length) {
                event.preventDefault();
                alert('请选择一个文件！');
                return false;
            }
            
            const file = fileInput.files[0];
            const fileName = file.name.toLowerCase();
            const validExtensions = ['.ppt', '.pptx', '.pdf', '.txt'];
            let isValid = false;
            
            for (let ext of validExtensions) {
                if (fileName.endsWith(ext)) {
                    isValid = true;
                    break;
                }
            }
            
            if (!isValid) {
                event.preventDefault();
                alert('不支持的文件格式！请上传 .txt, .pdf, .ppt 或 .pptx 文件。');
                return false;
            }
            
            // 文件大小验证（16MB限制）
            const maxSize = 16 * 1024 * 1024; // 16MB
            if (file.size > maxSize) {
                event.preventDefault();
                alert('文件大小超过限制！最大允许16MB。');
                return false;
            }
        });
    }
}

// 测验表单验证
function initQuizFormValidation() {
    const quizForm = document.getElementById('quizForm');
    if (quizForm) {
        quizForm.addEventListener('submit', function(event) {
            // 检查是否至少回答了一个问题
            const radioButtons = document.querySelectorAll('input[type="radio"]:checked');
            if (radioButtons.length === 0) {
                if (!confirm('您还没有回答任何问题，确定要提交吗？')) {
                    event.preventDefault();
                    return false;
                }
            }
        });
    }
}

// 登录表单验证
function initLoginFormValidation() {
    const loginForm = document.querySelector('.login-container form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            
            if (!username || !password) {
                event.preventDefault();
                alert('用户名和密码不能为空！');
                return false;
            }
        });
    }
}
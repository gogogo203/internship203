/* UI交互功能 */

// 选项高亮显示
function highlightOption(element) {
    // 移除同组中其他选项的高亮
    const name = element.getAttribute('name');
    const options = document.querySelectorAll(`input[name="${name}"]`);
    
    options.forEach(option => {
        const label = option.closest('.option-label');
        if (label) {
            label.classList.remove('selected');
        }
    });
    
    // 为当前选中的选项添加高亮
    const currentLabel = element.closest('.option-label');
    if (currentLabel) {
        currentLabel.classList.add('selected');
    }
}

// 自动隐藏通知消息
function initAlertAutoHide() {
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s';
                setTimeout(function() {
                    alert.style.display = 'none';
                }, 500);
            });
        }, 3000);
    }
}

// 初始化所有UI交互功能
function initUIInteractions() {
    initAlertAutoHide();
    
    // 为所有单选按钮添加高亮功能
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            highlightOption(this);
        });
    });
}
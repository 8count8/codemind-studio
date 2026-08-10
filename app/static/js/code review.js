document.addEventListener('DOMContentLoaded', function () {
    // 初始化 Tab 组件（可移除，依赖 Bootstrap 默认行为）
    const triggerTabList = [].slice.call(document.querySelectorAll('#functionTabs a'));
    triggerTabList.forEach(function (triggerEl) {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', function (event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });

    // 新增互斥逻辑处理函数
    function setupInputMutex(fileInputId, textareaId) {
        const fileInput = document.getElementById(fileInputId);
        const textarea = document.getElementById(textareaId);

        // 检查 fileInput 和 textarea 是否存在
        if (!fileInput || !textarea) {
            console.error('未找到对应的文件输入框或文本输入框');
            return;
        }

        function toggleDisabled() {
            const fileHasValue = fileInput.files.length > 0;
            const textHasValue = textarea.value.trim() !== '';
            
            textarea.classList.toggle('input-mutex-disabled', fileHasValue);
            fileInput.classList.toggle('input-mutex-disabled', textHasValue);
        }

        fileInput.addEventListener('change', toggleDisabled);
        textarea.addEventListener('input', toggleDisabled);
    }

    // 初始化所有标签页的互斥逻辑
    const tabs = ['code-commenting', 'code-documentation', 'missing-comment', 'code-conformance'];
    tabs.forEach(tabId => {
        const tab = document.getElementById(tabId);
        if (tab) {
            const fileInput = tab.querySelector('input[type="file"]');
            const textarea = tab.querySelector('textarea');
            if (fileInput && textarea) {
                setupInputMutex(fileInput.id, textarea.id);
            } else {
                console.error(`在 ${tabId} 标签页中未找到文件输入框或文本输入框`);
            }
        }
    });

    // 修改表单提交验证
    document.getElementById('main-form').addEventListener('submit', function(e) {
        const activeTab = document.querySelector('.tab-pane.active');
        const hasFile = activeTab.querySelector('input[type="file"]').files.length > 0;
        const hasText = activeTab.querySelector('textarea').value.trim() !== '';
        
        if (!hasFile && !hasText) {
            alert('请选择文件或输入代码！');
            e.preventDefault();
        }
    });


    // 向默认 Tab 插入内容
    // const defaultTabContent = document.getElementById("code-commenting");
    // defaultTabContent.innerHTML = createFormData([code_file, docs_file, zip_file, code_paste_textarea, submit_button]);
    // 监听 Tab 事件
    addEventListener('show.bs.tab', function (event) {
        // 获取当前激活的 Tab 的 ID 和目标内容区域选择器
        const activeTabId = event.target.getAttribute('id');
        const targetSelector = event.target.getAttribute('aria-controls');
        const tabContent = document.getElementById(targetSelector);


        // 根据 Tab ID 生成对应的内容
        let data = '';
        if (activeTabId === 'code-commenting-tab') {
            data = createFormData([code_file, docs_file, zip_file, code_paste_textarea, submit_button]);
        } else if (activeTabId === 'code-documentation-tab') {
            data = createFormData([code_file, docs_file, zip_file, code_paste_textarea, submit_button]);
        } else if (activeTabId === 'missing-comment-tab') {
            data = createFormData([code_file, docs_file, zip_file, code_paste_textarea, submit_button]);
        } else if (activeTabId === 'code-conformance-tab') {
            data = createFormData([code_file, docs_file, zip_file, code_paste_textarea, submit_button]);
        }

        // 将内容插入到目标区域
        tabContent.innerHTML = data;
    });

    // 处理提交事件
    // 修改表单提交处理逻辑
    document.getElementById('main-form').addEventListener('submit', function (event) {
        event.preventDefault();
        alert('提交成功！');
        const form = this;
        const formData = new FormData(form);
        const activeTabId = document.querySelector('.nav-link.active').id;
    
        // 立即渲染用户代码
        renderUserCode();
        
        // 隐藏表单容器
        document.getElementById('Submit-code-form').style.display = 'none';
        // 显示双结果容器
        document.getElementById('Submit-code-display').style.display = 'block';
    
        // 检查 Result-display 元素是否存在
        const resultDisplayElement = document.getElementById('Result-display');
        if (resultDisplayElement) {
            resultDisplayElement.style.display = 'block';
        } else {
            console.error('未找到 id 为 Result-display 的元素');
        }
    
        // 发送请求...
        fetch(form.action, {
            method: form.method,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 200) {
                setResultDisplay(data.results);
            } else {
                alert(data.message || '提交失败，请重试');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // 修改结果展示函数
    function setResultDisplay(results) {
        const resultDisplay = document.getElementById('result-container');
        // 清空之前的结果
        resultDisplay.innerHTML = '';
        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            const functionName = document.createElement('h4');
            functionName.textContent = result.function;
            const resultText = document.createElement('pre');
            resultText.textContent = result.result;
            resultItem.appendChild(functionName);
            resultItem.appendChild(resultText);
            resultDisplay.appendChild(resultItem);
        });
    }
    
    // 更新用户代码渲染函数
    function renderUserCode() {
        const codeFileInput = document.querySelector('.tab-pane.active input[type="file"]');
        const codeTextarea = document.querySelector('.tab-pane.active textarea');
        const codeDisplay = document.getElementById('Submit-code-display-text');
    
        if (codeFileInput?.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                codeDisplay.textContent = e.target.result;
            };
            reader.readAsText(codeFileInput.files[0]);
        } else if (codeTextarea?.value) {
            codeDisplay.textContent = codeTextarea.value;
        }
    }

    // 读取用户提交的文档渲染到页面
    function renderUserDocs() {

    }

});

// 在现有的setupInputMutex函数后添加
function initTabSpecificValidation() {
    document.querySelectorAll('.tab-pane').forEach(tab => {
        const form = tab.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                // 各Tab独立的验证逻辑
                const tabId = tab.id;
                let isValid = true;
                
                switch(tabId) {
                    case 'code-commenting':
                        isValid = validateCommentTab(tab);
                        break;
                    case 'code-documentation':
                        isValid = validateDocTab(tab);
                        break;
                    case 'missing-comment':
                        isValid = validateMissingTab(tab);
                        break;
                    case 'code-conformance':
                        isValid = validateStandardTab(tab);
                        break;
                }
                
                if (!isValid) e.preventDefault();
            });
        }
    });
}

function validateCommentTab(tab) {
    const fileInput = tab.querySelector('input[type="file"]');
    const textarea = tab.querySelector('textarea');
    return fileInput.files.length > 0 || textarea.value.trim() !== '';
}

function validateDocTab(tab) {
    const codeFile = tab.querySelector('#code-file-doc');
    const docFile = tab.querySelector('#doc-file-doc');
    if (!codeFile.files.length && !docFile.files.length) {
        alert('请至少选择一个代码文件或文档文件');
        return false;
    }
    return true;
}

// 在DOMContentLoaded事件中初始化
document.addEventListener('DOMContentLoaded', function() {
    initTabSpecificValidation();
});

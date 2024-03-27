
$(document).ready(function () {
    // 在頁面加載時，檢查是否有保存的選擇，並設置下拉菜單按鈕的文本
    var savedOption = localStorage.getItem('selectedOption');
    if (savedOption) {
        $('.custom-dropdown-toggle').html($('.custom-dropdown-item[data-value="' + savedOption + '"]').text());
    }

    // 當下拉菜單項目被選擇時
    $('.custom-dropdown-item').on('click', function () {
        // 獲取選擇的項目的文本和數據值
        var selectedText = $(this).text();
        var selectedValue = $(this).data('value');

        // 設置下拉菜單按鈕的文本
        $('.custom-dropdown-toggle').html(selectedText);

        // 將選擇的值保存在本地存儲中，以在頁面刷新後保持選擇狀態
        localStorage.setItem('selectedOption', selectedValue);
    });
});
document.addEventListener('DOMContentLoaded', function () {
    var buttons = document.querySelectorAll('.custom-button');
    var barcodeImage = document.getElementById('barcodeImage');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            var barcodeImg = this.getAttribute('data-barcode-img');
            barcodeImage.src = barcodeImg;
        });
    });
});



// function displaySrcText() {
//     var imageUrl = document.getElementById('barcodeImage').src;
//     var resultDisplay = document.getElementById('resultDisplay');
//     resultDisplay.innerHTML = "Image Source Text: " + imageUrl;
//     xhr.send(JSON.stringify({ imageUrl: imageUrl }));

// }

function displaySrcText() {
    var defaultImageUrl = "http://127.0.0.1:8000/static/img/barcode/barcode.png";
    var imageUrl = document.getElementById('barcodeImage').src;
    var resultDisplay = document.getElementById('resultDisplay');
    if (imageUrl === defaultImageUrl) {
        resultDisplay.innerHTML = "還未選取條碼";
    } else {
        resultDisplay.innerHTML = "已掃描（使用）";
    }

    // 发起 AJAX 请求
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/barcode/", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    // 将图像 URL 作为 JSON 数据发送
    xhr.send(JSON.stringify({ imageUrl: imageUrl }));

    // 处理响应
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                // 解析 JSON 响应
                var response = JSON.parse(xhr.responseText);
            } else {
                console.error("Error:", xhr.status);
            }
        }
    };
}

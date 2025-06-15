// app/static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    // Toast 通知逻辑
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function (toastEl) {
        var toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        return toast;
    });

    // 导航栏滚动效果
    var nav = document.getElementById('main-nav');
    if (nav) {
        // 初始加载时检查一次
        if (window.scrollY > 50 || document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
            nav.classList.add('scrolled');
        }
        // 监听滚动事件
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50 || document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        });
    }
});